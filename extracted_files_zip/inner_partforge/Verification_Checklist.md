# Verification_Checklist.md — Fabricated & Placeholder Data Audit

**Purpose:** Every number, domain, LOV value, and threshold below was written by an AI drafting plausible-sounding content — none of it was measured against your real files. This is not a style pass; it's a list of specific claims that will not survive a judge asking "how did you get that number" unless you replace them with real output. Organized by severity, then by file, with the exact fix needed.

**How to use this:** Work top to bottom. Tier 0 is a single action that fixes ~60% of the risk in the whole doc set. Tiers 1–4 are ordered by how badly it would go if a judge caught it, not by how easy the fix is.

---

## Tier 0 — The one fix that matters most

**Every number in `Evaluation.md` §3 (the benchmark scorecard) and every number in `Demo.md`'s Act 4 / Q&A section is invented.** Nothing in this project has actually been run against the 200-item ground truth yet. Until you:

1. Build even a minimal version of the pipeline (rules engine alone is enough for a first pass — classification/description can come later),
2. Run it against `Unilog-Sample_200_Items-Input-vs-Output.xlsx`,
3. Regenerate the scorecard from real output using something like the `eval/run_eval.py` sketch in `Evaluation.md` §5,

...**every accuracy claim in this submission is fiction presented as fact.** This is the single highest-risk item in the entire package — worse than any individual placeholder below — because it's not a missing detail, it's a fabricated result. Do this before polishing anything else.

---

## Tier 1 — CRITICAL: specific results/counts stated as measured fact

| # | File · Location | What's written | Why it's a problem | Fix |
|---|---|---|---|---|
| 1 | `Evaluation.md` §3, entire scorecard table | 15 rows of specific accuracy numbers (98.5%, 99.4%, 100.0%, 96.5%, etc.) with denominators like `197/200`, `1,988/2,000` | These read as *reported test results*. They are not — no test was run. This is the item most likely to end a Q&A badly. | Delete the table. Re-populate every cell only after running `run_eval.py` against real predictions. Until then, leave cells as `TBD` or remove the table and say "benchmark harness built, results below reflect our actual run" — never a placeholder dressed as a result. |
| 2 | `Evaluation.md` §3, "Baseline / Naive LLM" column | Numbers like 71.4%, 48.0%, 62.1% presented as if a comparison baseline was actually built and tested | Doubly fabricated — a comparison run against a baseline system that doesn't exist | Either actually build and run a naive-prompt baseline for comparison (strong if you have time — it's a great slide), or remove the column entirely. Do not keep invented baseline numbers. |
| 3 | `Evaluation.md` §4 / `Demo.md` Q3 answer | "4 rows with blank UNSPSC," "18 rows with missing country-of-origin," a specific mismatch at "**Row 87**" | The original brief only says *"blank UNSPSC and country-of-origin cells... at least one row"* — it never gives counts or a row number. These specifics are invented and are exactly the kind of thing a judge who has the same spreadsheet open will catch instantly. | Open the real 200-item Delivery Format sheet, `COUNTIF`/filter for blank UNSPSC and blank country-of-origin, and get the real counts. Manually find the actual mismatched row and cite its real row number. |
| 4 | `AI_Strategy.md` §5 | "completing 1,000 items in **<15 minutes** for $0.00" | Untested throughput claim stated as if benchmarked | Actually time a real batch run once the pipeline exists, or soften to "designed to process 1,000 items within free-tier rate limits — see Phases.md for the timed run" until you have a real number. |
| 5 | `Design.md` §2 header | Filename `Unihack_ Expected Output - Delivery Format.csv` | This filename does not appear anywhere in your original organizer brief (which names `Unilog-Sample_200_Items-Input-vs-Output.xlsx` as the ground-truth file). Citing a file that may not exist is worse than citing nothing. | Confirm whether this file is actually in your organizer-provided dataset pack. If not, delete the reference. If it is a real file you have, keep it — but verify the name character-for-character (the stray leading space in `"Unihack_ Expected..."` looks like a copy-paste artifact worth double-checking). |

---

## Tier 2 — HIGH: invented domain-specific values that must be replaced with real reference-data values

These aren't "wrong," they're *placeholders that look like real extracted data*. That's the dangerous part — a reader can't tell they're invented without checking your actual files.

