# Rules.md — Business Rule Specification

**Project:** PartForge · **Purpose:** This document is the single source of truth for every deterministic rule the pipeline enforces. If a rule is described here, it is implemented as a **table lookup or validator function**, never left to an LLM's discretion. Rules are stored as versioned, config-driven rule packs (YAML/JSON) so they can be updated as the Content Guidelines evolve without touching pipeline code.

---

## 1. Rule Philosophy

> "The output is constrained, not creative." — Solution Guide, §4

Every rule below exists to answer one question for a given field: **is this the one approved way to write this value, or not?** There is no "close enough." A rule either matches or the field is flagged. This document is organized by rule domain, in the order the pipeline applies them (see `Architecture.md` §4 for stage mapping).

---

## 2. Placeholder Handling Rules

**Source:** Solution Guide §4 · `Sample-1000_Items.xlsx` brand columns

| Rule ID | Rule |
|---|---|
| PH-1 | The following strings, wherever encountered in a brand field, are treated as **null**, not data: `-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --` |
| PH-2 | Placeholder detection runs **before** any fuzzy-matching or LLM step touches the field — a placeholder must never be passed to a matcher as if it were a candidate string |
| PH-3 | The placeholder list is config-driven and extensible; any string matching the pattern `^-- .* --$` encountered during ingestion that isn't already in the list is logged as a **candidate new placeholder** for human confirmation, not silently treated as real data |
| PH-4 | When both `E1_Brand`, `Unilog_Brand`, and `DIB_Brand` are placeholders/empty, `manufacturer` (from `Part_Manuf`) becomes the value used wherever "brand" is required downstream — per the explicit rule in the Manufacturer/Brand master data description: *"Where an item has no brand, the manufacturer name is used instead."* |

---

## 3. Unit of Measure (UOM) Rules

**Source:** `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx` (Sheet 1: ~500 abbreviations / 89 measurement types; Sheet 2: 22 house-style rules)

| Rule ID | Rule |
|---|---|
| UOM-1 | Every unit written anywhere in generated output must be the **single approved abbreviation** from Sheet 1 for its measurement type — never a synonym, never the raw source spelling |
| UOM-2 | A space always separates a numeric value and its unit: `24 in`, never `24in` |
| UOM-3 | Raw-to-approved mapping is many-to-one: `inches`, `IN.`, `inch`, `"` all resolve to the one approved form for the "length" measurement type; the mapping table is built once at load time from Sheet 1 and queried by exact/normalized-string lookup |
| UOM-4 | The 22 house-style rules on Sheet 2 (hyphenation, symbol usage, technical-abbreviation formatting) are applied **after** unit substitution, as a second normalization pass over the full string — because they govern formatting of the surrounding text, not just the unit token itself |
| UOM-5 | If a unit token in the source data cannot be matched to any of the ~500 approved abbreviations (even after normalization: lowercasing, stripping punctuation, singular/plural folding), the token is left unconverted and the field is flagged `unmapped_uom`, never guessed |
| UOM-6 | Measurement-type context matters: the same raw token can map differently depending on measurement type (e.g., `"` as inches vs. a quotation mark in a raw description) — the UOM matcher is scoped to the attribute/field it is normalizing, not run as a blind global find-replace |

**Implementation note:** loaded as `uom_rules(raw_variant, measurement_type, approved_abbreviation, worked_example)`, indexed on `raw_variant` (normalized) for O(1) lookup.

---

## 4. Decimal ⇄ Fraction Conversion Rules

**Source:** `Decimal_Fraction.xlsx` — 63 entries, 1/64 (0.015625) through 63/64 (0.984375)

