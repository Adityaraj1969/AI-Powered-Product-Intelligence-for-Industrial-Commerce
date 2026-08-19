# UniHack — Demo

## 1. Demo Objective

The demo must convince judges of four things in order:

1. the input is genuinely messy;
2. the system performs real product intelligence, not superficial text generation;
3. every important result is constrained and traceable;
4. the approach scales beyond a hand-picked example.

The organiser specifically recommends depth over breadth and encourages demonstrating a fully specified category such as Faucets or Fittings. citeturn154558view1

---

## 2. Recommended Demo Arc

### Act 1 — The mess

Show one raw row.

```text
MPN:        PDSH4816AF
Part Desc:  Dishwasher SS - Display Only
Brand:      -- Unbranded --
```

Say:

> "This is the kind of row a catalogue team receives. It is short, ambiguous, and nowhere near commerce-ready."

Do not spend time reading the spreadsheet.

---

## 3. Act 2 — One-click enrichment

Click:

**Enrich Product**

Show stage progress:

```text
✓ Cleaned input
✓ Resolved manufacturer
✓ Selected taxonomy
✓ Retrieved manufacturer evidence
✓ Extracted attributes
✓ Normalised UOM + LOV
✓ Built commerce content
✓ Validated output
```

The interface should make the process feel orchestrated, not like several disconnected scripts.

---

## 4. Act 3 — The evidence moment

Open one important attribute.

Example:

```text
Sound Level
47 dBA

Evidence
Manufacturer specification document
"Sound Level: 47 dBA"

Transformation
raw text → numeric value 47 + UOM dBA

Validation
✓ approved UOM
✓ source linked
✓ description consistent
```

This is where the judges should realise the system is not simply guessing.

---

## 5. Act 4 — The normalisation moment

Use a Fittings example where many source expressions map to one canonical value.

```text
RAW
3/8 Female National Pipe Thread

NORMALISER
Fittings LOV

CANONICAL
Female NPT

USED IN
Attribute
Product Title
Search Filter
```

The organiser explicitly highlights Fittings as a strong example of many-to-one normalisation across connection types and materials. citeturn154558view1

---

## 6. Act 5 — The validator catches a mistake

This is essential for credibility.

Intentionally create a controlled failure in demo data or replay mode:

```text
Generated:
50.25in

Validator:
✕ UOM formatting violation

Repair:
50.25in → 50-1/4 in

Result:
✓ compliant
```

Do not fabricate an organiser ground-truth error. The demo should use a deliberately injected test mutation or a real controlled perturbation outside the benchmark result.

---

## 7. Act 6 — Human review

Show one ambiguous manufacturer/brand case.

```text
Confidence: 0.71
Reason: two approved candidates

[Approve Candidate A]
[Choose Candidate B]
[Open Evidence]
```

Click `Open Evidence`, show the source, then approve.

Say:

> "We do not force the model to be confident. Uncertainty becomes a work queue."

---

## 8. Act 7 — Ground Truth

Switch to the 200-row evaluation dashboard.

Show:

```text
200 labelled products
────────────────────
Field accuracy       XX.X%
LOV compliance       XX.X%
UOM compliance       XX.X%
Rule compliance      XX.X%
Evidence coverage    XX.X%
Safe auto-approval   XX.X%
```

Then open a row comparison.

The organiser explicitly identifies this workbook as the labelled ground truth and suggests field-level accuracy, character compliance, and LOV coverage as evaluation evidence. citeturn154558view1

---

## 9. Act 8 — Scale

Show the 1,000-row run:

```text
1,000 / 1,000 processed
XX.X% publish-ready
XX.X% review
XX.X% failed/retry

Average latency: XX s/item
```

Then show a small error Pareto:

```text
Top errors
1. taxonomy ambiguity
2. missing manufacturer evidence
3. ambiguous LOV mapping
4. source conflict
5. parsing anomalies
```

The story is **controlled scale**, not "one perfect product."

---

## 10. Closing Slide

### Headline

**From sparse rows to trusted product intelligence.**

