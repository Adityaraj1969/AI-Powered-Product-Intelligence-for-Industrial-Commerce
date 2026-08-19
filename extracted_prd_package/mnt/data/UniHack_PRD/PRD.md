# UniHack — AI-Powered Product Intelligence for Industrial Commerce

## Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** Hackathon-ready / implementation baseline  
**Primary objective:** Build a defensible AI enrichment pipeline that turns sparse, messy industrial product rows into validated, standardised, commerce-ready product intelligence with traceable evidence.

---

## 1. Executive Summary

### 1.1 Problem

Industrial product catalogues are assembled from fragmented manufacturer and distributor sources. A single raw row may contain only a manufacturer part number, abbreviated description, inconsistent manufacturer/brand strings, and a small amount of classification data. The downstream commerce record, however, requires a canonical manufacturer and brand, taxonomy, attributes, units, titles, short/mobile copy, long descriptions, digital assets, and validation evidence.

The organiser's solution guide explicitly frames the required pipeline as **input analysis → de-duplication → taxonomy & classification → attribute extraction → enrichment from manufacturer sources → cleansing and normalisation → description building → digital assets**. The challenge is not simply to generate prose; it is to create constrained, trustworthy product intelligence. citeturn154558view1

### 1.2 Product vision

**UniHack Product Intelligence Engine (PIE)** is a hybrid AI + deterministic data-quality system that:

1. profiles and cleans raw catalogue inputs;
2. resolves manufacturer and brand entities against approved master data;
3. classifies products into the most defensible taxonomy path;
4. retrieves manufacturer-authoritative evidence;
5. extracts structured facts into a typed evidence graph;
6. normalises attributes, values, units, fractions, casing, symbols, and terminology;
7. generates channel-specific commerce copy from validated facts;
8. validates every output against field rules and controlled vocabularies;
9. assigns confidence and routes uncertain records to human review;
10. exports a delivery-ready record plus an audit trail.

### 1.3 North-star outcome

> **Maximum validated product coverage per unit of human effort, with no silent hallucinations.**

A successful system should prefer **"unknown / needs review"** over invented product facts, while still automating high-confidence work at catalogue scale.

---

## 2. Hackathon Context

Hack2Skill describes UniHack as a national AI innovation hackathon focused on AI-powered product intelligence, industrial commerce, and generative AI. Publicly listed event information shows registrations closing on **23 August 2026** and the event ending on **4 September 2026**; the public listing also describes judging dimensions including innovation, technical implementation, business relevance, and impact. citeturn154558search1

Unilog positions its product-content platform around the difficulty of finding correct product information and describes AI-powered agents for product-content workflows at industrial-commerce scale. citeturn154558search2

The organiser solution guide is the governing challenge interpretation for this project. It states that:

- `Unilog-Sample_200_Items-Input-vs-Output.xlsx` is the labelled ground truth.
- `Sample-1000_Items.xlsx` is the scale test set.
- content guidelines define construction formulas, character limits, casing, sourcing, and asset rules.
- UOM, manufacturer/brand, and LOV files are constrained vocabularies, not optional suggestions.
- placeholder brand values such as `-- Unbranded --` are empty values.
- manufacturer-originated sources are preferred over marketplaces/distributors.
- depth in Faucets or Fittings is preferable to shallow coverage of everything.
- evaluation should include field-level accuracy, character-limit compliance, and LOV validity. citeturn154558view1

---

## 3. Goals and Non-goals

### 3.1 Goals

| Goal | Definition of done |
|---|---|
| Structured enrichment | Raw rows become schema-valid product records with populated fields wherever evidence allows. |
| Controlled quality | Generated values are constrained by organiser LOV/master data/rules. |
| Evidence traceability | Every non-trivial enriched fact has a source/evidence reference and extraction confidence. |
| High accuracy | Accuracy is measured against the 200-row labelled dataset at field and record level. |
| Safe automation | Low-confidence or conflicting records are routed to review rather than silently published. |
| Scale | The same pipeline works on 1,000+ records without prompt-by-prompt manual intervention. |
| Demonstrability | The system has a fast, judge-friendly UI showing before → evidence → enriched record → validation. |
| Explainability | The system can show why it selected a manufacturer, taxonomy, attribute, or normalised value. |

### 3.2 Non-goals

- Building a complete industrial PIM/e-commerce platform.
- Perfectly automating every one of the 252+ delivery columns.
- Replacing all human content operations.
- Treating open-web search as an unrestricted source of truth.
- Generating attributes outside the organiser's allowed vocabularies.
- Optimising for prose quality at the expense of factual correctness.

---

## 4. Target Users

### Primary persona — Catalog Operations Analyst

Needs to transform supplier/manufacturer rows into publishable records quickly. Values traceability and bulk workflows.

### Secondary persona — Content Quality Reviewer

Needs to inspect exceptions, resolve ambiguous mappings, approve records, and understand why the system made a decision.

### Tertiary persona — Digital Commerce Manager

Needs consistent product copy, search-ready attributes, clean facets, and confidence in catalogue completeness.

### Hackathon judge

