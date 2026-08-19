# Design.md — Data & Experience Design

**Project:** PartForge · Covers: canonical data model, API surface, and the judge-facing UI/UX design.
**Companion docs:** `Architecture.md` (system design) · `Rules.md` (business rules) · `Demo.md` (how this UI gets presented)

---

## 1. Design Goals

1. **Every screen answers "why" as well as "what."** A judge (or an analyst) should never see a value without one click to its provenance — the input it came from, the rule that transformed it, or the source it was cited from.
2. **The messy input stays visible.** We deliberately never hide the raw `Part_Desc` string — the before/after contrast is the whole value proposition, so the UI always shows both.
3. **Confidence is a first-class visual signal**, not a hidden number. Low-confidence fields look visibly different (not just a tooltip) so a reviewer can scan a record in seconds.
4. **The 200-item ground truth is a UI citizen, not just a backend metric.** Judges should be able to toggle "show expected value" next to any field for any of the 200 items.

---

## 2. Canonical Data Model (UPIR)

### 2.1 Full field reference

| Field | Type | Populated by | Notes |
|---|---|---|---|
| `sku` | string | Input (200-item file) / generated | Present in the 200-item Input sheet; generated for 1,000-item set if absent |
| `mfg_part_num` | string | Input | Raw MPN, verbatim |
| `part_desc_raw` | string | Input | Verbatim raw description — never overwritten |
| `manufacturer.raw` | string | Input (`Part_Manuf`) | Pre-normalization |
| `manufacturer.canonical` | string \| null | Normalization Engine | From `UniCat_Manufacturer_and_Brand_List.xlsx`; null if unresolved |
| `manufacturer.code` | string \| null | Normalization Engine | `MANUFACTURER_CODE` |
| `manufacturer.match_confidence` | float | Normalization Engine | 0–1 |
| `brand.raw` | string | Input (`E1_Brand`/`Unilog_Brand`/`DIB_Brand`) | Pre-placeholder-filter |
| `brand.canonical` | string \| null | Normalization Engine (or MB-5 fallback to manufacturer) | |
| `brand.code` | string \| null | Normalization Engine | |
| `classification.dept` | string | Classification Agent | |
| `classification.class` | string | Classification Agent | |
| `classification.fine` | string | Classification Agent | |
| `classification.classpath` | string | Classification Agent | Full `Dept > Class > Fine` |
| `classification.unspsc` | string \| null | Classification Agent (category file) | Null is valid — see Rules.md CL-4 |
| `classification.confidence` | float | Classification Agent | |
| `classification.candidates[]` | array | Classification Agent | Top-3 alternates, shown when confidence is low |
| `attributes[]` | array of objects | Attribute Extraction + Enrichment + Normalization | See §2.2 |
| `descriptions.invoice_desc` | string | Description Builder | ≤40 char, CAPS |
| `descriptions.mobile_desc` | string | Description Builder | 60–80 char |
| `descriptions.product_title` | string | Description Builder | |
| `descriptions.long_description` | string | Description Builder | |
| `descriptions.marketing_desc` | string | Description Builder | |
| `digital_assets.status` | enum | — | Always `"not_built"` this build — see `PRD.md` §3.2 |
| `confidence_score` | float | Aggregation of stage confidences | Record-level rollup |
| `needs_review` | boolean | Validation Gate | |
| `review_reasons[]` | array of strings | Any stage | Human-readable, e.g. `"no_confident_classpath"`, `"unmapped_uom: 3/8 CPLG"` |
| `agent_trace[]` | array of objects | Every stage | `{stage, input_hash, output_summary, duration_ms}` |
| `pipeline_version` | string | System | For reproducibility |

### 2.2 `attributes[]` item schema

```json
{
  "label": "Sound Level",
  "value": "47",
  "normalized_value": "47 dBA",
  "lov_matched": true,
  "source": "manufacturer_source",
  "source_url": "https://www.frigidaire.com/.../spec-sheet.pdf",
  "confidence": 0.93,
  "sequence": 6
}
```

`source` is one of: `input` (extracted from `Part_Desc` directly), `lov` (resolved via controlled vocabulary match), `manufacturer_source` (from allowlisted RAG retrieval), `inferred` (LLM-derived, always paired with a lower confidence and eligible for review).

---

## 3. API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/pipeline/run` | POST | Kick off a batch run over a given input file (200-item or 1,000-item), returns `run_id` |
| `/pipeline/run/{run_id}/status` | GET | Stage-by-stage progress for a run |
| `/records` | GET | List UPIR records, filterable by `classpath`, `needs_review`, `confidence_score` range |
| `/records/{sku}` | GET | Full UPIR record including `agent_trace[]` |
| `/records/{sku}/ground-truth` | GET | The matching row from the 200-item Delivery Format, if it exists — for side-by-side display |
| `/records/{sku}/review` | POST | Human reviewer approves/edits/rejects a flagged field |
| `/evaluation/{run_id}` | GET | Full metrics report per `Evaluation.md` |
| `/reference/{table}` | GET | Introspect a loaded reference table (uom, manufacturer_brand, lov, decimal_fraction) — for debugging/demo transparency |

All endpoints are read-heavy and stateless except `/pipeline/run` and `/records/{sku}/review`, keeping the demo backend simple to run locally.

---

## 4. UX Design — Judge-Facing Application

### 4.1 Information architecture

