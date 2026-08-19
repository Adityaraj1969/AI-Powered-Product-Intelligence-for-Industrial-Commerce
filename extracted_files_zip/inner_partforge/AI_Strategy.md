# AI_Strategy.md — AI & LLM Strategy

**Project:** PartForge · **Purpose:** define which parts of the pipeline are genuinely AI/LLM problems, which are not, and exactly how we constrain, ground, and validate every generative step. This document is the direct implementation plan for the principle stated in `Architecture.md` §1: *deterministic where the answer is known, generative where it isn't.*

---

## 1. Where AI Is — and Isn't — the Right Tool

A recurring failure mode in enrichment projects is reaching for an LLM everywhere, including places a table lookup would be faster, cheaper, and more accurate. We made this decision explicit and per-stage:

| Pipeline stage | AI/LLM involved? | Why |
|---|---|---|
| Input parsing / placeholder filtering | **No** | Deterministic parsing logic; an LLM adds latency and non-determinism to a solved problem |
| De-duplication | **Light** — fuzzy string similarity (algorithmic, not LLM) | Classic string-matching problem; embeddings can assist edge cases but the core signal is algorithmic |
| Taxonomy & classification | **Yes** — retrieval + LLM | Genuinely open-ended: mapping a 6-word abbreviated string to one of thousands of classpaths requires semantic understanding of trade abbreviations, not just keyword match |
| Attribute extraction | **Yes** — LLM with structured/tool-call output | Same reasoning: `"3/8 CPLG BRS 150#"` requires domain knowledge to decompose into Size=3/8 in, Type=Coupling, Material=Brass, Pressure Class=150# |
| Manufacturer-source enrichment | **Yes** — LLM + retrieval (RAG) | Requires reading unstructured manufacturer documentation and answering a specific attribute question with citation |
| UOM normalization | **No** | Pure table lookup (`Rules.md` §3) |
| Decimal↔fraction conversion | **No** | Pure table lookup (`Rules.md` §4) |
| Manufacturer/brand canonicalization | **Mostly no** — exact match first, fuzzy/embedding match only as fallback | The correct answer is a specific row in a 27K-row table; an LLM "recalling" a brand name from training data is exactly the hallucination risk we must avoid — canonical values must come from retrieval against the actual table, never from the model's parametric memory |
| Description building | **Yes**, but formula-constrained | The *content and order* of each description is decided by the formula engine (`Rules.md` §9), not the LLM; the LLM's job is narrowly fluent phrasing inside that skeleton |
| Confidence scoring / review flagging | **Hybrid** — deterministic thresholds on retrieval scores + LLM self-reported confidence, blended | Neither alone is reliable; retrieval similarity catches "no good match exists," LLM confidence catches "the match exists but the model is unsure which is right" |

---

## 2. Model Selection