| Rule ID | Rule |
|---|---|
| DF-1 | Any inch measurement published by a manufacturer as a decimal must be converted to trade-fraction form in buyer-facing fields (title, descriptions), per the explicit example: `0.5 in` → `1/2 in`, `50.25 in` → `50-1/4 in` |
| DF-2 | Conversion is a **table lookup**, not arithmetic done by the LLM — the fractional part of a decimal inch value is looked up against the 63-row table; only the documented 64ths-precision fractions are valid outputs |
| DF-3 | For a mixed number (whole + fraction, e.g., `50.25`), the whole-number part is preserved and only the fractional remainder (`.25`) is looked up and rejoined with a hyphen: `50-1/4 in` |
| DF-4 | If a decimal value's fractional part does not exactly match one of the 63 table entries (i.e., precision finer than 1/64), the value is **not force-rounded** silently — it is flagged for review with the nearest table value shown as a suggestion |
| DF-5 | **Parsing note:** the source file lays the 63 conversions out as **four side-by-side `Fraction \| Decimal` column blocks**, not one linear list — the loader must read it as four stacked pairs and concatenate them into a single 63-row table before use (per the explicit warning in the Solution Guide: *"read it as four stacked pairs of columns, not one"*) |

---

## 5. Manufacturer & Brand Canonicalization Rules

**Source:** `UniCat_Manufacturer_and_Brand_List.xlsx` — 27,000+ rows: `MANUFACTURER_NAME`, `MANUFACTURER_CODE`, `BRAND_NAME`, `BRAND_CODE`

| Rule ID | Rule |
|---|---|
| MB-1 | A raw manufacturer/brand string is resolved to the **exact canonical form** in the master list — including legal casing, spacing, suffixes (`Inc`, `LLC`, `Ltd`), and ® / ™ symbols. `frigidaire` → `FRIGIDAIRE®`, not a title-cased guess. |
| MB-2 | Resolution runs in two stages: (a) exact-match against a normalized index (lowercased, punctuation-stripped) first; (b) fuzzy match (e.g., trigram or embedding similarity) only if (a) fails |
| MB-3 | A fuzzy match is only auto-accepted above a defined confidence threshold **and** with a defined margin over the second-best candidate — ambiguous matches (two similarly-scored manufacturers) are routed to review, never auto-resolved to the top result by default |
| MB-4 | Once a manufacturer is resolved, its **paired brand** is looked up from the same row — brand is never resolved independently of its manufacturer once the manufacturer match is confident, to avoid mismatched manufacturer/brand pairs |
| MB-5 | Per PH-4, if no brand is present in source data (all placeholder/empty), the resolved **manufacturer name is substituted wherever brand would appear** in output fields (title, descriptions) |
| MB-6 | The Solution Guide explicitly notes the ground truth contains *"at least one row where the manufacturer and brand look mismatched"* — the evaluation harness (`Evaluation.md`) treats this as a known ground-truth artifact and reports it separately, not as a pipeline defect when it reproduces the same mismatch faithfully from source data. Rule MB-4 exists precisely to prevent PartForge from *introducing new* mismatches. |

---

## 6. Taxonomy & Classification Rules

**Source:** `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx` (general), `FAUCETS_LOV.xlsx` / `Fittings_LOV.xlsx` (category-specific, authoritative where they apply)

| Rule ID | Rule |
|---|---|
| CL-1 | Classification output is always a full `Dept > Class > Fine` classpath that **exists in the LOV/category file** — never a freeform or partially-invented path |
| CL-2 | For Faucets and Fittings items, `FAUCETS_LOV.xlsx` / `Fittings_LOV.xlsx` (Summary sheet: classpath + UNSPSC) take precedence over the general 161K-row LOV, since they are the fully-specified, worked-to-depth categories |
| CL-3 | Classification confidence is computed from retrieval similarity + LLM self-reported confidence, blended; below a defined threshold, the record is routed to review with the top-3 candidate classpaths attached for a human to pick from — the system never forces a low-confidence top-1 |
| CL-4 | UNSPSC is populated only where the category file or LOV provides it; the ground truth itself has documented blank UNSPSC cells, so a blank UNSPSC in output is a valid, honest state, not a defect, when the source genuinely lacks it |

---

