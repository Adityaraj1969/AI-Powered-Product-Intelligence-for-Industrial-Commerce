# Validation.md — Validation & Quality Assurance Plan

**Project:** PartForge · **Purpose:** define every gate a value must pass before it is allowed into a published UPIR record, and how we test that those gates actually work — as distinct from `Evaluation.md`, which measures *how accurate* the output is, this document defines *how we prevent bad output from shipping in the first place*.

---

## 1. Validation Philosophy

`Evaluation.md` tells us how well the pipeline performed. **Validation.md is what makes that score trustworthy** — a pipeline with no gates could still score well on 200 curated ground-truth items and fail badly the moment it sees the messier 1,000-item set, or a real catalog. Every gate below is designed to catch the specific failure modes named in the brief:

- *"A fluent description made of invented values scores zero."* → §3
- *"Placeholders are not data."* → §2
- *"Expect messy spreadsheets."* → §4
- *"Real data is imperfect — say so."* → §6
- *"Sourcing rules apply."* → §5

---

## 2. Ingestion Validation Gates

| Gate | Check | Failure behavior |
|---|---|---|
| Schema gate | Every raw row from `.xlsx` maps to the expected 6/10-column schema (Sample-1000 vs. 200-item Input) | Row logged in parse report, not silently dropped |
| Merged-cell gate | Merged cells resolve to the correct value in every derived row, not blank/duplicated incorrectly | Spot-checked against 10 known merged-cell rows per source file at build time |
| Placeholder gate | `-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --` (and any pattern-matched candidates, Rules.md PH-3) are nulled before matching | Unit test asserts 0% of these strings appear in any `manufacturer.canonical`/`brand.canonical` field post-pipeline |
| Encoding gate | Non-UTF-8 or unusual characters (®, ™, fractions) survive ingestion intact | Byte-level diff test on a sample of symbol-containing rows |

---

## 3. Grounding Validation Gates (the core anti-hallucination layer)

This is the direct implementation of `Architecture.md` §6 (LLM proposes, tables dispose):

| Gate | Applies to | Check | On failure |
|---|---|---|---|
| **Classpath existence gate** | Classification output | `classpath` must be a literal string present in the LOV/category file | Reject; route to review with top-3 candidates |
| **Attribute applicability gate** | Extracted attributes | `label` must be valid for the item's resolved classpath | Drop the attribute; log `review_reason: "attribute_not_applicable_to_classpath"` |
| **LOV value gate** | Extracted attributes | `value` must resolve to a `Normalized Value` for that attribute/classpath (exact, then near-match with a defined similarity floor) | Exact/near-match → accept/coerce; below floor → drop, flag |
| **Evidence span gate** | Extracted attributes | The declared `evidence_span` must be a genuine substring of the source text (`Part_Desc` or a cited manufacturer excerpt) | If the span doesn't verify, the attribute confidence is downgraded even if the LOV gate passed — a value can be technically valid but unsupported, and that distinction matters |
| **Manufacturer/brand existence gate** | Normalization output | `manufacturer.canonical`/`brand.canonical` must be an exact row in the 27K-row master list | Reject to `null` + flag; never a fuzzy string written as if exact |
| **UOM gate** | Normalization output | Every unit token must equal an approved abbreviation string | Reject unconverted token, flag `unmapped_uom` |
| **Fraction gate** | Normalization output | Every converted fraction must equal a value in the 63-row Decimal_Fraction table | Reject, flag with nearest-table-value suggestion |
| **Citation gate** | Manufacturer-source enrichment | Every enrichment-sourced attribute must carry a `source_url` from an allowlisted domain | Drop the value if no valid citation exists — an unsourced enrichment claim is worse than a missing field |

**Implementation note:** these gates run as a single deterministic validator module invoked identically whether the candidate value came from the Classification Agent, the Extraction Agent, or the Manufacturer-Source Agent — the gate does not trust the source of the candidate, only the candidate itself against the table.

---

## 4. Output Format Validation Gates

| Gate | Check | On failure |
|---|---|---|
| Character-limit gate | Each description format is within its defined length range | One regeneration attempt with the violation explicitly fed back; second failure → flag, do not silently truncate (Rules.md DESC-2) |
| Casing gate | Invoice description is 100% ALL CAPS; other formats follow their documented casing rule | Same regenerate-once-then-flag pattern |
| Symbol-fidelity gate | ®/™ symbols in output match the canonical manufacturer/brand record exactly | Automated diff check against `manufacturer_brand` table |
| Formula field-presence gate | Required components of a formula (e.g., Title = Brand + Series + MPN + Item Type + key attributes) are all present in the generated string | Missing component → regenerate with explicit reminder of the missing field |
| Sequence-order gate (Faucets) | Attributes appear in the description in the sequence defined by `FAUCETS_LOV.xlsx`'s Attribute Detail sheet | Automated reorder check; violation triggers regeneration |

