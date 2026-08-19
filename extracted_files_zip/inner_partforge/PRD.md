# PRD.md — Product Requirements Document

**Project:** PartForge — AI-Powered Product Intelligence Pipeline for Industrial Commerce
**Hackathon:** UniHack 2026 · Unilog × Hack2Skill
**Track:** AI-Powered Product Intelligence for Industrial Commerce
**Document owner:** Team PartForge
**Status:** Hackathon Build v1.0

---

## 1. Executive Summary

Unilog turns fragmented distributor data — a part number, a cryptic six-word description, and a brand field that is usually a placeholder — into the structured, search-ready product content that lets an industrial buyer find the right part online. Today that transformation is manual, slow, and hard to scale across catalogs with hundreds of thousands of SKUs.

**PartForge** is an AI-powered enrichment pipeline that takes a raw catalog row and produces a complete **Unified Product Intelligence Record (UPIR)**: a canonical classification, a validated attribute set, five differently-formatted descriptions (invoice, mobile, title, long, marketing), and a traceable confidence score — every value either matched to an approved controlled vocabulary or flagged for human review.

Rather than attempting a shallow pass across all eight pipeline stages, PartForge goes **deep on three high-leverage stages** — Taxonomy & Classification, Attribute Extraction, and Cleansing/Normalization/Description Building — for two categories that are specified end-to-end in the reference data (**Kitchen & Bath Sink Faucets** and **Pipe/Tube/Hose Fittings**), while running a lighter-weight version of Ingestion, De-duplication, and a scoped Manufacturer-Source Enrichment across the full 1,000-item working set. Every output is measured against Unilog's own labelled ground truth: the 200-item Input-vs-Delivery-Format file.

This document defines what we are building, for whom, and how we will know it works.

---

## 2. Problem Statement

### 2.1 The business problem
A distributor hands Unilog a spreadsheet row that looks like:

```
Mfg_Part_Num: PDSH4816AF
Part_Desc:    PDSH4816AF Dishwasher SS - Display Only
E1_Brand:     -- Unbranded --
Part_Manuf:   FRIGIDAIRE
```

Unilog must turn this into a commerce-ready record with a fixed classpath, a canonical brand (`FRIGIDAIRE®`), a set of normalized attributes (Series, Mounting, Wash Cycles, Sound Level…), and **five separately-formatted descriptions**, each written to its own character limit and casing rule — an invoice line, a mobile snippet, a search-page title, a long description, and marketing copy. This is repeated across catalogs with hundreds of thousands of rows, most of which arrive with:

- Cryptic, abbreviated descriptions (`3/8 CPLG BRS 150#`)
- The same manufacturer spelled six different ways
- Units written five different ways (`inches`, `IN.`, `in`, `"`, `inch`)
- Empty or placeholder-filled brand fields (`-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`)

### 2.2 Why it's hard
The output is **constrained, not creative**. A fluent, well-written description built from invented attribute values is a *failure*, not a success — every value must trace back to an approved manufacturer/brand list (27,000+ rows), a controlled attribute vocabulary (~161,000 LOV rows), an approved UOM abbreviation (~500 entries across 89 measurement types), or a verifiable manufacturer source. This makes the problem a **grounding and validation problem** as much as a generation problem.

### 2.3 Why it matters
Every hour spent manually classifying and describing a row is an hour not spent on catalog coverage. A distributor with a partial or wrong-brand listing loses searchability, and a buyer who can't find a part by its fraction size (`1/2 in`) because the source only published a decimal (`0.5 in`) doesn't convert. Automating this pipeline — with defensible accuracy and clear "needs review" signals where automation shouldn't guess — is directly a revenue and catalog-coverage lever for Unilog and its distributor customers.

---

## 3. Goals & Non-Goals

### 3.1 Goals (this hackathon build)
| # | Goal |
|---|---|
| G1 | Demonstrate a working, end-to-end enrichment pipeline for **two fully-specified categories** (Faucets, Fittings), measured field-by-field against ground truth. |
| G2 | Demonstrate that every generated value is either (a) matched to a controlled vocabulary/master list, (b) traceable to a manufacturer source, or (c) explicitly flagged as unverified — never silently invented. |
| G3 | Demonstrate normalization correctness (UOM, fraction/decimal, manufacturer/brand canonicalization) at high, auditable accuracy — these are deterministic and should not be left to chance. |
| G4 | Demonstrate scale-readiness by running classification + normalization + description generation across the full 1,000-item sample, with honest reporting of coverage and confidence, not just the easy 200. |
| G5 | Present a credible, judge-facing evaluation harness with reproducible metrics against the 200-item ground truth. |