| Role | Model class | Rationale |
|---|---|---|
| Classification & extraction reasoning | A frontier chat model with strong structured-output/tool-use support (e.g., Claude, via the Anthropic API) | Needs to reason over abbreviated trade jargon and pick constrained outputs reliably via tool-calling, not just free text |
| Description compositor | Same model family, lower temperature | Prioritizes formula adherence and grounded phrasing over creative variation |
| Embeddings (classpath / LOV / manufacturer retrieval) | A dedicated embedding model (e.g., Voyage AI, since Anthropic's model family is optimized for generation, not embeddings) | Retrieval quality over the 161K-row LOV and 27K-row manufacturer list is the single biggest lever on classification/extraction accuracy — worth a dedicated, well-tuned embedding model rather than reusing a generation model's hidden states |
| Manufacturer-source RAG answering | Same chat model as classification, with a tool-use loop for fetch + cite | Needs to read a fetched document and answer a specific, narrow question with a citation, not summarize broadly |

**Provider-agnostic design:** the architecture (`Architecture.md` §3) treats the LLM as a swappable component behind a single interface (`generate(prompt, tools, schema) → structured_output`), so the model can be substituted without touching pipeline logic — relevant given hackathon API access can be constrained or change.

---

## 3. Prompt & Tool Design

### 3.1 Classification Agent — example tool schema

```json
{
  "name": "assign_classpath",
  "description": "Assign the most likely classpath for this item from the provided candidates only.",
  "input_schema": {
    "type": "object",
    "properties": {
      "selected_classpath": { "type": "string", "enum": ["<populated with retrieved top-k classpaths only>"] },
      "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
      "reasoning": { "type": "string" }
    },
    "required": ["selected_classpath", "confidence", "reasoning"]
  }
}
```

**Design choice:** the `enum` for `selected_classpath` is populated at call time with only the top-k candidates retrieved from the embedding index — the model is architecturally unable to output a classpath that doesn't exist in the LOV, because the schema itself doesn't allow it. This is stronger grounding than a prompt instruction like "only choose from the list below," which a model can still violate.

### 3.2 Attribute Extraction Agent — example tool schema

```json
{
  "name": "extract_attributes",
  "description": "Extract attribute values for this item, constrained to the applicable attribute list.",
  "input_schema": {
    "type": "object",
    "properties": {
      "attributes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "label": { "type": "string", "enum": ["<populated with this classpath's valid attribute labels>"] },
            "value": { "type": "string" },
            "evidence_span": { "type": "string", "description": "The substring of Part_Desc (or source excerpt) that supports this value" }
          },
          "required": ["label", "value", "evidence_span"]
        }
      }
    }
  }
}
```

**Design choice:** `evidence_span` is mandatory, not optional. Requiring the model to point to the exact substring that justifies a value does two things: it materially reduces free-invention (the model has to "show its work"), and it gives the LOV Validator Gate (`Architecture.md` §6) a second signal — a value with no plausible evidence span in the source text is a stronger candidate for rejection even if it happens to be a valid LOV value for a *different* item.

### 3.3 Manufacturer-Source RAG Agent — retrieval discipline

```
retrieve(query, allowed_domains) → chunks[]   # tool-layer enforced allowlist, not prompt-only
answer(question, chunks[]) → { value, citation_chunk_id, confidence }
```

The allowlist enforcement happens in the **retrieval tool itself** (`Rules.md` SRC-3), not as a system-prompt instruction, for a specific reason: prompt-only constraints are a request the model can misweight against other instructions or drift on under context pressure; a tool that structurally cannot return results from a non-allowlisted domain removes the failure mode entirely rather than making it merely less likely.

### 3.4 Description Compositor — formula-first prompting

The prompt for each description format is generated dynamically from the formula skeleton (`Rules.md` §9), not a static template string:

```
System: You write exactly one {format_name} description.
Hard constraints:
- Length: {min_chars}-{max_chars} characters
- Casing: {casing_rule}
- Must include, in this order: {ordered_field_list}
- Use ONLY the values provided below. Do not add attributes, numbers, or claims not present.

Validated fields (already normalized, already LOV-checked):
{field_list_with_values}
```

Because `field_list_with_values` only ever contains values that already passed the LOV Validator Gate, the compositor is structurally prevented from having any *other* content to draw on — there is nothing to hallucinate from, only fewer/more concise ways to phrase what's given.

---

## 4. Retrieval-Augmented Grounding (RAG) Design

| RAG use | Corpus | Chunking strategy | Notes |
|---|---|---|---|
| Classpath retrieval | Classpath + Fine Node text from the LOV, embedded once at load time | One embedding per leaf classpath | Re-embedded only when the LOV changes, not per query |
| Attribute/LOV retrieval | `Attribute Label` + `Normalized Values` + `Guidelines`/`Remarks` per classpath | One chunk per classpath's attribute set | Category override files (Faucets/Fittings) embedded and indexed separately, queried first per Rules.md CL-2 |
| Manufacturer/brand retrieval | 27K-row manufacturer/brand list | One embedding per manufacturer name (normalized) | Used only as a fallback after exact-match fails (Rules.md MB-2) |
| Manufacturer-source enrichment | Fetched HTML/PDF from allowlisted manufacturer domains | Semantic chunking (~300–500 tokens), page/section metadata retained for citation | Only fetched pages, never a general web index — no fetch, no chunk |

---

## 5. Hallucination Mitigation — the Full Chain

This is the single most judge-relevant section, because it's the direct answer to the brief's warning. Hallucination is mitigated at **four independent layers**, not one:

1. **Schema-level constraint** (§3.1, §3.2): the model cannot even *express* an invalid classpath or non-applicable attribute label, because the schema's enum doesn't include it.
2. **Evidence requirement** (§3.2): every extracted attribute must cite the source substring that justifies it.
3. **Post-generation validator gate** (`Architecture.md` §6): every value is re-checked against the LOV/master table after generation, independent of what the model claimed about its own output.
4. **Tool-layer source enforcement** (§3.3): retrieval simply cannot return non-allowlisted content, so there is no disallowed source to accidentally cite.

No single layer is trusted alone — this is intentional defense-in-depth, because prompting alone is well understood to be an incomplete mitigation.

---

## 6. Cost & Latency Budget

| Stage | Calls per record | Notes |
|---|---|---|
| Classification | 1 LLM call + 1 embedding query | Embedding query is cheap/fast; LLM call is the main cost |
| Attribute extraction | 1 LLM call (batched across all applicable attributes per item) | Batching attributes into one structured call, rather than one call per attribute, is a deliberate cost control |
| Manufacturer-source enrichment | 1–3 calls (fetch + answer), only for records with unresolved required attributes after extraction | Scoped to the bounded demo sample this build; see `Phases.md` contingency plan |
| Description building | Up to 5 calls (one per format), or 1 batched call producing all 5 in a single structured response, traded off against per-format regeneration-on-failure needs | Batched-by-default, with per-format regeneration only on a validator failure |
| Normalization | 0 LLM calls | Entirely deterministic |

Tracked live per run and surfaced on the Metrics Dashboard (`Design.md` §4.6, `Evaluation.md` §3.6) as cost-per-record — a number we present honestly, including where it's high, rather than omitting it.

---

## 7. Human-in-the-Loop Triggers

The AI layer is explicitly designed to **stop and ask**, not guess, when:

- Classification confidence falls below threshold (`Rules.md` CL-3)
- A manufacturer/brand fuzzy match lacks a clear margin over the runner-up (`Rules.md` MB-3)
- An attribute value fails the LOV Validator Gate with no close coercion candidate
- A description fails character-limit/casing validation twice in a row
- Manufacturer-source enrichment finds no allowlisted source for a required attribute

Each trigger writes a specific, human-readable `review_reason` (not a generic "low confidence") so the Review Queue (`Design.md` §4.5) is genuinely actionable rather than a black-box backlog.

---

**Related documents:** `PRD.md` · `Architecture.md` · `Rules.md` · `Validation.md` · `Evaluation.md`