## 7. Attribute Extraction Rules

**Source:** `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`, `FAUCETS_LOV.xlsx` (Attribute Detail sheet: sequence, filtering flag, permitted values, definitions, synonyms), `Fittings_LOV.xlsx` (390 fitting types, connection-type and material mappings)

| Rule ID | Rule |
|---|---|
| AT-1 | An attribute is only written to the record if its **label** is valid for the item's resolved classpath (per the LOV's classpath→attribute mapping) — attributes are not invented for a category that doesn't define them |
| AT-2 | An attribute's **value** must resolve to one of that attribute's `Normalized Values` in the LOV; free text is never accepted for a `Filtering = Y` attribute |
| AT-3 | Where the LOV provides `Guidelines`/`Remarks` for an attribute, those override generic extraction behavior for that attribute (e.g., a category-specific synonym list from `FAUCETS_LOV.xlsx`'s Attribute Detail sheet is checked before falling back to the general LOV's `Normalized Label`) |
| AT-4 | **Fittings-specific many-to-one normalization:** connection-type strings are mapped through the 1,472-variant → 515-canonical-value table; material strings are mapped through the 464-variant → 113-canonical-value table. These are lookup tables, structurally identical in role to the UOM table (§3) — many raw spellings, one approved output. |
| AT-5 | **Fittings-specific source constraint:** the 390 valid Fitting Types each carry a source URL in `Fittings_LOV.xlsx` — a fitting-type value is only accepted if it matches one of these 390 exactly; the source URL is retained as the attribute's provenance |
| AT-6 | Attribute **sequence** for display (order attributes appear in a description) is taken from `FAUCETS_LOV.xlsx`'s Attribute Detail sheet `sequence` column for Faucets — this is a fixed order, not left to the LLM to decide |
| AT-7 | Where extraction from the abbreviated `Part_Desc` alone is insufficient to populate a required attribute, the record is passed to the Manufacturer-Source Enrichment Agent (§8) before being marked incomplete |

---

## 8. Sourcing Hierarchy Rules

**Source:** `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx` sourcing rules, reiterated in Solution Guide §4

| Rule ID | Rule |
|---|---|
| SRC-1 | Product data used for enrichment must come from the **manufacturer's own site or official documentation** (spec sheets, install guides, datasheets hosted on the manufacturer's domain) |
| SRC-2 | Marketplaces (e.g., general e-commerce listings) and **distributor sites are explicitly excluded** as sources, even if they display the same product |
| SRC-3 | The retrieval agent enforces this via an **allowlist at the tool layer** — the fetch tool itself refuses non-allowlisted domains; this is not merely a prompt instruction to the LLM (see `AI_Strategy.md` §5 for why prompt-only enforcement is insufficient) |
| SRC-4 | Every fact pulled via enrichment carries its `source_url` on the attribute; a fact with no retrievable, allowlisted source is not written to the record |
| SRC-5 | If manufacturer domain identification itself is ambiguous (e.g., a manufacturer with multiple regional sites), the agent prefers the domain matched via the canonical manufacturer record (§5) over a guessed domain |

---

## 9. Description Formula Rules

**Source:** `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx` (formulas, character limits, casing) — illustrated concretely by the worked dishwasher example in the Solution Guide §3; category-specific word order fixed by `FAUCETS_LOV.xlsx`'s "Online Description build order" sheet for Faucets.

The pipeline implements **five description formats**, each a distinct formula, casing rule, and length constraint. The Description Builder (`Architecture.md` §4) is a **formula engine first, LLM compositor second**: the formula defines which normalized fields go in and in what order; the LLM's job is fluent phrasing within that fixed skeleton, not deciding content or order.

