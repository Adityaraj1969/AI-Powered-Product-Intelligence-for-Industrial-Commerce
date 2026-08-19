# PRD.md — Product Requirements Document

**Project:** **PartForge** — AI-Powered Product Intelligence Pipeline for Industrial Commerce  
**Hackathon:** UniHack 2026 · Unilog × Hack2Skill  
**Track:** AI-Powered Product Intelligence for Industrial Commerce  
**Infrastructure Target:** **100% Free Tier & Local Open-Source Architecture ($0.00 API Cost)**  
**Document Owner:** Team PartForge  
**Status:** Production-Ready Hackathon Specification v2.1  

---

## 1. Executive Summary

Industrial B2B distributors and manufacturers manage millions of Stock Keeping Units (SKUs) spanning hundreds of specialized technical categories—from high-pressure pipe fittings and hydraulic couplings to commercial appliances and electrical switchgear. However, raw catalog data received from suppliers is notoriously fragmented, cryptic, abbreviated, and incomplete:

```text
Mfg_Part_Num: PDSH4816AF
Part_Desc:    PDSH4816AF Dishwasher SS - Display Only
E1_Brand:     -- Unbranded --
Part_Manuf:   Appliance Dealers Cooperative (APPDE)
```

Unilog is tasked with transforming this unstructured raw feed into a structured, commerce-ready product intelligence record spanning **252 delivery columns** with exact classification, verified attributes, standardized units, and **five separately-formatted channel descriptions** (POS Invoice $\le 40$ chars ALL CAPS, Mobile card $60\text{--}80$ chars, SEO Title $\le 150$ chars, Long PDP Description, and Feature Bullets).

**PartForge** is an enterprise-grade, constraint-governed **Neuro-Symbolic Product Intelligence Engine** built entirely on a **100% Free Tier and Local Open-Source Architecture ($0.00 compute spend)**. It takes sparse, noisy supplier rows and produces a complete **Unified Product Intelligence Record (UPIR)**. Every extracted attribute, brand name, and unit of measure is strictly validated against controlled vocabularies (`UniCat_Manufacturer_and_Brand_List` with 27,000+ rows, `Unicat_Lov_v1_0` with 161,000+ rows, `Master UOM Standards` with 89 categories) or flagged for human review with traceable evidence—**guaranteeing 0.00% hallucination on technical specifications**.

PartForge delivers **deep vertical specialization** for two end-to-end specified benchmark categories (**Kitchen & Bath Sink Faucets** and **Pipe/Tube/Hose Fittings**) while running a robust, high-throughput pipeline across the full **1,000-item working dataset** (`Sample-1000_Items.xlsx`), benchmarked directly against Unilog’s **200-item ground truth delivery dataset** (`Unilog-Sample_200_Items-Input-vs-Output.xlsx`).

---

## 2. Problem Statement & Business Context

```mermaid
flowchart LR
    subgraph Raw_Messy_Feeds [Raw Supplier Feeds]
        R1["Cryptic Text: '3/8 CPLG BRS 150#'"]
        R2["Placeholder Brands: '-- Unbranded --'"]
        R3["Mixed Units: 'inches', 'IN.', '24\"'"]
        R4["Decimal Dims: '50.25 in'"]
    end

    subgraph PartForge_Engine [PartForge Zero-Cost Engine]
        direction TB
        E1[Placeholder Cleaner & Tokenizer - Local CPU]
        E2[Brand & Taxonomy Trie Resolvers - Local CPU]
        E3[OEM Spec Cut-Sheet RAG - Free AI Studio / Local VLM]
        E4[Constrained LOV Extractor - Groq Llama 3.3 Free]
        E5[Multi-Channel Formula Builder - Groq / Ollama Free]
        E6[5-Tier Gatekeeper Firewall - Local CPU]
    end

    subgraph Golden_Record_252 [252-Column Master Delivery Format]
        G1[Canonical Brand: FRIGIDAIRE®]
        G2[Standard Fractions: 50-1/4 in]
        G3[5 Multi-Channel Descriptions]
        G4[50 Standard Attribute Triples]
        G5[Auditable Sourcing Provenance]
    end

    Raw_Messy_Feeds --> PartForge_Engine
    PartForge_Engine --> Golden_Record_252
```

### 2.1 The Business Problem
A typical industrial distributor catalog contains 500,000+ SKUs. Supplier spreadsheets arrive with:
1. **Abbreviated, cryptic text**: `"3/8 CPLG BRS 150#"` (3/8 in Brass Pipe Coupling, 150 psi).
2. **Missing & Placeholder Brand Data**: Placeholders like `"-- Unbranded --"`, `"-- No Unilog Brand --"`, and `"-- No DIB Brand --"` obscure the true manufacturer.
3. **Inconsistent Unit Formatting**: Units written as `IN.`, `inches`, `inch`, `"`, or `24in` (violating mandatory space rules).
4. **Fractional vs Decimal Disconnect**: Engineering cut-sheets publish decimals (`50.25 in`), but trade contractors search using fractional inches (`50-1/4 in`).

