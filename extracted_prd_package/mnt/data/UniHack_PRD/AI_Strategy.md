# UniHack — AI Strategy

## 1. AI Thesis

The system should use AI where the task is ambiguous and language-heavy, and deterministic software where the answer can be decided from reference data or explicit rules.

### Core principle

> **RAG supplies evidence. Structured extraction supplies facts. Rules supply constraints. The LLM supplies interpretation and language. Validation supplies the final gate.**

This directly matches the challenge's openness to AI agents, RAG, knowledge graphs, document intelligence, vision-language models, and human-in-the-loop workflows. citeturn154558view1

---

## 2. AI Workloads

| Workload | Best mechanism |
|---|---|
| Manufacturer matching | deterministic + fuzzy + embeddings |
| Brand matching | master-data join + candidate ranking |
| Taxonomy | classifier + retrieval + evidence scoring |
| Web/doc retrieval | search + domain/source ranking |
| PDF understanding | document intelligence + LLM |
| Attribute extraction | structured LLM output |
| LOV mapping | retrieval + deterministic mapping |
| Conflict resolution | constrained reasoning agent |
| Description generation | template + LLM |
| Validation | deterministic first, semantic second |
| Image understanding | optional VLM |

---

## 3. Why Not One Giant Agent?

A single agent asked to "take this row and fully enrich it" has too many degrees of freedom. It may:

- hallucinate values;
- choose an invalid LOV value;
- mix evidence from different products;
- produce a plausible but non-compliant title;
- lose provenance.

Instead use **small, observable stages**.

---

## 4. Agent Roles

### Agent 1 — Resolver

Input: raw manufacturer/brand/MPN.

Output: candidate canonical entities + confidence.

Tools:

- manufacturer master;
- brand master;
- fuzzy search;
- semantic search.

### Agent 2 — Classifier

Input: raw row + resolved identity + available evidence.

Output: candidate classpath + confidence + reasoning evidence.

Tools:

- taxonomy index;
- category rules;
- evidence store.

### Agent 3 — Researcher

Input: canonical identity + classpath.

Output: ranked manufacturer sources and extracted documents.

Tools:

- web search;
- manufacturer domain filter;
- PDF/document parser.

### Agent 4 — Extractor

Input: evidence.

Output: structured claims.

Tools:

- schema-constrained LLM;
- regex/number parsing;
- unit recogniser.

### Agent 5 — Normaliser

Input: structured claims.

Output: LOV/UOM-compliant facts.

Tools:

- LOV index;
- UOM table;
- fraction lookup;
- category mappings.

This should be mostly deterministic.

### Agent 6 — Writer

Input: validated fact bundle + content rules.

Output: commerce fields.

### Agent 7 — Auditor

Input: complete record + evidence.

Output: rule failures, unsupported claims, confidence, publish/review decision.

---

## 5. Multi-Agent Orchestration

```text
                 ┌──────────────┐
                 │   Raw Item   │
                 └──────┬───────┘
                        ▼
                ┌───────────────┐
                │   Resolver    │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │   Classifier  │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │   Researcher  │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │   Extractor   │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │  Normaliser   │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │    Writer     │
                └──────┬────────┘
                       ▼
                ┌───────────────┐
                │    Auditor    │
                └──────┬────────┘
                       ▼
                PUBLISH / REVIEW
```

The orchestrator should be deterministic and stateful. Agents should not call each other in an unbounded loop.

---

## 6. RAG Strategy

### Query construction

```text
[canonical manufacturer]
[exact MPN]
[product-type keywords]
[high-value attributes if known]
```

Example:

```text
FRIGIDAIRE PDSH4816AF Professional Series dishwasher specification PDF
```

### Retrieval strategy

Use hybrid retrieval:

- exact MPN search;
- BM25/keyword retrieval;
- embedding retrieval;
- source authority filtering.

Then re-rank results with an LLM or cross-encoder.

---

## 7. Retrieval Guardrails

Reject or down-rank evidence when:

- source domain is outside manufacturer authority;
- MPN is absent and product identity is uncertain;
- document is clearly for a different model;
- page is a marketplace listing where organiser rules exclude it;
- content is contradictory with stronger evidence.

A source should never become "trusted" simply because the LLM finds it useful.