### 3.2 Non-Goals (explicitly out of scope for this build)
- Full digital-asset sourcing/tagging pipeline (image retrieval, background removal, alt-text) — documented as a future phase, not built.
- Coverage of all product categories in the 161,000-row LOV — we intentionally go deep on two categories rather than shallow on all.
- Production-grade authentication, multi-tenant infrastructure, or billing — this is a functional prototype, not a shipped SaaS product.
- Fully autonomous manufacturer-site scraping at catalog scale — we build and demonstrate the *pattern* (allowlisted, sourcing-hierarchy-respecting retrieval) on a bounded sample, not a production crawler.

---

## 4. Users & Personas

| Persona | Who they are | What they need from PartForge |
|---|---|---|
| **Catalog Enrichment Analyst** | Reviews and approves enriched records before publish | A review queue that surfaces only low-confidence/flagged records, with the evidence (source, LOV match, rule applied) attached to every field |
| **Data Quality Lead** | Owns accuracy SLAs across the catalog | Field-level accuracy dashboards, LOV-compliance %, and drill-down into failure modes |
| **Catalog Operations Manager** | Plans throughput across large item batches | Batch processing view, coverage %, and cost/latency per 1,000 items |
| **Distributor Buyer** (end beneficiary, not a direct user of the tool) | Searches for a part online | Accurate titles, correct fraction sizing, and consistent brand/attribute filtering that surfaces the right SKU |

---

## 5. Scope

### 5.1 Pipeline stages and our depth decision

```
Input Analysis → De-duplication → Taxonomy & Classification → Attribute Extraction →
Enrichment from Manufacturer Sources → Cleansing & Normalization → Description Building → Digital Assets
```

| Stage | Depth in this build | Rationale |
|---|---|---|
| 1. Input Analysis / Ingestion | **Full** — robust parsing of messy spreadsheets (merged cells, multi-row headers, side-by-side blocks, placeholder detection) | Everything downstream depends on this being right; it is also the cheapest stage to get to high accuracy on. |
| 2. De-duplication | **Partial** — fuzzy match on `Mfg_Part_Num` + normalized manufacturer, demonstrated on the 1,000-item set | Valuable, well-scoped, but secondary to correctness of a single record. |
| 3. Taxonomy & Classification | **Full**, for Faucets & Fittings; **best-effort** classpath suggestion for the rest of the 1,000 | These two categories are the only ones specified end-to-end in the reference pack — depth beats breadth. |
| 4. Attribute Extraction | **Full**, for Faucets & Fittings, LOV-constrained | Directly measurable against `FAUCETS_LOV.xlsx` / `Fittings_LOV.xlsx`. |
| 5. Enrichment from Manufacturer Sources | **Scoped demo** — allowlisted retrieval agent shown on a bounded sample, sourcing hierarchy enforced | Full-catalog live retrieval is not a realistic 36-hour build; the *pattern and guardrails* are what we demonstrate. |
| 6. Cleansing & Normalization | **Full**, across the entire 1,000-item set | Deterministic, rule-based, highest-confidence stage — the best return on effort. |
| 7. Description Building | **Full**, for Faucets & Fittings (all 5 formats); rule-templated for the wider set | Directly measurable against the 200-item ground truth. |
| 8. Digital Assets | **Not built** — documented in `Phases.md` as a post-hackathon roadmap item | Out of scope per §3.2. |

### 5.2 In scope
- 200-item ground-truth-driven build and scoring loop
- 1,000-item volume run for classification, normalization, and templated description
- Faucets and Fittings deep-dive, full 5-format description generation
- Confidence scoring and "needs human review" flagging
- Judge-facing evaluation dashboard (see `Evaluation.md`)

### 5.3 Out of scope
- Digital asset generation/sourcing
- Categories outside Faucets/Fittings for full attribute-level depth
- Production authentication, deployment, and multi-tenant concerns

---

## 6. Dataset Overview