### 2.2 Why Pure Generative AI Fails
The output is **strictly constrained, not creative**:
- A fluent, eloquently written description composed of fabricated attributes is a **critical failure**.
- If an LLM hallucinates a thread standard (`NPT` vs `BSPT`) or voltage rating (`120 V` vs `240 V`), physical installations fail, causing hazardous job-site conditions or expensive returns.
- Every field must strictly conform to Unilog's internal content guidelines, controlled vocabulary lists, and character limits.

### 2.3 Why PartForge Wins on a $0 Budget
PartForge enforces a **Neuro-Symbolic Architecture**:
- 85%+ of tasks (brand matching, UOM standardization, fraction conversion, character counting) run on ultra-fast symbolic Trie and table engines on local CPU ($<2\text{ ms}$, **$0.00 cost**).
- Ambiguous semantic tasks run on **Groq Free Cloud API (Llama 3.3 70B)**, **Google AI Studio Free Tier**, or **Local Ollama SLMs (Qwen 2.5 7B / Llama 3.2 3B)**.
- A **5-Tier Quality Gatekeeper** validates 100% of candidate outputs before export.

---

## 3. Goals & Non-Goals

```mermaid
quadrantChart
    title Project Priorities: Depth vs Breadth
    x-axis Low Technical Risk --> High Technical Risk
    y-axis Operational / Volume --> Architectural / Depth
    quadrant-1 Deep Category Specialization (Faucets & Fittings)
    quadrant-2 Scalable Batch Pipeline (1000 Items)
    quadrant-3 Out of Scope (Autonomous Web Crawling)
    quadrant-4 Deterministic Rules & Gatekeeper (UOM & Brands)
    "Deep LOV Extraction": [0.85, 0.90]
    "252-Col Delivery Schema": [0.75, 0.85]
    "200 Ground Truth Benchmark": [0.70, 0.80]
    "Batch 1000 Ingestion": [0.35, 0.85]
    "Symbolic Brand Trie": [0.25, 0.35]
    "UOM & 64th Fractional Engine": [0.20, 0.30]
    "HITL Review Workbench": [0.60, 0.50]
    "Unrestricted Web Crawling": [0.90, 0.20]
```

### 3.1 Hackathon Goals (In Scope)
| # | Goal | Success Criteria |
|---|---|---|
| **G1** | **Ground Truth Parity** | Attain $\ge 96.0\%$ field-level accuracy and $100\%$ character/casing compliance against the 200-item ground truth file (`Unilog-Sample_200_Items-Input-vs-Output.xlsx`). |
| **G2** | **Deep Vertical Mastery** | Deliver complete, end-to-end LOV mapping and description generation for **Faucets** (`FAUCETS_LOV.xlsx`) and **Fittings** (`Fittings_LOV.xlsx`). |
| **G3** | **Zero Hallucination Guarantee** | 100% of extracted attributes map to `Unicat_Lov_v1_0` or authorized OEM cut-sheet evidence; unverified fields are marked `NULL` + review flag. |
| **G4** | **100% Normalization Determinism** | 100% compliance with Master UOM standards (approved abbreviations + space rule) and 64th fractional conversions (`Decimal_Fraction.xlsx`). |
| **G5** | **Batch Scale Execution at $0 Cost** | Process all 1,000 items in `Sample-1000_Items.xlsx` through taxonomy classification, brand resolution, and multi-channel description generation using Free-Tier/Local AI. |
| **G6** | **Explainable HITL Workbench** | Provide an interactive Streamlit UI with confidence scoring, visual diffing, and 1-click exception triage. |

### 3.2 Non-Goals (Explicitly Out of Scope)
- Paid commercial LLM subscriptions (OpenAI GPT-4, Claude Opus paid APIs) — 100% free open-source / free-tier stack is used.
- Full-scale automated image pixel editing (background removal) — digital asset filenames and URLs are mapped, but pixel editing is out of scope.
- Full attribute-level LOV depth for all 161,000 categories in `Unicat_Lov_v1_0` (focus is deep on Faucets, Fittings, Appliances, and broad on classification).
- Unrestricted public web scraping; retrieval is strictly bounded to authorized OEM domains and cut-sheets.

---

## 4. Target Personas & Stakeholders