### Three proof points

```text
AI reasoning
+ controlled product knowledge
+ deterministic validation

= commerce-ready catalogue at scale
```

### Final sentence

> "Our innovation is not that an LLM can write product copy. It is that the entire path from messy input to publishable product intelligence is evidence-backed, vocabulary-constrained, and measurable."

---

## 11. 5-Minute Demo Script

### 0:00–0:30 — Problem

"Industrial commerce starts with product data that is often incomplete and inconsistent. The organiser's own sample demonstrates how a short raw row expands into hundreds of structured delivery fields governed by rules, vocabularies, and sourcing constraints." citeturn154558view1

### 0:30–1:15 — Raw input

Show raw item and placeholders.

"We clean placeholders, resolve identity, and decide what we actually know."

### 1:15–2:15 — AI enrichment

Run the orchestrator.

Show evidence and one structured attribute.

### 2:15–3:00 — Normalisation + generation

Show a canonical LOV mapping and the generated title/long description.

### 3:00–3:40 — Validation

Show an injected UOM/style failure, automatic deterministic repair, and publish gate.

### 3:40–4:30 — Ground truth

Show 200-row metrics and error breakdown.

### 4:30–5:00 — Scale + close

Show 1,000-row results, review queue, and final architecture principle.

---

## 12. Judge Questions We Should Be Ready For

### "Why do you need an LLM?"

Because extraction, interpretation, ambiguity resolution, and channel-specific language are language-heavy. We deliberately keep deterministic tasks out of the LLM.

### "How do you stop hallucinations?"

Evidence gate + controlled vocabulary + deterministic validation + provenance + human review.

### "Why RAG?"

Product-specific technical facts must be grounded in authoritative sources rather than model memory.

### "Why not use a knowledge graph?"

We do use graph-shaped evidence internally, but a relational evidence store is faster to deploy. The model is compatible with a future graph database without changing the core data model.

### "How is this different from a generic RAG chatbot?"

A chatbot returns answers. UniHack produces a **schema-valid, vocabulary-constrained, commerce-ready product record** and proves where each important value came from.

### "What happens when there is no manufacturer source?"

The system marks fields unknown/review rather than fabricating them. It can still preserve reliable input facts and partial enrichment.

### "Can it scale?"

Yes, because the expensive AI/retrieval steps are cached/batched, while lookups and validation are deterministic and highly parallelisable.

### "What did you choose not to build?"

We prioritised a complete, measurable enrichment slice over a shallow attempt at every capability, consistent with the organiser's guidance. citeturn154558view1

---

## 13. Demo Failure-Proofing

### Must work offline

- cache all demo sources;
- pre-index organiser files;
- use deterministic benchmark data;
- keep one local model/fallback or replay response set.

### Must have a fallback path

If live enrichment fails:

```text
Live mode → Cached evidence mode → Recorded demo mode
```

The UI should make this operational fallback invisible to the judge unless disclosed during Q&A.

### Keep three golden products

1. easy/high-confidence;
2. technically rich;
3. ambiguous/needs-review.

The third item is especially useful because it proves the system knows when not to guess.

---

## 14. Pre-Demo Checklist

- [ ] 200-row benchmark frozen and reproducible.
- [ ] 1,000-row batch run completed.
- [ ] Metrics match exported report.
- [ ] Demo sources cached.
- [ ] No API keys in repository.
- [ ] Review queue has one believable ambiguity.
- [ ] Intentional validator failure is clearly labelled as a test mutation.
- [ ] Export file generated.
- [ ] Architecture diagram matches implementation.
- [ ] All claimed metrics can be reproduced.

---

## 15. The One Screenshot Judges Should Remember

The strongest single screenshot is a product detail page with four simultaneous panels:

```text
RAW INPUT | MANUFACTURER EVIDENCE | GENERATED PRODUCT | VALIDATION
```

A product row on the left, the exact source evidence in the centre, the commerce-ready record on the right, and a green/amber validation rail showing each rule passed or failed.

That visual communicates the entire product in one frame.
