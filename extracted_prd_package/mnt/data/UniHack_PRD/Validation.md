# UniHack — Validation

## 1. Validation Mission

Validation is the system's final safety barrier between **AI output** and **commerce-ready output**.

The organiser's challenge strongly rewards constrained, traceable outputs: LOV compliance, UOM standards, exact manufacturer/brand values, character limits, and source requirements are part of the specification. citeturn154558view1

---

## 2. Validation Pipeline

```text
Generated Record
      │
      ▼
Schema Validator
      │
      ▼
Required-field Validator
      │
      ▼
Vocabulary / LOV Validator
      │
      ▼
UOM + Fraction Validator
      │
      ▼
Format + Character Validator
      │
      ▼
Cross-field Validator
      │
      ▼
Evidence / Provenance Validator
      │
      ▼
Semantic Claim Checker
      │
      ▼
Publish Gate
```

---

## 3. Validation Levels

### Level 1 — Syntax

- correct JSON/object structure;
- valid field types;
- no illegal characters where prohibited.

### Level 2 — Schema

- expected columns exist;
- data types match;
- required fields are present.

### Level 3 — Vocabulary

- manufacturer approved;
- brand approved;
- classpath valid;
- LOV value valid.

### Level 4 — Style

- UOM approved;
- casing correct;
- title formula correct;
- character limits correct;
- symbols correct.

### Level 5 — Semantic

- attributes are compatible with category;
- description agrees with attributes;
- no contradictory values.

### Level 6 — Evidence

- factual claims have valid support;
- source identity matches product;
- evidence is not stale/irrelevant where freshness matters.

---

## 4. Rule Object

Represent rules as data.

```json
{
  "rule_id": "TITLE.FITTINGS.001",
  "field": "product_title",
  "category": "Fittings",
  "type": "template",
  "template": "Brand + MPN + Fitting Type + Key Attributes",
  "severity": "blocking",
  "version": "1.0"
}
```

This lets the validator be driven by configuration instead of custom code for every field.

---

## 5. Required-Field Validation

For each classpath, determine the field requirement profile:

```text
REQUIRED
OPTIONAL
CONDITIONAL
NOT_APPLICABLE
```

A missing required field is blocking.

A missing optional field is a completeness warning.

A not-applicable field should not be treated as missing.

---

## 6. LOV Validation

Algorithm:

```python
if field.is_controlled:
    if value in allowed_values(field, classpath):
        PASS
    elif normalized_candidate(value) in allowed_normalized_values:
        PASS_WITH_NORMALIZATION
    else:
        BLOCK
```

Never accept a semantically similar but unapproved value as publishable.

---

## 7. Manufacturer / Brand Validation

Validation must operate on the paired relationship:

```text
manufacturer code
       ↕
manufacturer name
       ↕
brand code
       ↕
brand name
```

A brand that exists globally but is not paired with the selected manufacturer must fail the rule.

---

## 8. UOM Validation

Checks:

1. unit exists in UOM reference;
2. unit belongs to correct measurement type;
3. value-unit pairing is valid;
4. display spacing is correct;
5. unit casing/abbreviation is correct.

Examples:

```text
24 in      ✓
24in       ✕
24 IN.     ✕ if not approved
24 inches  ✕
```

The organiser guide specifically requires the approved UOM forms and a space between number and unit. citeturn154558view1

---

## 9. Fraction Validation

If the source value is an inch decimal, validate that the formatted fraction appears in the supplied fraction table where applicable.

```text
50.25 → 50-1/4
0.5   → 1/2
```

Do not accept a mathematically close but non-exact fraction if the lookup table contains the exact mapping. citeturn154558view1

---

## 10. Character Validation

```python
def validate_length(text, min_len=None, max_len=None):
    n = len(text)
    return (
        (min_len is None or n >= min_len)
        and (max_len is None or n <= max_len)
    )
```

Do not count Unicode code points differently from the organiser requirement without explicitly documenting the chosen counting convention.

---

## 11. Content Consistency Validation

Example checks:

### MPN consistency