Needs to understand the problem, see measurable improvement, inspect evidence, and verify that the architecture is technically credible within a short demo.

---

## 5. Inputs

The solution is designed around the organiser dataset pack described in the solution guide:

### Working data

- `Sample-1000_Items.xlsx`
- `Unilog-Sample_200_Items-Input-vs-Output.xlsx`

### Rule book

- `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx`
- `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx`
- `Decimal_Fraction.xlsx`

### Master data / controlled vocabulary

- `UniCat_Manufacturer_and_Brand_List.xlsx`
- `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`
- `FAUCETS_LOV.xlsx`
- `Fittings_LOV.xlsx`

### Index

- `Reference_Documents_Summary.xlsx`

The exact dataset files are expected to be attached after this specification is created. The implementation must therefore use a **configuration-driven ingestion layer**, not hard-code assumptions about a single workbook layout. citeturn154558view1

---

## 6. Product Scope

### Tier 1 — Core judge-visible pipeline

1. Input profiling and placeholder removal
2. Manufacturer + brand resolution
3. Taxonomy classification
4. Evidence retrieval / source linking
5. Attribute extraction
6. LOV/UOM/format normalisation
7. Title/description generation
8. Validation + confidence scoring
9. Human-review queue
10. Export

### Tier 2 — Scale and intelligence

- semantic duplicate detection;
- knowledge graph / evidence graph;
- batch processing;
- retrieval caching;
- category-specific prompt/policy routing;
- evaluation dashboard;
- error analytics;
- source quality ranking.

### Tier 3 — Optional differentiators

- image/diagram ingestion with a vision-language model;
- product-family clustering;
- conflict-resolution agents;
- active learning from approved/rejected outputs;
- synthetic perturbation testing;
- digital asset recommendations.

---

## 7. Core User Stories

### US-01 — Upload raw catalogue

**As a catalog analyst**, I upload an organiser workbook and want the system to profile it, identify columns, clean placeholders, and show an ingest report.

**Acceptance criteria**

- workbook loads without manual column remapping for known templates;
- parser handles merged cells, multi-row headers, side-by-side blocks, and stray notes;
- placeholder values are classified as missing;
- every row receives a stable internal item ID.

### US-02 — Resolve manufacturer and brand

**As a content analyst**, I want messy manufacturer/brand strings mapped to exact canonical values.

**Acceptance criteria**

- matching uses exact, alias, fuzzy, and semantic candidate generation;
- final values come from approved master data;
- canonical code/name pair is preserved;
- ambiguous matches are reviewable.

### US-03 — Extract product facts

**As a content analyst**, I want product facts extracted from the raw row and authoritative manufacturer evidence.

**Acceptance criteria**

- each fact has source metadata;
- unsupported facts are not fabricated;
- conflicting values are retained as conflicts, not overwritten silently;
- extraction captures numeric values and units separately where possible.

### US-04 — Generate commerce copy

**As a commerce manager**, I want valid invoice, mobile, title, short, and long descriptions.

**Acceptance criteria**

- each field uses the organiser's formula/rule profile;
- character limits are automatically checked;
- copied facts trace back to structured product evidence;
- casing and symbols are normalised.

### US-05 — Validate before publish

**As a quality reviewer**, I want a single validation score and a list of blocking errors.

**Acceptance criteria**

- schema, LOV, UOM, format, source, consistency, and provenance checks run automatically;
- critical errors prevent a record from being marked publish-ready;
- confidence is decomposed by component rather than presented as an opaque number.

### US-06 — Review exceptions

**As a reviewer**, I want to approve or correct only low-confidence fields.

**Acceptance criteria**

- review queue is sorted by business risk × uncertainty;
- reviewer sees evidence next to the proposed value;
- corrections are logged and can become future aliases/rules.

---

## 8. Product Workflow

```text
RAW WORKBOOK
   │
   ▼
[1] Ingest + Profile
   │
   ├── schema detection
   ├── placeholder cleanup
   └── row identity
   │
   ▼
[2] Entity Resolution
   │
   ├── manufacturer
   ├── brand
   └── part family / duplicate candidates
   │
   ▼
[3] Taxonomy Router
   │
   ├── category/classpath
   └── category-specific ruleset
   │
   ▼
[4] Evidence Retrieval
   │
   ├── manufacturer page
   ├── manufacturer PDF/catalog
   └── approved document set
   │
   ▼
[5] Fact Extraction
   │
   └── typed claims + source spans
   │
   ▼
[6] Normalisation Engine
   │
   ├── LOV mappings
   ├── UOM
   ├── fractions
   ├── casing/symbols
   └── house style
   │
   ▼
[7] Content Builder
   │
   ├── invoice description
   ├── mobile description
   ├── product title
   └── long description
   │
   ▼
[8] Validation Engine
   │
   ├── deterministic rules
   ├── semantic consistency
   ├── provenance coverage
   └── publish gate
   │
   ├───────────────┐
   ▼               ▼
APPROVED        REVIEW QUEUE
   │               │
   └──────┬────────┘
          ▼
      EXPORT / API
```

---

## 9. Functional Requirements

### FR-01 Ingestion