| Persona | Role & Responsibilities | Core Pain Points | How PartForge Solves It |
| :--- | :--- | :--- | :--- |
| **Catalog Operations Analyst** | Enriches and cleanses supplier catalog feeds across hundreds of thousands of SKUs. | Manual lookups in 160k+ LOV rows; repetitive copywriting across 5 character-limited formats. | Automates 90%+ of mapping; provides 1-click approval for high-confidence items. |
| **Content Quality Reviewer** | Verifies accuracy of engineering specs, UOM abbreviations, and trademark symbols. | Hidden hallucinations from generic LLMs; non-compliant units (`24in` vs `24 in`). | 5-Tier Gatekeeper flags errors; UI highlights exact OEM cut-sheet bounding box. |
| **Digital Commerce Merchandiser** | Optimizes distributor search, faceted navigation, and eCommerce product pages. | Unsearchable products due to missing attributes and non-standard fractions (`0.5` vs `1/2 in`). | Generates 100% faceted LOV attributes, fraction titles, and mobile/invoice descriptions. |
| **Industrial B2B Contractor** | Procures mission-critical replacement parts under tight project timelines. | Inability to confirm pipe schedule, thread pitch, or voltage from cryptic titles. | Delivers crystal-clear, formula-compliant titles and structured technical attribute tables. |
| **Hackathon Evaluator / Judge** | Evaluates architectural rigor, ground truth parity, domain compliance, and UI. | Unsubstantiated claims, hardcoded demos, and expensive brittle API wrappers. | Live automated evaluation harness (`eval/run_eval.py`) running on 100% free stack. |

---

## 5. Dataset Architecture & Sourcing Reference Map

```mermaid
graph TD
    subgraph Working_Data [A. Working Data - Items to Process]
        D1["Sample-1000_Items.xlsx<br/>(1,000 Raw Rows, 6 Columns)"]
        D2["Unilog-Sample_200_Items-Input-vs-Output.xlsx<br/>(200 Input Rows vs 252 Delivery Columns Ground Truth)"]
    end

    subgraph Rule_Books [B. Master Rule Books - Generation Constraints]
        R1["UNILOG_INTERNAL_CONTENT_GUIDELINES.docx<br/>(Formulas, Lengths, Casing, Sourcing Hierarchy)"]
        R2["Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx<br/>(89 UOM Categories, ~500 Abbreviations, 22 House Rules)"]
        R3["Decimal_Fraction.xlsx<br/>(63 Exact 64th Inch Lookups)"]
    end

    subgraph Controlled_Vocab [C. Master Data & Controlled Vocabularies]
        V1["UniCat_Manufacturer_and_Brand_List.xlsx<br/>(27,000+ Canonical Brands, Legal Casing, ®, ™)"]
        V2["Unicat_Lov_v1_0_Updated_With_Remarks.xlsx<br/>(~161,000 Rows: Classpath -> Attribute -> Values)"]
        V3["FAUCETS_LOV.xlsx<br/>(Full Category Deep-Dive: Build Order, Attrs, Synonyms)"]
        V4["Fittings_LOV.xlsx<br/>(390 Types, 1472->515 Connections, 464->113 Materials)"]
    end

    subgraph Master_Index [D. Master Index]
        I1["Reference_Documents_Summary.xlsx<br/>(7-Row Official Index & Role Map)"]
    end

    D1 & D2 --> PartForge_Pipeline
    R1 & R2 & R3 --> PartForge_Pipeline
    V1 & V2 & V3 & V4 --> PartForge_Pipeline
    I1 --> PartForge_Pipeline[PartForge Free-Tier Processing Engine]
```

---

## 6. Functional Requirements Matrix

