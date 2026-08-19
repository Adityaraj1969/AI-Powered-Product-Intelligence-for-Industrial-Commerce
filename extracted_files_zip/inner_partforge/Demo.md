# Demo.md — Judge Presentation & Demo Script

**Project:** PartForge · UniHack 2026 (Unilog × Hack2Skill)
**Purpose:** the exact script, timing, and fallback plan for presenting to judges. Timing blocks below assume a **7-minute pitch + 3-minute Q&A** slot — a common Hack2Skill grand-finale format. Rescale proportionally to whatever slot length is actually announced; do not add content, compress delivery instead.

---

## 1. The One-Sentence Pitch

> "PartForge turns a six-word, abbreviated catalog row into a fully classified, controlled-vocabulary, five-format product record — and shows its work on every single field, so nothing is ever invented and nothing is ever silently wrong."

Use this verbatim as the opening line. It contains the three things judges are scoring: the transformation (input→output), the grounding (controlled vocabulary, "shows its work"), and the honesty (nothing silently wrong).

---

## 2. Pitch Structure (7 minutes)

| Time | Section | Content |
|---|---|---|
| 0:00–0:45 | **The problem, in one row** | Show the raw dishwasher row (`PDSH4816AF Dishwasher SS - Display Only`, brand = `-- Unbranded --`) on screen. State the business problem: this happens across catalogs with hundreds of thousands of rows, and the output has to be constrained to approved values, not fluent guessing. |
| 0:45–1:15 | **Why this is hard** | One line: "The output is constrained, not creative — a fluent description built from invented values is a failure, not a success." This is a direct quote from the brief and signals to judges we understood the actual hard part of the problem, not just "call an LLM." |
| 1:15–1:45 | **Our scope decision** | "Rather than a shallow pass over all eight stages, we went deep on classification, extraction, normalization, and description building for two fully-specified categories — Faucets and Fittings — and ran normalization and classification at volume across all 1,000 items. Depth beats breadth, and we can prove the depth." |
| 1:45–4:30 | **Live demo** | See §3 below — this is the core of the pitch |
| 4:30–5:45 | **The numbers** | Switch to the Metrics Dashboard. State 3–4 headline numbers with their denominators (e.g., "94% LOV compliance — 376 of 400 attribute values" not just "94%"). Explicitly show the honest gaps too (coverage on the 1,000-item set, known ground-truth artifacts) — this is a deliberate credibility move. |
| 5:45–6:30 | **Architecture in 30 seconds** | One diagram slide: raw row → deterministic normalization (tables) + LLM (constrained, tool-calling) → validation gate → published or flagged. Say explicitly: "Every generated value passes through a validator that checks it against the actual controlled vocabulary before it's allowed into the record — the model proposes, the data disposes." |
| 6:30–7:00 | **Close + roadmap** | "This is a working pipeline against Unilog's own ground truth, not a mockup. Next: digital assets, full-catalog classification, and a production crawler — all scoped in our roadmap doc." Land on the one-sentence pitch again. |

---

## 3. Live Demo Flow (Screen-by-Screen)

**Golden rule: never demo on hope.** Every step below has been run and re-run in rehearsal (`Phases.md` Phase 6) before it is shown live.

### Step 1 — Overview screen (15 sec)
Land here first. Point at the three KPI cards. Say: "These are computed live from this run, not hardcoded."

### Step 2 — Pipeline Run screen: the dishwasher example (90 sec)
Walk the animated stepper stage by stage:
1. **Input Analysis** — show the raw `Part_Desc` string and the placeholder brand field getting nulled.
2. **Classification** — show the top-3 candidate classpaths and why the winning one was selected (retrieval score + LLM reasoning).
3. **Attribute Extraction** — click one attribute (e.g., Sound Level = 47 dBA), show its `evidence_span` highlighted in the source text.
4. **Normalization** — show `50.25 in` becoming `50-1/4 in` live, and name the source: "this came from a 63-row lookup table, not the model doing arithmetic."
5. **Description Building** — show the five formats appear side by side: Invoice (CAPS, ≤40), Mobile, Title, Long, Marketing. Point out the character counters turning green.
6. **Digital Assets** — point at the greyed-out stage card. Say directly: "We scoped this out — it's in our roadmap doc, not hidden." (This single sentence does more for credibility than trying to fake this stage.)

### Step 3 — Record Inspector: flip on "Show ground-truth" (45 sec)
Switch to a Faucet or Fitting record from the 200-item set. Toggle **"Show ground-truth expected value."** Let the green/red match indicators appear live next to each field. Say: "This toggle works for all 200 ground-truth items — we're not cherry-picking the one example that works."

### Step 4 — Review Queue (30 sec)
Show a flagged record. Open its `review_reason`. Say: "When we can't confidently resolve a value, we don't guess — we flag it, and here's exactly why." Click approve/edit to show the loop is real, not decorative.