| Group | File | Role |
|---|---|---|
| A. Working data | `Sample-1000_Items.xlsx` | Volume test input — 1,000 raw rows, 6 columns |
| A. Working data | `Unilog-Sample_200_Items-Input-vs-Output.xlsx` | **Ground truth** — Input sheet + 252-column Delivery Format sheet |
| B. Rule book | `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx` | Field formulas, character limits, casing, category rules, sourcing rules |
| B. Rule book | `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx` | ~500 approved UOM abbreviations across 89 measurement types + 22 house-style rules |
| B. Rule book | `Decimal_Fraction.xlsx` | 63 exact inch fraction↔decimal conversions |
| C. Master data | `UniCat_Manufacturer_and_Brand_List.xlsx` | 27,000+ canonical manufacturer/brand rows with exact casing, suffixes, symbols |
| C. Master data | `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx` | ~161,000-row cross-category List of Values (classpath → attribute → allowed value) |
| C. Master data | `FAUCETS_LOV.xlsx` | Full category spec: classpath, UNSPSC, description build order, attribute sequence, style guide |
| C. Master data | `Fittings_LOV.xlsx` | Full category spec: 390 fitting types, 1,472 connection-type variants → 515 canonical, 464 material variants → 113 canonical |
| D. Index | `Reference_Documents_Summary.xlsx` | Client-authored map of all reference files |

See `Rules.md` §2 for how each of these is consumed programmatically, and `Architecture.md` §5 for storage design.

---

## 7. Functional Requirements

| ID | Requirement | Acceptance Criteria |
|---|---|---|
| FR-1 | System shall ingest raw catalog rows from `.xlsx` sources, correctly handling merged cells, multi-row headers, and side-by-side column blocks | 100% of sheets in the reference pack parse without silent data loss; a parsing report lists any row/column dropped |
| FR-2 | System shall detect and null out placeholder brand values (`-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`) before any downstream matching | 0% of placeholder strings survive into the canonical record as a real value |
| FR-3 | System shall flag likely duplicate rows using normalized `Mfg_Part_Num` + canonical manufacturer | Duplicate clusters are surfaced with a similarity score; no automatic silent merge without a confidence threshold |
| FR-4 | System shall assign a `Dept > Class > Fine` classpath to each item, for Faucets and Fittings items with ≥ the accuracy defined in `Evaluation.md` | Exact-match accuracy against the 200-item ground truth reported and reproducible |
| FR-5 | System shall extract attribute values constrained to the applicable classpath's LOV entries — never freeform for filterable attributes | % of generated attribute values found in the LOV's Normalized Values reported per category |
| FR-6 | System shall normalize every unit of measure to its single approved abbreviation with correct number-unit spacing | 100% of numeric+unit tokens in output match an entry in the Master UOM sheet |
| FR-7 | System shall convert decimal inch measurements to trade fraction form (and vice versa where the guideline calls for it) using the Decimal_Fraction lookup | 100% match against the 63-entry lookup for in-scope values |
| FR-8 | System shall resolve messy manufacturer/brand strings to the exact canonical form (casing, suffix, ® / ™) from the 27,000-row master list | Exact-string-match rate reported; unresolved names flagged, never guessed |
| FR-9 | System shall generate five description formats (Invoice ≤40 char CAPS, Mobile 60–80 char, Product Title/Short Desc, Long Description, Marketing) following the construction formulas in the Content Guidelines | Character-limit compliance and field-formula compliance reported per format |
| FR-10 | System shall attach a confidence score and, where applicable, a `needs_review` flag with a human-readable reason to every record | Every UPIR record has a non-null confidence score and review reason when flagged |
| FR-11 | System shall restrict manufacturer-source enrichment to manufacturer-owned domains/documentation, explicitly excluding marketplaces and distributor sites | Sourcing agent's allow/deny list is inspectable; any retrieved fact carries its source URL |
| FR-12 | System shall expose a judge-facing dashboard showing field-level accuracy, LOV compliance, character-limit compliance, and coverage across both the 200-item and 1,000-item sets | Dashboard loads with live numbers computed from the evaluation harness, not hardcoded |

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Accuracy over fluency** | A field that is fluent but ungrounded is a defect. Every generation path must have a validation gate (see `Validation.md`). |
| **Explainability** | Every field in a UPIR record must be traceable to one of: input data, a rule (UOM/fraction/brand table), an LOV entry, or a cited manufacturer source. |
| **Determinism where it matters** | Normalization (UOM, fractions, manufacturer/brand canonicalization) is rule-based and deterministic, not LLM-generated, to avoid unnecessary variance on solved problems. |
| **Scalability** | The pipeline must run unmodified on 1,000 items and be architected (batching, async, stateless workers) to extend to catalog-scale without a redesign — see `Architecture.md` §7. |
| **Latency/cost budget** | Target ≤ [X] seconds and ≤ [$Y] per record at hackathon scale; tracked and reported, not assumed. |
| **Auditability** | Every pipeline run persists an `agent_trace` per record so any output can be explained after the fact. |
| **Graceful degradation** | Where a value cannot be confidently resolved (no LOV match, no source, ambiguous classpath), the system emits `null` + a review flag rather than a best-guess string. |