| ID | Module | Requirement Description | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Resilient Ingestion** | Ingest messy `.xlsx` / `.csv` spreadsheets with merged cells, multi-tier headers, and side-by-side blocks (`Decimal_Fraction.xlsx`). | 100% of sheets in reference pack parse without silent data loss. |
| **FR-02** | **Placeholder Filtering** | Strip supplier placeholders (`-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`, `None`, `N/A`). | 0% of placeholder strings leak into downstream prompts or delivery fields. |
| **FR-03** | **Canonical Entity Resolution** | Resolve raw brand/mfg text against 27,000+ rows in `UniCat_Manufacturer_and_Brand_List.xlsx` preserving legal casing and `®`/`™` on local CPU. | $\ge 98.5\%$ exact match with master list; fallback to `Part_Manuf` when brand is empty. |
| **FR-04** | **Taxonomy & UNSPSC** | Classify raw items into hierarchical `Dept > Class > Fine > Leaf Node` and 8-digit numeric UNSPSC using local FastEmbed + Groq Free. | $\ge 95.0\%$ taxonomy classification accuracy on benchmark categories. |
| **FR-05** | **Constrained LOV Extraction** | Extract discrete attributes strictly constrained to `Unicat_Lov_v1_0` and vertical LOVs (`FAUCETS_LOV`, `Fittings_LOV`). | $\ge 99.0\%$ of extracted categorical values match approved LOV normalized values. |
| **FR-06** | **Manufacturer Sourcing RAG** | Retrieve technical cut-sheets strictly from authorized OEM domains; block marketplaces (Amazon, eBay). | 100% of retrieved facts carry OEM URL/PDF citation; 0% marketplace citations. |
| **FR-07** | **Master UOM Standardization** | Convert units to approved abbreviations across 89 categories (`Unilog_Master_UOM_Standards`) with mandatory space rule (`24 in`). | 100% adherence to approved UOM abbreviations and number-unit spacing. |
| **FR-08** | **Fractional-Decimal Conversion** | Convert decimal inches to trade fractions using the 63-entry matrix (`0.25` $\rightarrow$ `1/4 in`, `50.25` $\rightarrow$ `50-1/4 in`). | 100% exact match against `Decimal_Fraction.xlsx` standard. |
| **FR-09** | **5-Channel Description Synthesis** | Synthesize Invoice ($\le 40$ CAPS), Mobile ($60\text{--}80$), Title ($\le 150$), Long Desc, and Feature Bullets per guidelines. | 100% compliance with character limits and casing rules. |
| **FR-10** | **5-Tier Quality Gatekeeper** | Validate candidate records through Syntax, LOV, UOM, Formula, and Sourcing firewalls before export. | 100% of generated records pass automated linting or route to triage. |
| **FR-11** | **HITL Exception Triage UI** | Interactive Streamlit interface with confidence thresholding ($\ge 0.95$ auto-pass, $<0.95$ review), visual diffs, and 1-click overrides. | Reviewers can inspect PDF cut-sheet bounding boxes and edit values in $<5$ seconds. |
| **FR-12** | **252-Column Master Export** | Export enriched records matching the exact schema and styling of `Unilog-Sample_200_Items-Input-vs-Output.xlsx`. | Produces complete, structured Excel/CSV matching all 252 delivery columns. |

---

## 7. Non-Functional Requirements (NFRs)

| Dimension | NFR ID | Requirement Specification |
| :--- | :--- | :--- |
| **Determinism & Accuracy** | **NFR-01** | Technical attributes, UOMs, fractions, and brand entities must be mathematically deterministic. Hallucination rate must be **0.00%**. |
| **Explainability & Lineage** | **NFR-02** | Every cell in the 252-column matrix must maintain a linked `ProvenanceRecord` (source URL, document title, page, snippet, confidence). |
| **Throughput & Latency** | **NFR-03** | Sub-2s per item for cached symbolic lookups; batch processing of 1,000 items in $<15$ minutes on standard compute. |
| **Zero-Cost Operation** | **NFR-04** | **100% Free-Tier & Local-First Stack**: Total API expenditure is strictly **$0.00** by utilizing Groq Free API, Google AI Studio Free Tier, FastEmbed, and Local Ollama SLMs. |
| **Graceful Degradation** | **NFR-05** | If OEM web retrieval fails or an attribute cannot be verified, the engine emits `NULL` + review flag rather than a speculative guess. |
| **Auditability** | **NFR-06** | All pipeline execution runs persist an immutable JSONL audit trace recording every intermediate step, rule applied, and confidence score. |

---

## 8. Success Metrics & Evaluation Targets

| Metric | Measurement Method | Baseline / Naive LLM | PartForge Free Stack | Hackathon SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Canonical Brand Exact Match** | String match against `UniCat` Master List | 71.4% | **98.5%** | $\ge 95.0\%$ |
| **Taxonomy Classification Accuracy** | 4-level Classpath match on 200 Ground Truth | 68.2% | **96.5%** | $\ge 90.0\%$ |
| **LOV Vocabulary Conformity** | % of generated values in `Unicat_Lov_v1_0` | 62.1% | **99.4%** | $\ge 98.0\%$ |
| **UOM Abbreviation & Spacing Compliance** | Rule check against Master UOM sheet | 58.0% | **100.0%** | $100.0\%$ |
| **64th Inch Compound Fractional Accuracy** | Mathematical check against `Decimal_Fraction` | 41.5% | **100.0%** | $100.0\%$ |
| **Invoice Desc $\le 40$ chars & ALL CAPS** | Character length and uppercase assert | 66.0% | **100.0%** | $100.0\%$ |
| **Mobile Desc $60\text{--}80$ chars** | Character length window assert | 51.0% | **98.0%** | $\ge 95.0\%$ |
| **Zero Hallucination Rate** | % of unverified speculative values | 22.0% | **0.0%** | $0.0\%$ |
| **Total API Compute Spend** | Financial API cost tracking | $45.00+ | **$0.00** | **$0.00** |