| # | File · Location | What's written | Fix |
|---|---|---|---|
| 6 | `Rules.md` §8 (SRC-01) | OEM domain allowlist: `*.frigidaire.com`, `*.moen.com`, `*.parker.com` | Build the real allowlist from the actual manufacturer names in `UniCat_Manufacturer_and_Brand_List.xlsx` — 27,000+ rows means this needs a programmatic domain-derivation step (manufacturer name → likely domain, human-verified for the ones you'll actually demo), not three hand-picked examples. |
| 7 | `Rules.md` §7.1 | Faucets controlled vocabulary lists — `Mounting Type`, `Valve Core Type`, `Finish` values, UNSPSC `30181702` | Every one of these must be read directly off `FAUCETS_LOV.xlsx`'s Attribute Detail and Summary sheets. The values shown (Chrome/Brushed Nickel/Matte Black, Ceramic Disc/Ball Valve/Cartridge, etc.) are plausible industry-standard terms, not verified against your actual file — and the UNSPSC code is a guess. |
| 8 | `Rules.md` §7.2 | Sample of 9 fitting types (Coupling, Elbow 90°, Tee, Union...) out of the real 390; connection-type examples (`MIP x FIP`, `NPT x NPT`...); material examples (BRS→Brass, SST→Stainless Steel...) | These are plausible trade terms but presented as if pulled from the real 390-type list and the 1,472→515 / 464→113 mapping tables. Cross-check each example actually appears in `Fittings_LOV.xlsx` before keeping it in the doc. |
| 9 | `Rules.md` §4.2 | UOM abbreviation reference table — ~10 measurement categories with specific approved forms (`dBA`, `V`, `A`, `Hz`, `deg F`, `kW-hr`) | The real file has ~500 abbreviations across 89 measurement types. Even something as basic as whether temperature is written `deg F`, `°F`, or `F` needs to be read off the actual Sheet 1 — don't assume the plausible-looking form is the approved one. |
| 10 | `Design.md` §2 | The entire 252-column range breakdown (Cols 1–7 System Identifiers, 8–23 Taxonomy, 56–205 "50 Dynamic Attribute Triples," etc.) with specific invented column names (`MFR URL`, `Ref URL 1`...`5`, `ITEM_FEATURES_1`...`20`) | This entire table is a structural guess. Open the real Delivery Format sheet, list the actual 252 header names in order, and rebuild this table from what's really there — including the real max attribute count (the doc guesses 50; count it). |
| 11 | `Demo.md` §3.1–3.2 | Case-study examples: Parker Hannifin fitting resolution, Moen 8277 faucet with specific gpm/finish/valve values | Verify these MPNs actually exist in your 1,000-item or 200-item files, and that the "before/after" shown is what your real pipeline actually produces for them — not an illustrative mock-up presented as a case study. If the MPN isn't in your data, either pick a real row or clearly label the example as illustrative, not a pipeline output. |

---

## Tier 3 — MEDIUM: unvalidated thresholds and parameters presented as tuned

These are reasonable starting guesses for engineering constants, but they're written with a confidence that implies they were tuned against real data. They weren't.

| # | File · Location | What's written | Fix |
|---|---|---|---|
| 12 | `Rules.md` MB-01, MB-04 | Fuzzy-match threshold `≥0.88`, ambiguity margin `<0.05` | Arbitrary until you run real fuzzy-matching against the 27K manufacturer list and check where false positives/negatives actually start appearing. Treat as a tunable config value, not a fixed spec. |
| 13 | `Validation.md` §3 | Confidence formula weights `w1=0.20, w2=0.20, w3=0.40, w4=0.20` | No evidence these weights were derived from anything — they're a clean-looking guess. Fine as a v1 default, but say so ("initial weights, to be calibrated against manual audit results") rather than presenting as settled. |
| 14 | `Validation.md` §2.5 (Rule 5.2) | Physical outlier thresholds: Faucet flow rate `>5.0 gpm`, dishwasher sound level `<30 or >70 dBA`, voltage enum `{12,24,120,208,240,277,480}` | These aren't sourced from the Content Guidelines — they're invented domain plausibility bounds. If wrong, they'll incorrectly flag valid real values as anomalies. Verify against the actual guideline doc or real ground-truth value ranges before trusting them to gate anything. |
| 15 | `Validation.md` §4 | Auto-repair abbreviation examples: `DISHWASHER→DISHW`, `STAINLESS STEEL→SST` | Invented abbreviation choices. Check the Content Guidelines' own house-style/abbreviation rules (Sheet 2 of the UOM file has 22 house-style rules — there may be existing approved abbreviations) before inventing new truncation logic that could itself violate a rule. |
| 16 | `Rules.md` PH-01 | Extra placeholder strings beyond the brief's three: `Unbranded`, `Generic`, `None`, `N/A`, `NA`, `TBD`, `Blank` | The original brief names exactly three placeholder strings. These additions are reasonable guesses but risk false positives — e.g., nulling out a real manufacturer literally named something containing "NA." Check whether these patterns actually appear in your real data before hard-coding them as null-triggers. |
| 17 | `AI_Strategy.md` §2 | Rate limits stated as current fact: Groq "30 RPM / 14,400 RPD," Gemini "15 RPM / 1,500 RPD," OpenRouter "200 RPD"; model IDs `llama-3.3-70b-versatile`, `gemini-2.5-flash` | Free-tier limits and model availability change frequently and are provider-controlled, not something this doc can guarantee. Re-verify directly against each provider's current docs immediately before the event — don't trust a doc written weeks earlier. |
| 18 | `AI_Strategy.md` §1 | Workload routing split "85% local / 12% cloud LLM / 3% multimodal" | Presented as an outcome, but it's a target/assumption with no measurement behind it yet. Once you run the 1,000-item batch, report the real split. |

---

## Tier 4 — LOW: minor/cosmetic, low risk but easy to fix

| # | File · Location | What's written | Fix |
|---|---|---|---|
| 19 | `Demo.md` §5, Judges' Rubric Alignment Matrix | Weights 25%/25%/20%/15%/15% presented as "the" rubric | This is your own internal framing of what you think matters, not Unilog/Hack2Skill's actual published rubric (which you likely don't have visibility into). Fine to keep as "how we think about our own strengths," but don't present it as if it's the organizers' real scoring weights. |
| 20 | `Demo.md` Act 2/Act 4 | "Trie speed benchmarks (<0.5ms)" | Untested performance claim. Either benchmark it for real (it's a cheap thing to actually measure) or drop the specific number and say "sub-millisecond lookups by design." |
| 21 | `Architecture.md` §3 | Evidence graph example cites "Cut-Sheet: PDSH4816AF.pdf, Page 2" | No real cut-sheet was fetched for this illustrative example — the page number is invented. Fine for a conceptual diagram, but don't let it get quoted later as if it were a real citation. |
| 22 | `Evaluation.md` §5, `BenchmarkEvaluator` code | Column names referenced in code: `INVOICE_DESC`, `MOBILE_DESC`, `MANUFACTURER_NAME`, `BRAND_NAME`, `UNSPSC`, `Classpath` | Verify these exact strings (case, underscores, spacing) match your real Delivery Format headers — a mismatched column name will silently break the eval script rather than error loudly, since `pandas` will just return `NaN`/missing-column behavior. |
| 23 | `Phases.md` §1, Gantt chart | "36–48 Hour Sprint" and specific hour blocks | Confirm against the actual published event schedule; re-anchor hour labels once you know it, per my note in the original doc. |

---

## Quick pass: what's actually fine to keep as-is

To be clear about what *isn't* on this list — these are legitimately grounded in your organizer brief and don't need touching:

- The dishwasher worked example (`PDSH4816AF`, FRIGIDAIRE®, CleanBoost™, `50-1/4 in`) — this is verbatim from your uploaded brief, safe to keep everywhere it appears.
- The dataset-scale facts (27,000+ manufacturer rows, ~161,000 LOV rows, ~500 UOM abbreviations/89 types, 63 fraction entries, 390 fitting types, 1,472→515 connection variants, 464→113 material variants) — these are all stated directly in your organizer materials.
- The general rule *structure* (placeholder handling, precedence hierarchy, 5-format description building, sourcing hierarchy) — the architecture of the rules is sound; it's specific invented values slotted into that structure that need replacing.

---

## Note on `PRD.md`

Your upload list included `PRD.md`, but its content wasn't actually passed to me in this message — only the other eight files came through. I haven't been able to audit it for the same issues. If you'd like it checked, re-share its content (or re-upload) and I'll run the same pass against it — given the pattern in the other eight files, it likely has at least a few benchmark-style claims worth checking too.

---

## Suggested verification workflow

1. Open the real `Unilog-Sample_200_Items-Input-vs-Output.xlsx` and `FAUCETS_LOV.xlsx` / `Fittings_LOV.xlsx` side by side with this checklist.
2. Work Tier 1 first — these are the load-bearing credibility risks.
3. For Tier 2, do a find-and-replace pass: every invented domain/LOV value gets swapped for the real one, or explicitly marked `[VERIFY AGAINST FILE]` if you haven't gotten to it yet — an honest placeholder tag is infinitely safer than a confident-looking guess.
4. Tier 3/4 can wait until after you have a working pipeline producing real numbers to tune against.
5. Re-run this same audit mentally on any new content you or the AI adds from here — the failure pattern is consistent: specific-sounding numbers and lists are the tell, whether or not they're actually verified.