### Step 5 — Metrics Dashboard (45 sec)
Show the scorecard grid. Click into one metric's drill-down (e.g., LOV compliance) to show the failing records list. Say: "We show you where we're wrong, not just where we're right."

**Total live-demo time target: ~3.5–4 minutes**, leaving buffer inside the 7-minute slot for a slower delivery or a recovered hiccup.

---

## 4. Before/After Showcase Slide (for the deck, not necessarily spoken)

| | Before | After |
|---|---|---|
| Description | `PDSH4816AF Dishwasher SS - Display Only` | 5 separate, formula-correct, character-compliant formats — see `Rules.md` §9 |
| Brand | `-- Unbranded --` (placeholder) | `FRIGIDAIRE®` (canonical, symbol-exact) |
| Measurement | `50.25 in` (if published as decimal) | `50-1/4 in` (trade-fraction form) |
| Classification | none | `Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers` |
| Trust | Analyst has to verify everything by hand | Every field carries its source and a confidence score |

---

## 5. Pitch Deck Structure

1. Title slide — project name, one-sentence pitch, team
2. The problem — the raw row, stated plainly
3. Why it's hard — constrained not creative, controlled vocabularies at scale (27K manufacturers, 161K LOV rows)
4. Our scope decision — depth on Faucets/Fittings + volume run, explicit non-goals
5. Architecture — one clean diagram (adapt from `Architecture.md` §2)
6. **Live demo** (or the backup video, see §6)
7. The numbers — metrics with denominators
8. Grounding strategy — the four-layer anti-hallucination approach (`AI_Strategy.md` §5), because judges scoring "AI agents, RAG, explainability" will specifically look for this
9. Roadmap — what's next, scoped honestly
10. Close — one-sentence pitch, repeated

---

## 6. Backup Plan

- A **screen-recorded video** of the exact live-demo flow (§3) is prepared in advance and ready to play instantly if live software, network, or API access fails during the slot.
- If only the manufacturer-source enrichment step fails live (most likely single point of failure, since it depends on external network access), skip directly to Normalization — the script in §3 is written so each stage can be individually skipped without breaking the narrative.
- A static, annotated screenshot set of all 5 UI screens exists in the deck as slide 6b, usable if the live environment is entirely unavailable.

---

## 7. Anticipated Judge Questions

| Likely question | Prepared answer |
|---|---|
| "How do you know it's not just hallucinating fluently?" | Point directly to the four-layer grounding chain in `AI_Strategy.md` §5: schema-level constraint, evidence-span requirement, post-generation validator gate, tool-layer source enforcement. Offer to open the Record Inspector and show a specific field's provenance live. |
| "Why only two categories in depth?" | "Faucets and Fittings are the only categories fully specified end-to-end in the reference pack — going deep there, with reproducible ground-truth scoring, beats a shallow, unmeasurable pass over everything. We still ran classification and normalization across all 1,000 items to prove the pattern scales." |
| "What happens when it's wrong?" | Open the Review Queue live. "It doesn't silently publish a wrong value — it flags it with a specific reason and routes to a human." |
| "How would this scale to a real catalog?" | Point to `Architecture.md` §7 (scalability path) — stateless workers, managed vector DB, crawler with rate limits — and be honest that the hackathon build demonstrates the pattern on a bounded sample, not production throughput. |
| "What's your accuracy, really?" | State the actual numbers from the last `eval_report.json` run, with denominators, not a rounded-up soundbite. If a number is weaker than we'd like, say so and explain the plan (`Phases.md` roadmap) rather than deflecting. |
| "Why didn't you build digital assets?" | "We scoped it out deliberately, per our own PRD — we'd rather show four stages done rigorously than eight stages done shallowly. It's fully specced in our roadmap." |
| "What LLM / stack did you use and why?" | Reference `AI_Strategy.md` §2 — model choice by role (reasoning/extraction vs. embeddings), and the provider-agnostic interface that made the choice swappable. |

---

## 8. Delivery Tips

- **Lead with the messy input, every time.** The single most persuasive visual in this entire project is a genuinely ugly six-word string next to a clean, correct, five-format output. Don't bury it under architecture talk — open with it.
- **Say the word "flagged" out loud at least once.** A pipeline that never shows a failure case reads as either untested or dishonest to an experienced judge; showing the Review Queue for even 20 seconds does more for credibility than another accuracy number.
- **Never round a metric up in speech beyond what's on screen.** If the dashboard says 87%, say 87%, not "around 90%."
- **Keep one team member solely on timing** during rehearsal and the live pitch — with a 7-minute slot, the live demo (§3) is the section most likely to overrun, and it's the section most tightly rehearsed for exactly that reason.

---

**Related documents:** `PRD.md` · `Architecture.md` · `Rules.md` · `Design.md` · `Phases.md` · `Evaluation.md` · `AI_Strategy.md` · `Validation.md`