---

## 8. Structured Extraction Prompt Strategy

Use JSON-schema constrained output.

### Extraction contract

```json
{
  "claims": [
    {
      "attribute": "string",
      "raw_value": "string",
      "normalized_candidate": "string|null",
      "unit": "string|null",
      "qualifier": "string|null",
      "evidence_text": "string",
      "source_id": "string",
      "confidence": 0.0
    }
  ]
}
```

Prompt rules:

- extract only explicitly supported claims;
- preserve qualifiers such as `maximum`, `minimum`, `nominal`, or `with door open`;
- do not collapse distinct measurements;
- return null when unsupported.

---

## 9. LOV Retrieval Strategy

The LOV is too large to prompt in full. The system should retrieve a relevant slice:

```text
classpath
   ↓
attribute set
   ↓
candidate values
   ↓
LLM semantic match
   ↓
deterministic canonicalisation
```

For Fittings, use the category-specific mappings for connection types and materials described by the organiser. citeturn154558view1

---

## 10. Knowledge Graph Strategy

A full graph database is optional. A relational evidence graph is enough for the hackathon.

### Minimum schema

```text
products
sources
claims
attributes
lov_values
rules
claim_sources
field_derivations
```

This supports graph-like traversal without infrastructure overhead.

### High-value queries

- Which source supports this title token?
- Which products share this ambiguous manufacturer string?
- Which fields depend on a conflicting claim?
- Which attributes are repeatedly unresolved for this classpath?

---

## 11. Vision-Language Strategy

Use VLM only where the visual asset provides information unavailable in text, such as:

- product packaging labels;
- dimensional diagrams;
- connection diagrams;
- visual finish/colour where permitted by category rules;
- technical drawing interpretation.

### VLM rule

A VLM observation is still a claim and therefore needs confidence and, where applicable, human review.

Do not turn visual similarity into factual specifications without corroborating evidence.

---

## 12. Description Generation Strategy

Use a two-stage writer:

### Stage 1 — content planner

Select facts allowed for the field.

### Stage 2 — renderer

Turn the facts into the required format.

Example:

```text
Fact bundle
  Brand = FRIGIDAIRE®
  Series = Professional Series
  MPN = PDSH4816AF
  Type = Dishwasher
  Wash Cycles = 5
  Material = Stainless Steel

          ↓

Title template
Brand + Series + MPN + Type + key attributes

          ↓

FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With ...
```

This mirrors the organiser's example where the same facts are rendered differently across invoice, mobile, title, and long-description surfaces. citeturn154558view1

---

## 13. Hallucination Defence

Use four gates:

### Gate 1 — Evidence gate

Can this claim be traced to a source?

### Gate 2 — Vocabulary gate

Does the final value exist in an allowed vocabulary?

### Gate 3 — Rule gate

Does the field comply with format/casing/length rules?

### Gate 4 — Consistency gate

Does the claim agree with other product facts?

Only then does the value enter the publishable record.

---

## 14. Model Routing

Use the cheapest reliable mechanism per task.

```text
Simple normalisation  → deterministic code
Exact match            → indexed lookup
Candidate ranking      → small embedding model
Complex extraction     → strong LLM
Long document synthesis→ strong LLM + retrieval
Image understanding   → VLM
Validation             → code + small semantic checker
```

This keeps latency and cost under control and makes the architecture easier to explain.

---

## 15. Prompt Versioning

Every prompt is stored as:

```text
prompt_id
version
purpose
input_schema
output_schema
ruleset_version
model
examples
```

Prompt changes must run through the evaluation suite.

---

## 16. Feedback Loop

Reviewer corrections become:

- new aliases;
- new conflict patterns;
- prompt examples;
- mapping fixes;
- threshold adjustments.

Do not automatically rewrite the ground truth or promote every correction into a global rule.

---

## 17. Recommended AI Demo Story

The best AI moment is not "look, the LLM generated a paragraph." It is:

> **The system finds the manufacturer's document, extracts the connection type, maps 3/8 FNPT to the organiser's canonical value, uses that validated fact to build the product title, and then the validator confirms every derived output.**

That demonstrates reasoning, retrieval, normalisation, domain control, and explainability in one chain.
