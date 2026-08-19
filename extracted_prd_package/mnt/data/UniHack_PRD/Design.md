# UniHack — Design

## 1. Design Goal

The interface should make an industrial data-quality workflow understandable in **under 60 seconds**. A judge should immediately see:

**messy input → evidence → canonical facts → commerce content → validation → business value**.

The UI should feel like a professional product-content operations console rather than an AI chatbot.

---

## 2. Design Principles

### Trust before wow

Show the source and rule beside generated values.

### Dense but not noisy

Industrial catalog work is data-heavy. Use compact tables, grouped metadata, and clear status indicators.

### Evidence is first-class

Evidence should not be buried behind a modal. The user should be able to trace a value in one click.

### Review only what needs review

Highlight uncertain fields rather than forcing a reviewer to read 250 columns.

### Demo-first composition

The first screen should answer:

1. What came in?
2. What did the system understand?
3. How do we know?
4. What changed?
5. Is it valid?

---

## 3. Information Architecture

```text
Dashboard
│
├── Runs
│   ├── 200-row evaluation
│   └── 1,000-row batch
│
├── Product Explorer
│   └── Product detail
│       ├── Input
│       ├── Evidence
│       ├── Enriched record
│       └── Validation
│
├── Review Queue
│
├── Rules & Vocabulary
│   ├── Manufacturer / Brand
│   ├── LOV
│   └── UOM
│
└── Evaluation
    ├── Accuracy
    ├── Rule compliance
    ├── Evidence coverage
    └── Failure analysis
```

---

## 4. Dashboard

### Header

**UniHack Product Intelligence Engine**

Subtitle: `From sparse industrial SKUs to validated commerce-ready content`

### KPI cards

```text
1,000 items processed
94.8% field accuracy
98.7% LOV compliance
96.2% evidence coverage
71% auto-approved
```

The numbers above are **mock values for layout only**. The live UI must display actual evaluation results.

### Pipeline status

```text
Input       ██████████ 100%
Identity    █████████  96%
Taxonomy    █████████  94%
Evidence    ████████   88%
Attributes  ████████   87%
Content     ████████   86%
Validation  ████████   86%
```

### Key message

> `1,000 raw rows → 1,000 validated records → 286 records routed to review`

The purpose is to make the business value obvious: automation plus controlled exceptions.

---

## 5. Product Explorer

### Layout

```text
┌───────────────────────────────────────────────────────────┐
│ Product: PDSH4816AF                     [PUBLISH READY]   │
├───────────────┬───────────────────────┬───────────────────┤
│ RAW INPUT     │ EVIDENCE              │ VALIDATION        │
│               │                       │                   │
│ MPN           │ Manufacturer page     │ ✓ Brand          │
│ Description   │ Technical PDF         │ ✓ LOV            │
│ Brand raw     │ Source snippets       │ ✓ UOM            │
│ Manufacturer  │                       │ ✓ Length         │
├───────────────┴───────────────────────┴───────────────────┤
│ ENRICHED PRODUCT                                         │
│ Manufacturer | Brand | Classpath | MPN                  │
│                                                           │
│ Attributes                                                │
│ Series = Professional Series     [source] [99%]         │
│ Wash Cycles = 5                   [source] [98%]         │
│ Sound Level = 47 dBA              [source] [99%]         │
│                                                           │
│ Commerce Content                                          │
│ Invoice Desc                                              │
│ Mobile Desc                                               │
│ Product Title                                             │
│ Long Description                                          │
└───────────────────────────────────────────────────────────┘
```

---

## 6. Evidence Drawer

Clicking a source icon opens:

```text
SOURCE
Manufacturer technical document

TITLE
Professional Series Dishwasher Specification

EVIDENCE
“Sound Level: 47 dBA”

USED FOR
Sound Level = 47 dBA

TRANSFORMATION
Raw text → numeric value + approved UOM

CONFIDENCE
0.99
```

This is the strongest trust mechanism in the product.

---

## 7. Field Confidence UI

Never use confidence alone as a colour or an unexplained percentage.

Use:

```text
98%  High
Source: Manufacturer PDF
Match: Exact
Rule: LOV-valid
```

For uncertain values:

```text
68%  Review
Source: Manufacturer page
Match: Partial
Conflict: 2 candidate values
Action: Review
```

