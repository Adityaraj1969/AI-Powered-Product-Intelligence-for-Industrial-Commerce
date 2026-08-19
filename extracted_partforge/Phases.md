# Phases.md — Execution Plan & Roadmap

**Project:** PartForge · UniHack 2026 (Unilog × Hack2Skill)
**Team assumption:** 4 members — AI/ML Engineer, Data/Backend Engineer, Full-Stack/Frontend Engineer, Data-Quality/PM Lead. Adjust role split if the team size differs; the phase sequence does not change.
**Note on timing:** hour ranges below are written against a standard 36-hour build sprint (a common Hack2Skill grand-finale format). Re-anchor the hour labels to whatever build window the organizers publish — the *order and gating of phases* is what matters, not the exact clock time.

---

## 0. Pre-Build Preparation (before the clock starts)

Everything in this phase can and should happen **before** the official build window opens, so no build hours are lost to orientation.

| Task | Owner |
|---|---|
| Read `Reference_Documents_Summary.xlsx` end to end (Solution Guide's own recommended first step) | Whole team |
| Open the 200-item Input sheet next to the Delivery Format sheet; trace 3 items across by hand | PM Lead + AI Engineer |
| Skim `UNILOG_INTERNAL_CONTENT_GUIDELINES.docx` for the fields we plan to generate; note formulas and char limits | AI Engineer |
| Stand up empty repo skeleton: `/pipeline`, `/rules`, `/api`, `/ui`, `/eval` per `Architecture.md` | Backend Engineer |
| Confirm LLM API access/keys and rate limits (see `AI_Strategy.md`) | Backend Engineer |
| Draft the UPIR schema in code from `Design.md` §2 | AI Engineer + Backend Engineer |
| Agree on the two deep-dive categories (Faucets, Fittings) and lock scope per `PRD.md` §5 — **do not revisit this decision mid-build** | Whole team |

---

## Phase 1 — Data Foundation (Hours 0–6)

**Goal:** every reference file is a queryable table; the messy parts of the pack are handled once, correctly, and never touched again.

| Task | Deliverable | Owner |
|---|---|---|
| Build the Excel ingestion parser: handle merged cells, multi-row headers, side-by-side blocks | `raw_record_store` populated from both 200-item and 1,000-item files | Backend Engineer |
| Parse `Decimal_Fraction.xlsx`'s four-block layout into one flat 63-row table | `decimal_fraction.yaml` | AI Engineer |
| Parse `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx` (both sheets) into `uom_rules.yaml` | UOM lookup table live | AI Engineer |
| Load `UniCat_Manufacturer_and_Brand_List.xlsx` into an indexed table (exact + fuzzy) | `manufacturer_brand` table + fuzzy index | Backend Engineer |
| Load `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx` into the `lov` table, indexed by classpath + attribute | `lov` table live | Backend Engineer |
| Load `FAUCETS_LOV.xlsx` and `Fittings_LOV.xlsx` as category override tables | Category rule packs live | AI Engineer |
| Implement placeholder filter (PH-1..PH-4 from `Rules.md`) | Clean brand fields across both datasets | Data-Quality Lead |
| **Exit checkpoint:** every reference file loads without silent row loss; a parse report proves it | Parse report artifact | Whole team |

**Phase 1 is the highest-leverage phase in the whole build** — every later phase is only as good as these tables. Do not proceed to Phase 2 until the parse report is clean.

---

## Phase 2 — Core Pipeline: Classification & Extraction (Hours 6–16)

**Goal:** a single Faucets item and a single Fittings item go end-to-end through classification and attribute extraction, scored against ground truth.

| Task | Deliverable | Owner |
|---|---|---|
| Build embedding index over classpaths (general LOV + Faucets/Fittings category files) | Retriever live | AI Engineer |
| Build the Classification Agent (retrieve top-k → LLM selects → confidence score) | Classpath assigned to test items | AI Engineer |
| Build the LOV Validator Gate (`Architecture.md` §6) | Reject/coerce/accept logic live | Backend Engineer |
| Build the Attribute Extraction Agent with structured tool-call output, constrained to resolved classpath's LOV | Attributes extracted for test items | AI Engineer |
| Implement Fittings many-to-one normalization (connection-type 1,472→515, material 464→113) | Fittings attribute normalization live | Data-Quality Lead |
| Wire up the de-duplication blocking + fuzzy scorer over the 1,000-item set | Duplicate clusters surfaced | Backend Engineer |
| **Exit checkpoint:** one Faucet item and one Fitting item, fully classified and attributed, manually verified against the 200-item ground truth | 2 verified end-to-end example records | Whole team |

---

## Phase 3 — Normalization & Description Building (Hours 16–24)

**Goal:** the five description formats generate correctly, character-limit-compliant, for the Faucets/Fittings items already classified.

| Task | Deliverable | Owner |
|---|---|---|
| Implement the deterministic Normalization Engine (UOM + fraction + manufacturer/brand) as a pipeline stage | Normalized fields on test records | Backend Engineer |
| Build the Description Formula Engine (skeleton per format, per `Rules.md` §9) | Formula skeletons defined per format | AI Engineer |
| Build the LLM Compositor for fluent phrasing within each formula skeleton | 5 description fields generated | AI Engineer |
| Build the post-generation char-limit/casing validator + regeneration-on-failure loop | Validator gate live | Backend Engineer |
| Scope and build the Manufacturer-Source Enrichment Agent (allowlisted domains only) on a small bounded sample | RAG enrichment demoed on ≥5 items with citations | AI Engineer |
| **Exit checkpoint:** all five description formats generated for both deep-dive categories, char-limit compliant, matched against the dishwasher-style worked example pattern | Sample outputs for demo | Whole team |

---

## Phase 4 — Scale Run, Evaluation Harness & Review Queue (Hours 24–30)

**Goal:** run the full pipeline over the 200-item ground truth (for scoring) and the 1,000-item set (for coverage), and build the metrics that prove it.

| Task | Deliverable | Owner |
|---|---|---|
| Run full pipeline over all 200 ground-truth items | 200-item run complete, stored | Backend Engineer |
| Build the Evaluation Harness (`Evaluation.md` metrics) scoring the 200-item run field-by-field | Metrics report generated | Data-Quality Lead |
| Run classification + normalization + templated description across the 1,000-item set | 1,000-item run complete | Backend Engineer |
| Build the Review Queue backend (filter on `needs_review`) and human-approve endpoint | Review Queue functional | Backend Engineer |
| Triage: inspect worst-performing field/category, do a targeted fix pass (not a rewrite) | Fixed regressions logged | Whole team |
| **Exit checkpoint:** metrics report is real, reproducible from a single command, and matches what will be shown on stage | `eval_report.json` + printed summary | Whole team |

---

## Phase 5 — UI Assembly & Polish (Hours 30–34)

**Goal:** the five screens in `Design.md` §4 are live and wired to real data — no mocked numbers.

| Task | Deliverable | Owner |
|---|---|---|
| Build Overview screen with live KPI cards | Screen 1 live | Frontend Engineer |
| Build Pipeline Run animated stepper for the dishwasher/faucet example | Screen 2 live | Frontend Engineer |
| Build Record Explorer + Inspector with ground-truth toggle | Screen 3 live | Frontend Engineer |
| Build Review Queue screen | Screen 4 live | Frontend Engineer |
| Build Metrics Dashboard wired to `eval_report.json` | Screen 5 live | Frontend Engineer + Data-Quality Lead |
| Visual pass: confidence color-coding, provenance icons, Digital Assets "roadmap" greyed-out state | Consistent visual system | Frontend Engineer |
| **Exit checkpoint:** a full click-through from Overview → a record → its provenance → the metrics dashboard, with zero hardcoded numbers | Working demo build | Whole team |

---

## Phase 6 — Demo Rehearsal & Submission (Hours 34–36)

| Task | Deliverable | Owner |
|---|---|---|
| Run the `Demo.md` script twice, timed, on the actual demo machine/network | Rehearsed run | Whole team |
| Record a backup video of the full demo flow in case of live failure | Backup video | Frontend Engineer |
| Freeze the codebase; tag the submission commit | Tagged release | Backend Engineer |
| Finalize pitch deck (`Demo.md` §5 structure) | Deck ready | PM Lead |
| Submit per Hack2Skill's submission checklist | Confirmed submission | PM Lead |

---

## Contingency Plan (if behind schedule)

Cut in this order — never cut ground-truth scoring, since it is what makes the whole submission credible:

1. **Cut first:** Manufacturer-Source Enrichment Agent (Phase 3) — degrade gracefully to "attributes from input + LOV only," clearly labeled in the UI as a scoped-out stretch
2. **Cut second:** 1,000-item volume run — fall back to reporting Phase 2–3 results on the 200-item set only, and say so explicitly rather than fudging coverage numbers
3. **Cut third:** Review Queue interactivity — ship it as read-only if the approve/edit endpoint isn't ready
4. **Never cut:** the Evaluation Harness and the ground-truth toggle in the Record Inspector — this is the single highest-credibility artifact in the whole submission (see Solution Guide §4: *"Show your evaluation... Judges will look for them."*)

---

## Post-Hackathon Roadmap (beyond this build)

For completeness — and to show judges the team understands the full problem even where scope was intentionally cut:

| Roadmap item | What it would add |
|---|---|
| **Digital Assets pipeline (Stage 8)** | Image sourcing from manufacturer sites (same allowlist as §8 of `Rules.md`), alt-text generation, background/format normalization per `FAUCETS_LOV.xlsx`'s visual style guide sheet |
| **Full-catalog classification** | Extend the Classification Agent beyond Faucets/Fittings across the full 161K-row LOV, with category-by-category confidence benchmarking before enabling auto-publish per category |
| **Production crawler for manufacturer enrichment** | Scheduled, robots.txt-respecting crawler with per-domain rate limits and source freshness policies, replacing the bounded hackathon demo sample |
| **Active learning from the Review Queue** | Human corrections in the Review Queue feed back into few-shot examples / fine-tuning signal for the extraction and classification agents |
| **Knowledge-graph layer** | Formalize classpath → attribute → allowed-value and manufacturer → brand relationships as an explicit graph (e.g., Neo4j) instead of relational lookup tables, to support more complex cross-category queries as coverage grows |
| **Multi-tenant deployment** | Auth, per-distributor catalog isolation, and SLA-based throughput scaling per `Architecture.md` §7 |

---

**Related documents:** `PRD.md` · `Architecture.md` · `Evaluation.md` · `Demo.md`