---

## 5. Sourcing Compliance Validation

| Gate | Check | On failure |
|---|---|---|
| Domain allowlist gate | Every fetched URL during enrichment matches the manufacturer's canonical domain or an approved documentation subdomain | Fetch tool refuses the request outright — this is enforced at the tool layer, so there is no "failure path" to test around; the request simply cannot be made (Rules.md SRC-3) |
| Marketplace/distributor exclusion gate | A denylist of known marketplace/distributor domains is checked even within an otherwise-plausible-looking domain | Blocked at fetch time, logged for audit |
| Source-freshness sanity check | Retrieved content is checked for a reasonable minimum content length/structure (not an error page or redirect stub) before being used as citation evidence | If the fetch returns unusable content, the enrichment attempt is recorded as a miss, not silently treated as "no relevant info found" |

---

## 6. Ground-Truth-Aware Validation (handling known imperfection honestly)

Per the Solution Guide's explicit note about the 200-item file's own imperfections, the validation layer distinguishes between three states for any field, not two:

| State | Meaning | How it's surfaced |
|---|---|---|
| **Pass** | Value present, passed all applicable gates | Normal display |
| **Flagged** | Value present but failed a gate, or below confidence threshold | Review Queue, with specific `review_reason` |
| **Honestly blank** | No value produced because none could be confidently determined (including cases where ground truth itself is blank, e.g. UNSPSC/country-of-origin) | Displayed as blank, **not** as a flagged error — an honestly blank field is a correct behavior, not a defect |

This three-state model is what prevents the evaluation harness (`Evaluation.md` §7) from either over-penalizing legitimate abstention or, worse, incentivizing the pipeline to guess just to avoid a blank cell.

---

## 7. Test Suite Structure

```
/tests
  test_ingestion.py          # merged cells, multi-row headers, placeholder detection
  test_uom_rules.py          # every one of the ~500 UOM entries round-trips correctly
  test_decimal_fraction.py   # all 63 entries convert correctly both directions
  test_manufacturer_brand.py # exact-match + fuzzy-fallback + ambiguous-match routing
  test_lov_gate.py           # accept / coerce / reject logic across representative LOV entries
  test_classification_gate.py# classpath-existence enforcement, top-3 fallback behavior
  test_description_formats.py# char-limit, casing, formula field-presence per format
  test_sourcing_allowlist.py # allowlist enforcement, denylist enforcement, refusal behavior
  test_review_flagging.py    # every defined review_reason is triggered by its intended failure case
  test_e2e_golden_examples.py# the dishwasher example + 1 Faucet + 1 Fitting example, full pipeline, exact expected output
```

**Golden examples policy:** the dishwasher row from the Solution Guide's worked example (§3), plus one hand-verified Faucet and one hand-verified Fitting record, are checked into the test suite as **golden examples** — if a code change breaks any of these three, the build is considered broken, independent of what the aggregate `Evaluation.md` score says. This catches regressions that an aggregate metric could mask.

---

## 8. Manual Audit Process

Automated gates catch structural violations; they don't catch "this is technically LOV-valid but wrong for this item." For that:

1. A stratified sample of 20 records per run (10 `needs_review`, 10 not) is manually reviewed by the Data-Quality Lead.
2. Each is scored pass/fail against a short rubric: *Is the classpath right? Is every attribute actually true of this item? Would a buyer searching for this find it?*
3. Results feed the review-flag precision/recall metrics in `Evaluation.md` §3.5 and directly inform the Phase 4 triage pass in `Phases.md`.

---

## 9. Acceptance Criteria Before a Record Is "Published"

A UPIR record is only marked `published` (as opposed to sitting in the Review Queue) when **all** of the following hold:

- [ ] Classpath passed the existence gate
- [ ] Every attribute in `attributes[]` passed the LOV value gate or was explicitly dropped (not left in a failed state)
- [ ] Every unit token passed the UOM gate
- [ ] Every fraction conversion passed the fraction gate
- [ ] Manufacturer/brand passed the existence gate or is explicitly `null` with a review reason
- [ ] All five description fields passed their character-limit and casing gates
- [ ] `confidence_score` is above the record-level publish threshold, or the record has been manually approved via the Review Queue

A record failing any of these sits in `needs_review` indefinitely until resolved — there is no timeout-based auto-publish, by design.

---

**Related documents:** `PRD.md` · `Architecture.md` · `Rules.md` · `AI_Strategy.md` · `Evaluation.md`