---

## 8. Review Queue

Columns:

| Priority | Product | Field | Proposed | Reason | Evidence | Action |
|---|---|---|---|---|---|---|
| High | SKU-18 | Brand | BRAND A | 2 matches | Open | Review |
| High | SKU-31 | Material | Stainless Steel | source conflict | Open | Review |
| Medium | SKU-41 | Taxonomy | Fittings > ... | low score | Open | Review |

Priority formula:

```text
priority = business_impact × uncertainty × downstream_dependency
```

---

## 9. Comparison View

For the 200-item evaluation, provide:

```text
GROUND TRUTH           MODEL OUTPUT
------------------     ------------------
Brand = FRIGIDAIRE®    Brand = FRIGIDAIRE®     ✓
MPN = PDSH4816AF       MPN = PDSH4816AF        ✓
Class = ...            Class = ...             ✓
Sound = 47 dBA         Sound = 47 dBA          ✓
Title = ...            Title = ...             ✕ length
```

A toggle should switch between:

- exact match;
- normalised match;
- semantic match;
- rule failure.

---

## 10. Evaluation Dashboard

### Top section

```text
Field Accuracy     94.8%
LOV Compliance     98.7%
UOM Compliance     99.4%
Rule Compliance    96.2%
Evidence Coverage  96.2%
```

### Charts

1. field accuracy by field;
2. accuracy by category;
3. error distribution;
4. auto-approval vs review;
5. processing latency;
6. source authority distribution.

### Judge-friendly narrative

```text
Biggest improvement:
Manufacturer normalisation + LOV mapping reduced invalid categorical outputs by 73%.
```

Only display this when supported by measured runs.

---

## 11. Visual Language

### Statuses

Use consistent neutral UI with clear semantic status:

- success = validated;
- warning = review;
- error = blocking;
- neutral = unknown/not applicable.

Avoid excessive use of red/green alone; include icons/text for accessibility.

### Typography

- large, clear page title;
- compact table text;
- monospaced snippets for MPNs, codes, and rule values;
- readable long-description preview.

### Spacing

Use an 8px spacing scale. Keep cards compact enough to compare data without excessive scrolling.

---

## 12. Interaction Patterns

### Generate

Button label: `Enrich Product`

Substate labels:

```text
Resolving manufacturer…
Selecting taxonomy…
Retrieving evidence…
Extracting attributes…
Normalising values…
Building content…
Validating…
```

### Review

Use `Accept`, `Edit`, `Reject`, `Open Evidence`.

### Bulk run

`Run Batch` should show stage-level progress, not a generic spinner.

---

## 13. Error UX

Avoid:

> AI failed.

Prefer:

> **Brand resolution needs review**  
> Two approved brands matched the manufacturer. No automatic selection was made.

This turns failure into an explainable quality-control state.

---

## 14. Demo Mode

Provide a `Demo Mode` toggle that:

- loads a curated 3–5 item scenario;
- uses cached evidence;
- shows the complete pipeline in seconds;
- links the UI to the full 200-row evaluation page.

The demo must work without live internet.

---

## 15. Mobile / Responsive Behaviour

Desktop is primary because the workload is spreadsheet/data heavy. At narrower widths:

- stack evidence and output panels;
- pin validation summary to the top;
- collapse wide attribute tables into field cards;
- keep the review action bar sticky.

---

## 16. Accessibility

- keyboard navigation;
- status text in addition to colour;
- readable contrast;
- source links with descriptive labels;
- focus states;
- tooltips only for secondary information.

---

## 17. Microcopy

Prefer:

- `Validated against LOV`
- `Source confirmed`
- `Needs review`
- `Unsupported — omitted`
- `Normalised from manufacturer text`

Avoid:

- `AI confidence magic`
- `Probably correct`
- `Looks good`
- generic `Success` messages without explanation.

---

## 18. Signature UI Moment

The product should have one memorable interaction:

**Click an attribute → see the source sentence → see the normalisation mapping → see the generated field that consumed it.**

Example:

```text
"3/8 FNPT"
      │
      ▼
Fittings mapping
      │
      ▼
"Female NPT"
      │
      ▼
Product Title + Attribute
```

That single interaction communicates traceability, domain rules, and AI assistance better than a page of architecture diagrams.