```text
canonical MPN == MPN in title
canonical MPN == MPN in mobile description
```

### Attribute consistency

```text
sound_level attribute = 47 dBA
long description contains 47 dBA
```

### Brand consistency

```text
canonical brand == brand in title
canonical manufacturer ≠ incorrectly inserted brand
```

### Numeric consistency

If `wash_cycles = 5`, the title/description must not say `6`.

---

## 12. Unsupported Claim Detection

Use a claim extractor on generated text and compare claims against the evidence graph.

```text
Generated sentence
      ↓
atomic claims
      ↓
claim matching
      ├─ supported → PASS
      ├─ derivable → PASS if rule allows
      ├─ ambiguous → REVIEW
      └─ unsupported → BLOCK
```

This makes hallucination testing measurable.

---

## 13. Provenance Validation

A factual field is publishable only if one of these is true:

- directly supported by an authoritative source;
- deterministically derived from supported values;
- explicitly supplied in organiser input where that input is authoritative for the field.

The system should record the derivation chain.

---

## 14. Confidence Validation

Confidence should be based on observed signals rather than LLM self-report.

Recommended inputs:

- source authority;
- MPN match strength;
- extraction agreement;
- LOV distance;
- rule pass/fail;
- cross-field agreement;
- human approval history.

LLM-generated `"confidence": 0.99` is not sufficient evidence by itself.

---

## 15. Publish Gate

```text
BLOCK if:
  any critical field invalid
  OR unsupported critical claim exists
  OR required provenance missing
  OR controlled value invalid
  OR source policy violated

REVIEW if:
  no blocker
  AND confidence below threshold
  OR non-critical conflict exists

PUBLISH if:
  all blockers clear
  AND rules pass
  AND provenance coverage is sufficient
```

---

## 16. Repair Engine

### Allowed automatic repairs

- trim whitespace;
- canonicalise UOM;
- canonicalise approved spelling;
- format fractions from exact lookup;
- enforce title casing if rule is deterministic;
- remove duplicate punctuation.

### Not allowed

- invent a missing value;
- change numeric specifications;
- choose an unverified manufacturer;
- resolve an unresolved conflict by guessing.

---

## 17. Validation Output

Every run should produce:

```json
{
  "status": "review",
  "blocking_errors": [
    {
      "field": "brand",
      "code": "BRAND.MISMATCH",
      "message": "Brand is not a valid pair for selected manufacturer"
    }
  ],
  "warnings": [],
  "checks_passed": 42,
  "checks_failed": 1,
  "review_fields": ["brand"]
}
```

---

## 18. Validation Test Suite

### Unit tests

- UOM normalisation;
- fraction conversion;
- LOV lookup;
- manufacturer-brand pairing;
- title length;
- placeholder cleanup.

### Integration tests

- raw row → canonical product;
- evidence → claims;
- claims → normalised values;
- values → descriptions;
- description → validator.

### End-to-end tests

- 200-row benchmark;
- 1,000-row batch;
- Fittings scenario;
- Faucets scenario.

### Failure tests

- fake MPN;
- conflicting sources;
- invalid manufacturer;
- invalid brand;
- illegal unit;
- unsupported attribute;
- overlength title;
- empty source result.

---

## 19. Validation Metrics

Track:

```text
validation_pass_rate
blocking_error_rate
lov_failure_rate
uom_failure_rate
length_failure_rate
unsupported_claim_rate
source_policy_violation_rate
review_rate
repair_rate
```

A strong product should improve the validation pass rate without simply deleting difficult fields.

---

## 20. Judge-Facing Validation Proof

The most convincing UI pattern is a side-by-side example:

```text
AI GENERATED
FRIGIDAIRE Professional Series ... 50.25 in ...
                  │
                  ▼
VALIDATOR
✓ MPN matches
✓ Brand approved
✓ Fitting/attribute LOV valid
✕ UOM format
                  │
                  ▼
AUTO REPAIR
50.25 in → 50-1/4 in
                  │
                  ▼
FINAL
✓ Publish ready
```

It demonstrates that the system does not merely generate; it generates **and verifies**.