```
┌────────────────────────────────────────────────────────┐
│  Top nav:  Overview │ Pipeline Run │ Record Explorer │  │
│            Review Queue │ Metrics Dashboard            │
└────────────────────────────────────────────────────────┘
```

### 4.2 Screen 1 — Overview
Landing screen. Shows: dataset selector (200-item ground truth / 1,000-item volume set), last run summary card (items processed, avg confidence, % needing review), and three big-number KPIs pulled live from the evaluation harness (classification accuracy, LOV compliance %, char-limit compliance %). This screen exists so a judge gets the headline result in the first five seconds.

### 4.3 Screen 2 — Pipeline Run (the "wow" screen)
A single item is selected (defaults to the dishwasher example or a Faucet/Fitting item) and animated left-to-right through the 8 pipeline stages as a horizontal stepper — matching the exact flow named in the brief: *Input analysis → De-duplication → Taxonomy & classification → Attribute extraction → Enrichment → Cleansing & normalization → Description building → Digital assets.* Each stage card, when clicked, expands to show:
- What went in
- What came out
- Which rule/table/agent was responsible (deep link into `Rules.md` rule IDs, rendered as tooltips)
- A timing badge (ms)

Digital Assets is shown as a **greyed-out stage card** labeled "Roadmap — see Phases.md," which is an intentional honesty signal to judges rather than a gap we hide.

### 4.4 Screen 3 — Record Explorer
A table of all processed records (both datasets), each row showing SKU, classpath, confidence (color-coded: green ≥0.9, amber 0.7–0.9, red <0.7), and a "needs review" badge. Clicking a row opens the **Record Inspector**:

```
┌───────────────────────────────┬───────────────────────────────┐
│  RAW INPUT                    │  ENRICHED OUTPUT               │
│  Part_Desc: "PDSH4816AF        │  Product Title:                │
│  Dishwasher SS - Display Only" │  "FRIGIDAIRE® Professional      │
│  Part_Manuf: FRIGIDAIRE        │  Series PDSH4816AF Dishwasher   │
│  E1_Brand: -- Unbranded --     │  With CleanBoost™, Leg          │
│                                 │  Mounting, 5-Wash Cycle,        │
│                                 │  Stainless Steel"    [source ⓘ]│
├───────────────────────────────┴───────────────────────────────┤
│  Attributes table: Label │ Value │ Source │ Confidence │ ⓘ      │
├─────────────────────────────────────────────────────────────────┤
│  [Toggle: Show ground-truth expected value]  ← only for 200-set │
│  [Toggle: Show agent trace]                                     │
└─────────────────────────────────────────────────────────────────┘
```

The **"Show ground-truth expected value"** toggle is the single most important UX element for judge credibility: it overlays the actual Delivery Format cell next to every generated field, with a green/red match indicator, computed live — not a static screenshot.

### 4.5 Screen 4 — Review Queue
A worklist of `needs_review = true` records, groupable by `review_reason`. Each entry is actionable inline (approve / edit / reject) to demonstrate the human-in-the-loop loop is real, not decorative. This screen directly demonstrates FR-10 and the "needs human review" principle the brief calls out as "a genuinely valuable feature," not a failure state.

### 4.6 Screen 5 — Metrics Dashboard
Implements the full metric set from `Evaluation.md`: a scorecard grid (classification accuracy, LOV compliance %, char-limit compliance %, manufacturer/brand match rate, UOM/fraction correctness, hallucination rate, review-flag precision, throughput), each with a drill-down into the specific failing records. This screen is what makes "show your evaluation" (Solution Guide §4) a live artifact instead of a claim in a slide deck.

---

## 5. Visual Design Principles

- **Two-column raw/enriched layout everywhere a record is shown** — reinforces the transformation story visually, every time.
- **Color is reserved for confidence and match state** (green/amber/red, plus a neutral grey for "not built / roadmap") — not used decoratively, so it stays meaningful.
- **Provenance is always one click away** (an "ⓘ" icon on every generated field), never buried in a separate tab.
- **Numbers are never presented without their denominator** — "94% LOV compliance" is always shown as "376 / 400 attribute values," so judges can sanity-check the metric itself.
- **The Digital Assets stage is visibly present but visibly inactive** everywhere it would appear, rather than omitted — this is a deliberate scope-honesty choice per `PRD.md` §3.2.

---

## 6. State Management (Frontend)

| State slice | Scope | Notes |
|---|---|---|
| `currentRun` | Global | Active/last pipeline run metadata |
| `selectedDataset` | Global | 200-item vs 1,000-item toggle |
| `records[]` | Per-run, paginated | Lazily fetched via `/records` |
| `selectedRecord` | Screen-local | Drives Record Inspector |
| `reviewQueue[]` | Global, polled | Drives Review Queue badge count in nav |
| `metrics` | Per-run | Drives Metrics Dashboard, refetched on run completion |

---

## 7. Accessibility & Clarity Notes

- Confidence color-coding is paired with a text label (`High`/`Medium`/`Low`), not color alone.
- All tables support keyboard navigation for the live-demo walkthrough (see `Demo.md`).
- The pipeline stepper (§4.3) works as a static, readable list if animation is disabled — no information is animation-only.

---

**Related documents:** `PRD.md` · `Architecture.md` · `Rules.md` · `Evaluation.md` · `Demo.md`
