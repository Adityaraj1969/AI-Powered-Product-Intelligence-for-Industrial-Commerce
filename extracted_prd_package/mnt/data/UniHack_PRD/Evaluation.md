# UniHack — Evaluation

## 1. Evaluation Philosophy

The evaluation system must prove that the solution improves product data **without trading factual correctness for fluent text**.

The organiser explicitly recommends field-level accuracy against the 200 known-good rows, character-limit compliance, and LOV-valid output measurement. citeturn154558view1

The evaluation framework therefore uses four layers:

1. exact/normalised data accuracy;
2. rule compliance;
3. evidence/provenance quality;
4. operational impact.

---

## 2. Datasets

### Primary benchmark

`Unilog-Sample_200_Items-Input-vs-Output.xlsx`

- Input sheet = model input;
- Delivery Format = labelled target. citeturn154558view1

### Scale benchmark

`Sample-1000_Items.xlsx`

Used to measure coverage, throughput, stability, and exception handling. citeturn154558view1

---

## 3. Comparison Modes

### Exact match

For fields where formatting is meaningful.

```python
pred.strip() == truth.strip()
```

### Normalised match

Apply only allowed deterministic normalisations:

- whitespace;
- casing where case-insensitive;
- approved UOM equivalence;
- exact fraction mapping;
- approved synonym → canonical value.

### Semantic match

Use only for free-text descriptions where exact comparison is too brittle. Semantic similarity must **never** be used to excuse an invalid controlled value.

---

## 4. Core Metrics

## 4.1 Field Accuracy

For each field:

```text
field_accuracy = correct_predictions / eligible_ground_truth_values
```

Report both:

- macro-average across fields;
- weighted average by business priority.

### Business-weighted accuracy

```text
weighted_accuracy = Σ(field_accuracy × field_weight) / Σ(field_weight)
```

Recommended weights:

| Field group | Weight |
|---|---:|
| MPN / manufacturer / brand | 5 |
| taxonomy/classification | 5 |
| key filter attributes | 5 |
| dimensions / technical specifications | 4 |
| commerce descriptions | 2 |
| optional descriptive fields | 1 |

Weights are internal evaluation choices and should be documented.

---

## 5.2 Attribute Completeness

```text
completeness = populated_valid_fields / applicable_fields
```

Do not count fabricated values as successful completeness.

---

## 5.3 LOV Compliance

```text
lov_rate = approved_values / categorical_values_produced
```

Report by category and attribute.

This is one of the most important metrics because the challenge specifically constrains output through organiser LOVs. citeturn154558view1

---

## 5.4 UOM Compliance

```text
uom_compliance = correctly_formatted_units / total_units_output
```

Include:

- unit abbreviation;
- spacing;
- exact type;
- numeric/unit consistency.

---

## 5.5 Character Compliance

```text
char_compliance = fields_within_allowed_length / fields_with_length_rules
```

Report separately for invoice/mobile/title/long fields.

---

## 5.6 Provenance Coverage

```text
provenance_coverage = enriched_fields_with_evidence / enriched_fields
```

Target for the polished demo: ≥95% for non-trivial enriched factual fields.

---

## 5.7 Unsupported Claim Rate

```text
unsupported_claim_rate = unsupported_generated_claims / factual_claims_generated
```

This should trend toward zero for publishable records.

---

## 5.8 Review Rate

```text
review_rate = records_sent_to_review / records_processed
```

A lower review rate is not automatically better. The meaningful metric is **safe auto-approval**.

### Safe auto-approval

```text
safe_auto_approval = auto_approved_records / records_processed
```

subject to a minimum accuracy threshold.

---

## 6. Composite Quality Score

Use a transparent score rather than a black-box leaderboard number.

```text
Quality Score =
    35% Field Accuracy
  + 20% LOV/UOM Compliance
  + 15% Rule Compliance
  + 15% Evidence Coverage
  + 10% Safe Auto-Approval
  +  5% Throughput/Cost Efficiency
```

This is a project evaluation rubric, not an organiser-published scoring formula.

### Hard gates

Regardless of composite score:

- invalid controlled values cannot be counted as correct;
- unsupported critical specifications invalidate the field;
- source-policy violations are critical;
- hard character-rule failures are non-compliant.

---

## 7. Category-level Reporting

Always show:

```text
Fittings
  Accuracy: 96.1%
  LOV: 99.1%
  Evidence: 97.4%

Faucets
  Accuracy: 94.8%
  LOV: 98.7%
  Evidence: 95.5%
```

Numbers shown above are examples only; replace them with actual run results.

This proves the system is not only optimised for one easy category.

---

## 8. Baselines

### Baseline A — Raw passthrough

Return only input values.

### Baseline B — LLM-only generation

Ask a model to enrich the raw row with minimal context.

### System C — UniHack PIE

Hybrid pipeline with master data, RAG, structured extraction, normalisation, and validation.

The most persuasive experiment is:

```text
LLM-only          → fluent but invalid
PIE without RAG   → better structure, weak evidence
PIE full          → higher accuracy + controlled values + traceability
```

This ablation demonstrates why the architecture matters.

---

## 9. Error Taxonomy

Every failure should be assigned one primary reason:

```text
E01 wrong manufacturer
E02 wrong brand
E03 wrong taxonomy
E04 missing evidence
E05 wrong attribute
E06 wrong LOV mapping
E07 wrong UOM
E08 formatting/length
E09 unsupported claim
E10 source conflict
E11 parser issue
E12 generation issue
E13 validation bug
```

Plot a Pareto chart of the error classes.

---

## 10. Confidence Calibration

Group predictions into confidence buckets:

| Confidence | Expected use |
|---|---|
| 0.95–1.00 | auto-approve candidates |
| 0.85–0.949 | conditional auto-approve |
| 0.70–0.849 | human review |
| <0.70 | unresolved |

Measure precision in each bucket.

A strong system should show:

```text
higher confidence → higher empirical accuracy
```

If it does not, the confidence model needs recalibration.

---

## 11. Robustness Tests

### Input perturbation

Create controlled variants:

- lower case manufacturer;
- extra spaces;
- punctuation removed;
- unit written long form;
- decimal instead of fraction;
- abbreviation changes;
- brand omitted;
- placeholder inserted.

The correct normalised result should remain stable.

### Evidence perturbation

Remove one source document and verify that:

- supported fields remain stable;
- unsupported fields become review/unknown;
- the system does not hallucinate a replacement source.

---

## 12. Regression Testing

Every model/prompt/rule change runs:

```text
1. 200-row benchmark
2. targeted category benchmark
3. rule suite
4. hallucination suite
5. parser suite
```

Store results by run ID.

---

## 13. Judge Dashboard

The judge should see exactly five numbers first:

```text
FIELD ACCURACY       95.2%
LOV COMPLIANCE       99.0%
RULE COMPLIANCE      97.1%
EVIDENCE COVERAGE    96.3%
SAFE AUTO-APPROVAL   72.4%
```

Then allow drill-down by field/category/error.

Again, these are presentation placeholders, not actual results.

---

## 14. Evaluation Report Template

```text
Run ID:
Date:
Model:
Prompt version:
Ruleset:
Reference snapshot:

200-ROW RESULTS
Field Accuracy:
Normalised Accuracy:
LOV Compliance:
UOM Compliance:
Character Compliance:
Evidence Coverage:
Unsupported Claim Rate:
Safe Auto-Approval:

1,000-ROW RESULTS
Processed:
Failed:
Review:
Throughput:
Latency p50:
Latency p95:
Estimated cost/item:

TOP 5 ERRORS
1.
2.
3.
4.
5.

KEY ABLATION FINDING
...
```

---

## 15. Success Thresholds for Internal Readiness

Use the following as **team targets**, not claims of organiser scoring:

- ≥95% field accuracy on critical fields;
- ≥98% LOV compliance;
- ≥99% UOM compliance;
- ≥95% evidence coverage on factual enriched fields;
- 0 fabricated critical specifications in the final publishable set;
- >70% safe auto-approval on the chosen demo category;
- measurable advantage over the LLM-only baseline.

A lower number with a truthful error analysis is preferable to inflated metrics produced by excluding difficult rows.