---

## 9. Success Metrics

Primary metrics (full definitions and methodology in `Evaluation.md`):

1. **Classification exact-match accuracy** (Dept/Class/Fine) on Faucets & Fittings, vs. 200-item ground truth
2. **Attribute LOV-compliance rate** — % of extracted attribute values found in the controlled vocabulary
3. **Character-limit compliance rate** across all five description formats
4. **Manufacturer/brand canonicalization exact-match rate** against the 27,000-row master list
5. **UOM & fraction normalization correctness**
6. **Hallucination rate** — % of output fields with no traceable source
7. **Review-flag precision** — of records flagged `needs_review`, what % genuinely had an issue on manual audit
8. **Throughput** — items processed per minute at 1,000-item scale

---

## 10. Assumptions & Constraints

- We assume the 200-item Delivery Format sheet is the authoritative definition of "correct," including its documented imperfections (blank UNSPSC/country-of-origin cells, at least one manufacturer/brand mismatch) — we do not "fix" ground truth, we report against it as-is.
- We assume manufacturer-source enrichment during the hackathon is demonstrated on a bounded, allowlisted sample due to time and network constraints, not run unrestricted across all 1,000 items.
- We assume LLM API access (see `AI_Strategy.md`) is available for the duration of the build; the architecture is provider-agnostic where possible.
- We assume "Unbranded"-style placeholders are the complete list of placeholder strings encountered; the parser is written to be extensible if others appear.

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LLM invents an attribute value not in the LOV | Silent data-quality defect | Constrained generation + post-hoc LOV validator gate (`Validation.md` §3) rejects/flags any non-matching value |
| Manufacturer/brand fuzzy match resolves to the wrong canonical row (e.g., similar names) | Wrong brand on record | Similarity threshold + top-2 margin check; ambiguous matches routed to review, not auto-resolved |
| Time pressure collapses scope from "deep on 2 categories" to "shallow on everything" | Weak, unmeasurable demo | Explicit scope lock in §5.1; 1,000-item run intentionally excludes attribute-level depth outside Faucets/Fittings |
| Manufacturer-source retrieval pulls from a disallowed domain | Sourcing-policy violation | Domain allowlist enforced at the retrieval-tool layer, not just prompted |
| Ground-truth file itself contains known gaps (blank cells, one mismatch) | Evaluation harness misreports these as pipeline errors | Evaluation harness treats known documented gaps as "ground truth is empty" cases, scored separately from genuine misses |

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **UPIR** | Unified Product Intelligence Record — PartForge's canonical internal schema for one enriched item |
| **Classpath** | The `Dept > Class > Fine` taxonomy path assigned to an item |
| **LOV** | List of Values — the controlled vocabulary of allowed attribute values per classpath |
| **MPN** | Manufacturer Part Number |
| **UOM** | Unit of Measure |
| **Sourcing hierarchy** | The rule that manufacturer-owned sites/docs are the only valid enrichment source; marketplaces/distributors are excluded |
| **Needs-review flag** | A record-or-field-level marker indicating automation could not confidently resolve a value |

---

## 13. Appendix — Dataset-to-Requirement Traceability

| Requirement | Primary dataset(s) consumed |
|---|---|
| FR-1, FR-2 | `Sample-1000_Items.xlsx`, `Unilog-Sample_200_Items-Input-vs-Output.xlsx` |
| FR-3 | `Sample-1000_Items.xlsx` |
| FR-4 | `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`, `FAUCETS_LOV.xlsx`, `Fittings_LOV.xlsx` |
| FR-5 | `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`, `FAUCETS_LOV.xlsx`, `Fittings_LOV.xlsx` |
| FR-6 | `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx` |
| FR-7 | `Decimal_Fraction.xlsx` |
| FR-8 | `UniCat_Manufacturer_and_Brand_List.xlsx` |
| FR-9 | `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx`, `FAUCETS_LOV.xlsx` (build order sheet) |
| FR-11 | `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx` (sourcing rules) |
| FR-12 | `Unilog-Sample_200_Items-Input-vs-Output.xlsx` (as ground truth) |

**Related documents:** `Architecture.md` · `Rules.md` · `Design.md` · `Phases.md` · `Evaluation.md` · `AI_Strategy.md` · `Validation.md` · `Demo.md`
