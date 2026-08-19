# Verification Checklist & Integrity Audit (`Verification_Checklist.md`)

**Project:** **PartForge** — AI-Powered Product Intelligence Pipeline for Industrial Commerce  
**Hackathon:** UniHack 2026 · Unilog × Hack2Skill  
**Purpose:** Pre-submission verification checklist ensuring all claims, schemas, and metrics are mathematically verified, traceable to real dataset files, and defendable before the judging panel.

---

## 1. Ground Truth & Dataset Verification Matrix

| Dataset Item | Ground Truth Reference File | Verified State & Inspection Result | Status |
| :--- | :--- | :--- | :--- |
| **Input Schema** | `Unihack_ Sample Dataset - Input.csv` / `Sample-1000_Items.xlsx` | 1,000 rows, exactly 6 columns: `Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`. | ✅ Verified |
| **Delivery Schema** | `Unihack_ Expected Output - Delivery Format.csv` / `Unilog-Sample_200_Items-Input-vs-Output.xlsx` | Exactly 252 columns, including 50 Attribute Triples (Cols 56–205), System Keys (Cols 1–7), Brand & Taxonomy (Cols 8–23), 5-Channel Copy (Cols 24–29), Dimensions (Cols 215–224), and Digital Assets (Cols 225–252). | ✅ Verified |
| **Placeholder Strings** | Official Organizer Brief | Exactly 3 official placeholders: `-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`. Config-driven regex for heuristic candidate discovery. | ✅ Verified |
| **Controlled Vocabularies** | `UniCat_Manufacturer_and_Brand_List.xlsx` | 27,000+ canonical manufacturer/brand rows with legal casing, suffixes (`Inc.`, `LLC`), and trademark symbols (`®`, `™`). | ✅ Verified |
| **Attribute LOV** | `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx` | ~161,000 cross-category rows: `Classpath -> Leaf Node -> Attribute Label -> Normalized Values`. | ✅ Verified |
| **Master UOMs** | `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx` | 89 measurement categories, ~500 approved abbreviations, 22 house-style rules, mandatory single-space rule (`24 in`). | ✅ Verified |
| **Fractional Matrix** | `Decimal_Fraction.xlsx` | 63 exact 64th fraction-to-decimal lookup pairs ($1/64$ to $63/64$), compound format (`50.25` $\rightarrow$ `50-1/4 in`). | ✅ Verified |
| **Category LOVs** | `FAUCETS_LOV.xlsx` & `Fittings_LOV.xlsx` | Faucets build order & controlled enums; Fittings 390 types, 1,472 $\rightarrow$ 515 connection types, 464 $\rightarrow$ 113 materials. | ✅ Verified |

---

## 2. Integrity Audit by Severity Tier

### Tier 0 & Tier 1: Benchmark Reporting & Metrics Integrity
* [x] **Target SLA vs. Live Execution Framing**: Scorecards in `Evaluation.md` and `PRD.md` clearly distinguish between **Target SLA Acceptance Gates** (the engineering success criteria) and live test runs produced by `eval/run_eval.py`.
* [x] **Exact Column Name Parity**: All python code, evaluators, and schema models reference the verbatim 252 delivery headers (`INVOICE_DESC`, `MOBILE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `MANUFACTURER_NAME`, `BRAND_NAME`, `Classpath`, `ATTRIBUTE_LABEL 1`, `ATTRIBUTE_VALUE 1`, `ATTRIBUTE_UOM 1`).
* [x] **Zero Fabricated Baseline Numbers**: Comparison baselines are framed around standard heuristic/naive LLM failure modes rather than unverified test runs.

### Tier 2: Domain Values & Controlled Vocabularies
* [x] **OEM Whitelisting Hierarchy**: Domain whitelisting is programmatically derived from `UniCat_Manufacturer_and_Brand_List.xlsx` with explicit blocking of consumer marketplaces (Amazon, eBay).
* [x] **Faucets & Fittings LOV Mapping**: Extraction targets strictly conform to `FAUCETS_LOV.xlsx` and `Fittings_LOV.xlsx` reference structures.
* [x] **Compound Fractional Sizing**: Inch conversions strictly follow the 64th table with hyphenated compound notation (`50-1/4 in`).

### Tier 3: Configurable Parameters & Weights
* [x] **Confidence Calibration Weights**: Explicitly stated as initial configurable weights ($w_1=0.20, w_2=0.20, w_3=0.40, w_4=0.20$) subject to empirical calibration.
* [x] **Fuzzy Match Thresholds**: RapidFuzz threshold ($\ge 0.88$) and ambiguity margin ($0.05$) framed as tunable configuration parameters.
* [x] **Free Tier Rate Limits**: Documented against current provider caps (Groq: 30 RPM; Google AI Studio: 15 RPM; Local Ollama: Unlimited).

---

## 3. Pre-Pitch Verification Checklist

- [x] **Dataset Paths Checked**: `Unihack_ Sample Dataset - Input.csv` and `Unihack_ Expected Output - Delivery Format.csv` located and validated.
- [x] **252 Delivery Columns Indexed**: Verified that 50 attribute triples = 150 columns (Cols 56–205).
- [x] **Free AI Stack Verified**: FastEmbed (local CPU) + Groq Free API / Local Ollama wrapper ready.
- [x] **100% Space & Casing Rules Enforced**: Invoice $\le 40$ chars ALL CAPS, Mobile $60\text{--}80$ chars, Title $\le 150$ chars, `24 in` space rule.
- [x] **Evaluation Runner Standalone**: `eval/run_eval.py` runnable with single CLI command.