| Format | Length / Casing | Formula (general pattern) | Worked example (dishwasher) |
|---|---|---|---|
| **Invoice Description** | ≤ 40 characters, ALL CAPS | Item type + top distinguishing attributes, abbreviated, no brand | `DISHWASHER LEG 5 SST 120V 15A 50-1/4IN` |
| **Mobile Description** | 60–80 characters | Manufacturer + Brand + Item Type + Series + MPN, compact | `Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF` |
| **Product Title / Short Description** | Per category char cap in Content Guidelines | `Brand + Series + MPN + Item Type + key attributes` (explicit formula from the guidelines) | `FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel` |
| **Long Description** | Per category char cap | Brand + descriptive phrase + Series + full attribute set in LOV sequence order, each unit normalized (§3) | `FRIGIDAIRE® Dishwasher With CleanBoost™, Professional Series, 5 Wash Cycles, 120 V, 15 A, Leg Mounting, 24 in W x 24-1/4 in D, 50-1/4 in Depth With Door Open, 47 dBA Sound Level, Stainless Steel` |
| **Marketing / Feature Description** | Per category char cap | Benefit-oriented phrasing built from the same validated attribute set; most latitude for fluent language, still zero tolerance for invented attributes | Category-dependent — built from the same validated `attributes[]`, never from ungrounded text |

| Rule ID | Rule |
|---|---|
| DESC-1 | Every description format is assembled from the **already-normalized and LOV-validated** record — the LLM compositor never sees raw/unvalidated attribute candidates, only the accepted set |
| DESC-2 | Character-limit and casing compliance is checked **after** generation by a deterministic validator (regex/length check), not trusted from the prompt instruction alone; a violation triggers one regeneration attempt with the violation fed back explicitly, then a review flag if still non-compliant |
| DESC-3 | For Faucets, attribute order within Product Title and Long Description follows the exact sequence defined in `FAUCETS_LOV.xlsx`'s Online Description build order sheet — this is category-specific and overrides the general pattern above |
| DESC-4 | No description format may reference an attribute value that did not pass the LOV Validator Gate (`Architecture.md` §6) — this is the enforcement point for the brief's "a fluent description made of invented values scores zero" warning |
| DESC-5 | Symbols (®, ™) are reproduced exactly as they appear in the canonical manufacturer/brand record (§5), including in every description format that includes the brand name |

---

## 10. Category-Specific Rule Packs

Faucets and Fittings each get a dedicated rule pack layered on top of §1–§9, loaded from their respective `_LOV.xlsx` files:

**Faucets rule pack** (`FAUCETS_LOV.xlsx`)
- Classpath fixed to Kitchen & Bath Sink Faucets subtree (Summary sheet)
- Attribute sequence and filtering flags per Attribute Detail sheet
- Description word order per the Online Description build order sheet
- Visual style guide sheet informs (but does not gate, since Digital Assets is out of scope — `PRD.md` §3.2) any future asset work

**Fittings rule pack** (`Fittings_LOV.xlsx`)
- 390 valid Fitting Types, each source-URL-backed (AT-5)
- 1,472 → 515 connection-type canonicalization table (AT-4)
- 464 → 113 material canonicalization table (AT-4)

---

## 11. Rule Change Management

All rules above are implemented as **data**, not code:

```
/rules
  uom_rules.yaml          # generated from Unilog_Master_UOM_Standards...xlsx at build time
  decimal_fraction.yaml   # generated from Decimal_Fraction.xlsx
  manufacturer_brand.yaml # generated from UniCat_Manufacturer_and_Brand_List.xlsx
  lov_general.yaml        # generated from Unicat_Lov_v1_0...xlsx
  lov_faucets.yaml        # generated from FAUCETS_LOV.xlsx
  lov_fittings.yaml       # generated from Fittings_LOV.xlsx
  placeholders.yaml       # PH-1..PH-3
  description_formulas.yaml # DESC-1..DESC-5, per format/category
```

A change to the Content Guidelines document requires only a regeneration of `description_formulas.yaml`, never a code change — this is what makes the pipeline maintainable as Unilog's own standards evolve.

---

**Related documents:** `PRD.md` · `Architecture.md` · `Design.md` · `Validation.md` · `Evaluation.md`
