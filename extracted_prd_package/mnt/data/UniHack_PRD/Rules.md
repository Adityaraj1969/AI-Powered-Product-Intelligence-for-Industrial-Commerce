# UniHack — Rules

## 1. Purpose

These rules define what the UniHack Product Intelligence Engine is allowed to produce. The system should behave like a constrained data-production system, not a creative copywriter.

The organiser solution guide is explicit that output values must conform to controlled vocabularies, approved manufacturer/brand names, UOM standards, content rules, and sourcing requirements. citeturn154558view1

---

## 2. Rule Precedence

When two sources conflict, use this precedence unless the organiser's supplied content guideline specifies a stricter field-specific rule:

1. organiser content guidelines;
2. organiser category-specific LOV/rules;
3. organiser master data / approved vocabularies;
4. manufacturer primary source/documentation;
5. other explicitly allowed source;
6. model inference;
7. no value.

**Inference is never allowed to override explicit source evidence or controlled vocabularies.**

---

## 3. Missing-Value Rules

Treat the following as empty placeholders during preprocessing:

- `-- Unbranded --`
- `-- No Unilog Brand --`
- `-- No DIB Brand --`
- blank cells;
- whitespace-only cells;
- parser-generated null strings.

Do not train or prompt the model to reproduce these placeholders as real values. citeturn154558view1

Recommended internal values:

```text
NULL            = no known value
UNKNOWN         = searched/processed but not supported
CONFLICT        = credible sources disagree
NOT_APPLICABLE  = field is not valid for selected class
```

These must never be exported unless the delivery format explicitly expects them.

---

## 4. Manufacturer Rules

1. Match raw manufacturer text against the supplied manufacturer/brand master.
2. Preserve official casing and legal suffixes.
3. Preserve registered/trademark symbols when the master data includes them.
4. Never invent a manufacturer.
5. Never choose a manufacturer solely because its name appears in a generated description.
6. Manufacturer/brand pairing must be valid in the supplied master table.
7. When the raw value is ambiguous, keep candidates and route to review.

The organiser describes more than 27,000 manufacturer/brand rows with exact legal casing, suffixes, and symbols. citeturn154558view1

---

## 5. Brand Rules

1. Resolve brand only against approved master data.
2. Validate the brand belongs to the selected manufacturer.
3. Do not convert a manufacturer into a brand unless the rules explicitly allow it.
4. When an item has no brand, use the manufacturer name only where the organiser specification permits it.
5. Preserve approved `®`/`™` symbols.

---

## 6. MPN Rules

1. Preserve the manufacturer part number as the primary identifier.
2. Do not remove meaningful hyphens or slashes without a rule.
3. Do not insert spaces into an MPN based on stylistic preference.
4. When a source gives a different MPN representation, retain the raw value and canonical value separately.
5. Generated content must use the canonical MPN consistently.

---

## 7. Taxonomy Rules

1. Select taxonomy from the available taxonomy/classes.
2. Use evidence, not description keywords alone.
3. Verify category compatibility with the relevant LOV.
4. If multiple classpaths remain plausible, present alternatives and request review.
5. Do not fabricate a classpath absent from the organiser taxonomy.

---

## 8. Attribute Rules

### 8.1 General

Every extracted attribute should have:

- raw value;
- normalised value;
- optional unit;
- source;
- evidence span or document location;
- confidence;
- validation status.

### 8.2 Controlled values

If an attribute is controlled by the LOV, the final value must be an approved/normalised value. Synonyms may be used during retrieval/matching, but not necessarily in final output.

### 8.3 Free-text values

Use free-text only where the relevant field definition permits it. Do not turn a free-text field into an unconstrained dumping ground for unsupported attributes.

---

## 9. UOM Rules

The supplied UOM workbook is authoritative for final unit spelling and formatting. The solution guide states that it is the only permitted way to write units in output and requires a space between numeric value and unit. citeturn154558view1

### Required behaviour

```text
24 inches  → 24 in
24in       → 24 in
24 IN.     → 24 in
```

Exact approved output wins over model preference.

Store numeric value and unit separately internally:

```json
{"value": 24, "unit": "in", "display": "24 in"}
```

---

## 10. Fraction Rules

Use the supplied exact fraction/decimal lookup for inch conversions.

Examples from the organiser guide:

```text
0.5 in      → 1/2 in
50.25 in    → 50-1/4 in
```

Do not calculate approximate fractions when an exact lookup is available. The organiser provides 63 exact mappings from 1/64 through 63/64. citeturn154558view1

---

## 11. Content Rules

