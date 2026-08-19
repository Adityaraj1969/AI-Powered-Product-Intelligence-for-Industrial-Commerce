# UniHack — Phases

## 1. Execution Strategy

The delivery strategy is intentionally staged around the organiser's guidance: first understand the 200-row ground truth, then build the smallest measured end-to-end slice, then widen to the 1,000-row dataset. citeturn154558view1

The project should optimise for **judge-visible completeness** rather than feature count.

---

## 2. Phase 0 — Dataset Reconnaissance

### Objective
Understand the reference pack before writing enrichment logic.

### Tasks

- inspect `Reference_Documents_Summary.xlsx`;
- inspect the 200-row Input and Delivery Format side-by-side;
- trace at least three rows manually;
- identify output columns and rule groups;
- profile merged cells/multi-row headers;
- identify placeholders;
- build a data dictionary.

### Outputs

```text
data_dictionary.json
reference_inventory.json
parser_tests/
field_rule_matrix.csv
```

### Exit criteria

- every major input/reference file has a parsing strategy;
- top 30 judge-visible output fields are mapped to their source/rules.

---

## 3. Phase 1 — Ground-Truth Baseline

### Objective
Create the evaluation harness before the AI pipeline.

### Tasks

- load 200-row ground truth;
- normalise comparable values;
- define exact vs normalised vs semantic comparison;
- calculate baseline completeness;
- implement field-level scoring;
- produce a first evaluation report.

### Outputs

```text
evaluation/
  ground_truth_loader.py
  metrics.py
  baseline_report.html
```

### Exit criteria

A changed algorithm can be run and compared against the same ground truth with one command.

---

## 4. Phase 2 — Reference Knowledge Layer

### Objective
Turn spreadsheets/documents into queryable knowledge.

### Tasks

- manufacturer/brand index;
- LOV index by classpath/attribute;
- UOM lookup;
- fraction lookup;
- category-spec index;
- content-rule registry.

### Outputs

```text
knowledge/
  manufacturer_brand.db
  lov.db
  uom.db
  fractions.db
  category_specs.db
  rules.json
```

### Exit criteria

Given an attribute/classpath/value candidate, the system can return approved alternatives, normalised values, and the governing rule.

---

## 5. Phase 3 — Identity Resolution

### Objective
Resolve manufacturer/brand/MPN safely.

### Tasks

- exact matching;
- aliases;
- fuzzy matching;
- semantic candidate ranking;
- manufacturer-brand pair validation;
- confidence thresholds.

### Metrics

- manufacturer accuracy;
- brand accuracy;
- unresolved rate;
- ambiguous-match rate.

### Exit criteria

Identity errors are visible in evaluation rather than hidden inside downstream generation.

---

## 6. Phase 4 — Taxonomy Router

### Objective
Select classpath/category and activate the correct rule/LOV slice.

### Tasks

- candidate retrieval;
- description + source evidence scoring;
- taxonomy confidence;
- category-specific rule loading.

### Focus
Prioritise **Fittings** and **Faucets** because the organiser provides deep category specifications for both. citeturn154558view1

### Exit criteria

Selected taxonomy is measurable against ground truth, and the downstream attribute schema changes correctly by category.

---

## 7. Phase 5 — Evidence Retrieval

### Objective
Retrieve manufacturer-authoritative evidence.

### Tasks

- MPN-based search;
- manufacturer-domain filtering;
- page/PDF extraction;
- source caching;
- source authority scoring;
- evidence span capture.

### Exit criteria

For curated demo items, the system can show the exact evidence used for important attributes.

---

## 8. Phase 6 — Attribute Extraction + Normalisation

### Objective
Convert evidence into validated structured facts.

### Tasks

- typed extraction schema;
- unit parsing;
- UOM canonicalisation;
- fraction conversion;
- LOV candidate retrieval;
- synonym mapping;
- conflict detection.

### Exit criteria

At least one category is fully enriched with traceable facts and no unsupported final values.

---

## 9. Phase 7 — Commerce Content Builder

### Objective
Generate channel-specific copy from validated facts.

### Tasks

- field templates;
- category-specific ordering;
- invoice description;
- mobile description;
- title;
- long description;
- deterministic post-formatting;
- automatic repair only for safe rules.

### Exit criteria

The generated content passes hard length/casing/UOM/LOV rules for the targeted fields.

---

## 10. Phase 8 — Validation + Human Review

### Objective
Make correctness visible and actionable.

### Tasks

- blocking vs warning rules;
- field confidence;
- publish gate;
- review queue;
- reviewer actions;
- audit trail.

### Exit criteria

A bad output is rejected before export and the system explains why.

---

## 11. Phase 9 — Scale to 1,000 Items

### Objective
Prove the approach is more than a curated demo.

### Tasks

- batch processing;
- concurrency controls;
- caching;
- retries;
- failure recovery;
- progress UI;
- batch metrics;
- cost/latency measurement.

### Exit criteria

The entire 1,000-row dataset can be processed with a run report and export.

---

## 12. Phase 10 — Evaluation Hardening

### Objective
Protect against overfitting to a few demo rows.

### Tests

1. 200-row full evaluation;
2. category-stratified evaluation;
3. adversarial formatting tests;
4. placeholder tests;
5. unit-format tests;
6. invalid-LOV tests;
7. unsupported-claim tests;
8. missing-source tests;
9. duplicate/near-duplicate tests;
10. regression suite after every prompt/rule change.

---

## 13. Phase 11 — Demo Packaging

### Objective
Turn technical work into a top-tier pitch.

### Demo assets

- one 3–5 item live/cached flow;
- 200-row evaluation dashboard;
- 1,000-row scale result;
- architecture one-pager;
- failure-case example;
- evidence graph interaction;
- final export.

### Exit criteria

A judge can understand the value and technical defensibility without reading source code.

---

## 14. Suggested Team Split

### Track A — Data / Evaluation

- parsing;
- data dictionary;
- ground truth comparator;
- metrics;
- regression tests.

### Track B — AI / Retrieval

- RAG;
- extraction;
- entity resolution;
- taxonomy;
- source ranking.

### Track C — Product / Frontend

- dashboard;
- product explorer;
- evidence drawer;
- review queue;
- demo mode.

### Track D — Platform / Integration

- FastAPI;
- storage;
- batch orchestration;
- caching;
- Docker;
- export.

If the team is smaller, combine A+D first, then B+C.

---

## 15. Priority Matrix

| Feature | Priority | Judge value | Engineering risk |
|---|---:|---:|---:|
| 200-row evaluator | P0 | Very high | Low |
| Manufacturer/brand resolution | P0 | High | Medium |
| LOV/UOM validation | P0 | Very high | Low |
| Evidence traceability | P0 | Very high | Medium |
| Fittings end-to-end | P0 | Very high | Medium |
| Product UI | P0 | High | Medium |
| 1,000-row batch | P1 | High | Medium |
| Human review | P1 | High | Medium |
| VLM image enrichment | P2 | Medium | High |
| Full autonomous multi-agent system | P2 | Medium | High |

---

## 16. Definition of Done

A feature is done only when it has:

- implementation;
- unit/integration test;
- evaluation impact;
- error handling;
- observability;
- UI visibility if judge-relevant;
- reproducible run instructions.