The system SHALL accept XLSX input and SHALL produce a normalised internal row model.

### FR-02 Data profiling

The system SHALL report null rates, placeholder rates, unique counts, suspicious formatting, and schema anomalies before enrichment.

### FR-03 Canonical entity resolution

The system SHALL map manufacturer and brand candidates to the supplied approved master data before using them in final content.

### FR-04 Taxonomy inference

The system SHALL infer a taxonomy/classpath using evidence from the input and supporting source material, then validate that attributes requested for the classpath exist in the relevant LOV.

### FR-05 Evidence retrieval

The system SHALL prioritise manufacturer-owned sources and supplied documentation. It SHALL store URL/document identifiers and retrieval timestamps. Marketplaces/distributor pages SHALL NOT be treated as authoritative sources where organiser rules exclude them. citeturn154558view1

### FR-06 Attribute extraction

The system SHALL extract attributes into a typed schema, including value, unit, normalised value, source, evidence span, confidence, and status.

### FR-07 Normalisation

The system SHALL use only approved UOM/LOV mappings for final output. It SHALL support decimal-to-fraction conversion using the supplied exact lookup table. citeturn154558view1

### FR-08 Generation

Generated product copy SHALL be assembled from validated facts rather than independently hallucinated by a free-form language model.

### FR-09 Validation

The system SHALL block publication when required fields, allowed values, character limits, or source requirements fail.

### FR-10 Human review

The system SHALL provide field-level review for low-confidence or conflicting claims.

### FR-11 Export

The system SHALL export an output workbook/JSON that can be compared column-by-column with the organiser's delivery format.

### FR-12 Audit

The system SHALL preserve an immutable decision record for every generated field.

---

## 10. Non-functional Requirements

| Requirement | Target |
|---|---|
| Reproducibility | Same input + same reference snapshot should produce deterministic rule-layer outputs. |
| Traceability | ≥95% of non-empty enriched fields in the demo should expose a source or derivation path. |
| Safety | Unsupported facts become `UNKNOWN`/review, not invented values. |
| Batch throughput | Target ≥100 items/minute for local deterministic transforms; web/LLM steps may be slower but must be batched/cached. |
| Availability during demo | Fully runnable from a prepared environment without depending on uncontrolled external sites. |
| Observability | Every stage produces counts, latency, errors, and confidence distributions. |
| Extensibility | New category = new config/rules/LOV, not a rewrite of the pipeline. |
| Data handling | Do not send more data to an external model than needed; allow a local/sandbox model path where available. |

---

## 11. Success Metrics

### Primary

1. **Field Accuracy:** percentage of predicted fields matching the organiser ground truth after approved normalisation.
2. **Valid LOV Rate:** percentage of categorical outputs that are in the allowed vocabulary.
3. **Rule Compliance:** percentage of populated fields meeting casing, formula, symbol, and character constraints.
4. **Evidence Coverage:** percentage of enriched facts with traceable evidence.
5. **Review Efficiency:** percentage of rows/fields auto-approved without human intervention.

### Secondary

- duplicate resolution accuracy;
- taxonomy accuracy;
- attribute completeness;
- source-authority rate;
- conflict detection rate;
- processing time per 100/1,000 items;
- cost per processed item if external model/API usage is measured.

---

## 12. MVP Acceptance Gate

The MVP is ready for judging when it can:

- load the supplied 200-item ground truth;
- enrich a focused category end-to-end;
- show exact comparison against the delivery format;
- reject invented/unapproved values;
- show source evidence and confidence;
- run the same flow on the 1,000-item scale dataset;
- produce an export;
- demonstrate measurable metrics before and after validation.

---

## 13. Recommended Demonstration Scope

### Primary: Fittings

Fittings are ideal for demonstrating entity/value normalisation because the organiser describes mappings from many manufacturer connection variants into a smaller set of canonical connection values and many material-construction values into a simpler approved material list. citeturn154558view1

### Secondary: Faucets

Faucets are ideal for demonstrating category-specific generation because the organiser provides a tightly specified category package with fixed attribute order, description build order, and visual guidance. citeturn154558view1

### Why this scope

A narrow category lets the team show a complete story: classification → retrieval → extraction → normalisation → generation → validation → export, instead of claiming shallow coverage of the entire catalogue.

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated attributes | Generate only from evidence-backed structured facts. |
| Wrong manufacturer match | Candidate ranking + exact master-data validation + review threshold. |
| Wrong category | Taxonomy confidence + category-specific attribute consistency checks. |
| Web instability | Cache evidence snapshots and support uploaded source documents. |
| Prompt drift | Version prompts and rule profiles; log model/rule versions. |
| Workbook parsing failures | File-specific parser adapters and ingestion tests. |
| Over-engineering | Keep deterministic validation and output export as the backbone. |
| Demo failure | Prepare a local replay dataset and a no-network fallback. |

---

## 15. Product Principle

**The LLM is the language interface, not the source of truth.**

Reference data, source evidence, deterministic transformations, and validation rules decide what may appear in the final commerce record. The model decides how to interpret, reconcile, and express that information within those constraints.