Each generated field is treated as a different product surface.

### Invoice description

- obey the organiser maximum length;
- use required casing;
- use only validated facts;
- optimise for compact recognition, not marketing prose.

### Mobile description

- obey the organiser range;
- prioritise manufacturer/brand/product type/series/MPN as required;
- avoid unsupported claims.

### Product title / short description

- follow category formula;
- use canonical brand, MPN, item type, and approved high-value attributes;
- preserve required symbols.

### Long description

- expand only facts that have evidence;
- use category-appropriate order;
- avoid introducing claims that are absent from the evidence bundle.

The organiser's example illustrates that one product is rewritten into multiple formats with different lengths/casing for different commerce surfaces. citeturn154558view1

---

## 12. Hallucination Rules

The model SHALL NOT:

- invent dimensions;
- invent materials;
- invent certifications;
- invent warranty information;
- infer electrical ratings without evidence;
- convert a likely feature into a definite feature;
- treat a distributor statement as authoritative where organiser rules exclude it;
- make up missing values to complete a template.

When evidence is unavailable:

```text
No evidence → UNKNOWN / REVIEW
```

not:

```text
No evidence → plausible model guess
```

---

## 13. Sourcing Rules

The organiser's guide states that product data should come from the manufacturer's own site or documentation and that marketplaces/distributor sites are explicitly excluded. citeturn154558view1

### Source record requirements

Each source must store:

```text
source_id
source_type
url_or_document_id
publisher/manufacturer
retrieved_at
content_hash
authority_score
```

Each claim should store:

```text
claim_id
product_id
attribute
value
source_id
evidence_span
extraction_method
confidence
```

---

## 14. Conflict Rules

When two authoritative sources disagree:

1. prefer the source with stronger manufacturer authority;
2. prefer product-specific over category-level evidence;
3. prefer newer documentation only where date is meaningful;
4. retain both claims internally;
5. mark the field `CONFLICT` if the difference cannot be safely resolved;
6. route high-impact conflicts to human review.

Never hide a conflict just to produce a complete-looking row.

---

## 15. Validation Rules

### Blocking errors

- invalid manufacturer code/name;
- invalid brand/manufacturer pairing;
- invalid LOV value;
- illegal UOM;
- exceeded hard character limit;
- unsupported high-impact factual claim;
- missing mandatory field;
- malformed schema;
- missing required provenance.

### Warnings

- low confidence;
- source is weak but allowed;
- optional field missing;
- non-critical style deviation.

---

## 16. Repair Rules

Validation may trigger automatic repair only when the repair is deterministic.

Safe repairs:

- unit abbreviation;
- whitespace;
- casing;
- punctuation;
- decimal-to-fraction lookup;
- approved synonym → canonical value.

Unsafe repairs:

- inventing an attribute;
- choosing among two unresolved manufacturers;
- silently rewriting a conflicting technical specification;
- adding a feature because it is typical for a product class.

---

## 17. Review Policy

Route a record to human review when:

```text
identity_confidence < threshold
OR taxonomy_confidence < threshold
OR critical_attribute_conflict = true
OR unsupported_claims > 0
OR blocking_validation_error > 0
```

Review should be **field-level** where possible. A reviewer should not need to re-approve the entire product because one attribute is uncertain.

---

## 18. Prompt Rules

Prompts must include:

1. task;
2. selected product/category context;
3. validated facts;
4. allowed values;
5. field-level constraints;
6. forbidden behaviour;
7. expected output schema;
8. evidence references where needed.

Do not pass the entire 161,000-row LOV into the prompt. Retrieve only the relevant classpath/attribute slice.

---

## 19. Data Lineage Rules

Every output field must be classified as one of:

```text
SOURCE_DIRECT
NORMALIZED_FROM_SOURCE
DERIVED_FROM_VALIDATED_FIELDS
GENERATED_FROM_VALIDATED_FIELDS
UNKNOWN
REVIEWED
```

This allows the UI to make a key distinction between **what the source said** and **how the system expressed it**.

---

## 20. Security and Secrets

- API keys live in environment variables/secrets only.
- Do not commit organiser datasets unless allowed.
- Do not expose secrets in logs.
- Sanitize uploaded filenames and external URLs.
- Cache only what is needed for reproducibility.
- Maintain a list of allowed source domains when possible.

---

## 21. Rule File Governance

Every run records:

```text
ruleset_version
lov_snapshot_version
uom_snapshot_version
manufacturer_master_version
prompt_version
model_name
model_version
```

No silent rule updates inside an evaluation run.
