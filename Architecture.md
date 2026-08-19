# System Architecture Specification (`Architecture.md`)

**Project:** **PartForge** — AI-Powered Product Intelligence Pipeline for Industrial Commerce  
**Hackathon:** UniHack 2026 · Unilog × Hack2Skill  
**Infrastructure Cost Target:** **100% Free Tier & Local-First Stack ($0.00 Total API Cost)**  
**Companion Documents:** `PRD.md` · `Rules.md` · `Design.md` · `AI_Strategy.md` · `Validation.md` · `Evaluation.md`  

---

## 1. Architectural Philosophy: The Neuro-Symbolic Principle

Industrial product data engineering operates under a strict constraint: **specifications must be factual, standardized, and legally compliant**. A pure Large Language Model (LLM) pipeline inevitably fails because LLMs are non-deterministic, struggle with hard character limits, and hallucinate plausible-sounding engineering values.

PartForge enforces a **100% Free-Tier Neuro-Symbolic Hybrid Architecture**:

> **"Deterministic where the answer is known, generative where it isn't."**
> 
> *UOM conversions, fraction lookups, brand canonicalization, character counting, and casing enforcement are table lookups—they run in high-speed symbolic rules engines on local CPU ($0.00). Taxonomy classification, unstructured spec-sheet parsing, and multi-channel narrative synthesis run through free-tier open-source LLMs (Groq Llama 3.3 70B / Ollama Qwen 2.5 / Google AI Studio Free Tier).*

```mermaid
flowchart TD
    subgraph Data_Plane [Layer 1: Resilient Data Ingestion Plane]
        IN[Raw Catalog: Excel / CSV / Stream] --> PARSE[Messy Excel Resilient Parser]
        PARSE --> CLEAN[Placeholder Stripper & Sanitizer]
        CLEAN --> DEDUP[De-duplication & Blocking Engine]
        DEDUP --> UPIR_INIT[Raw UPIR Record Initializer]
    end

    subgraph Knowledge_Plane [Layer 2: Symbolic Knowledge & Master Vocabularies]
        BRAND_TRIE[(UniCat 27k Brand/Mfg Trie - Local CPU)]
        LOV_GRAPH[(Unicat 161k LOV Trie Graph - Local CPU)]
        UOM_ENG[(Master UOM 89 Categories - Local CPU)]
        FRAC_MAT[(64th Fractional Matrix - Local CPU)]
        VERT_LOV[(Faucets & Fittings Deep LOVs)]
    end

    subgraph AI_Reasoning_Plane [Layer 3: Multi-Agent AI Reasoning Core - 100% Free Models]
        ORCH[Enrichment Orchestrator Agent]
        CLASS_AGENT[Taxonomy & UNSPSC Classifier: Local BGE-Small]
        RAG_AGENT[OEM Sourcing RAG: Free AI Studio / Local VLM]
        ATTR_AGENT[Constrained Extractor: Groq Llama 3.3 70B Free]
        SYNTH_AGENT[Multi-Channel Formula Builder: Groq / Ollama Free]
    end

    subgraph Quality_Plane [Layer 4: Deterministic Quality Gatekeeper - Local CPU]
        T1[Tier 1: Syntax & Length Linter]
        T2[Tier 2: Controlled LOV Validator]
        T3[Tier 3: UOM & Fraction Verifier]
        T4[Tier 4: Formula & Casing Linter]
        T5[Tier 5: Sourcing Lineage & Anomaly Guard]
        CONF[Confidence Calibration Engine]
    end

    subgraph Experience_Plane [Layer 5: Delivery & HITL Experience Plane]
        AUTO_EXPORT[252-Column Master Delivery Exporter]
        HITL_UI[Interactive Streamlit HITL Workbench]
        AUDIT_LOG[(Immutable Audit Trace Store)]
    end

    UPIR_INIT --> ORCH
    ORCH --> CLASS_AGENT
    CLASS_AGENT --> BRAND_TRIE
    CLASS_AGENT --> LOV_GRAPH
    ORCH --> RAG_AGENT
    RAG_AGENT --> ATTR_AGENT
    ATTR_AGENT --> LOV_GRAPH
    ATTR_AGENT --> VERT_LOV
    ATTR_AGENT --> SYNTH_AGENT
    SYNTH_AGENT --> UOM_ENG
    SYNTH_AGENT --> FRAC_MAT
    SYNTH_AGENT --> Quality_Plane

    Quality_Plane -->|Score >= 0.95 & 100% Valid| AUTO_EXPORT
    Quality_Plane -->|Score < 0.95 or Flagged| HITL_UI
    Quality_Plane --> AUDIT_LOG
    HITL_UI -->|1-Click Reviewer Approval| AUTO_EXPORT
```

---

## 2. Five-Layer Architecture Breakdown

### 2.1 Layer 1: Data Plane (Ingestion & Normalization)
* **Messy Excel Resilient Parser**: Directly addresses structural anomalies in the Unilog dataset:
  - Multi-tier column headers and merged metadata cells.
  - Multi-column stacked blocks (`Decimal_Fraction.xlsx` structured as 4 side-by-side fraction/decimal columns).
  - Stray text notes in margin columns (`Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx`).
* **Placeholder Sanitizer**: Regex and token filters stripping `-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`, `None`, and `N/A`.
* **De-duplication & Blocking**: Hashes `Mfg_Part_Num` + canonical manufacturer to flag duplicate supplier catalog entries before enrichment.

### 2.2 Layer 2: Knowledge Plane (Controlled Vocabularies)
* **UniCat Master Brand Trie Index (27,000+ rows)**:
  - In-memory double-metaphone and Jaro-Winkler prefix tree running 100% on local CPU.
  - Resolves noisy strings (`"Frigidaire"`, `"FRIG"`, `"Rheem Mfg"`) to canonical `MANUFACTURER_NAME`, `MANUFACTURER_CODE`, `BRAND_NAME`, `BRAND_CODE` with legal casing and `®`/`™` retention.
* **Trie-Indexed LOV Constraint Graph (161,000+ rows)**:
  - Hierarchy: `Classpath -> Leaf Node -> Attribute Label -> Permitted Values`.
  - Enables sub-millisecond constraint injection during prompting.
* **UOM & Fractional Matrix**:
  - 89 measurement categories, ~500 approved abbreviations (`in`, `ft`, `gpm`, `psi`, `V`, `A`).
  - 63-entry 64th decimal-to-fraction converter (`0.25` $\rightarrow$ `1/4 in`, `50.25` $\rightarrow$ `50-1/4 in`).

### 2.3 Layer 3: AI Reasoning Plane (Multi-Agent DAG — Free Model Tiering)

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator Agent
    participant Class as Classification Agent (Local BGE-Small)
    participant Sourcing as OEM Sourcing RAG (Free Tier)
    participant Extr as Attribute Extractor (Groq Llama 3.3 Free)
    participant Synth as Formula Builder (Groq / Ollama Free)
    participant Gate as Gatekeeper Engine (Local CPU)

    Orch->>Class: Classify(Raw Desc, MPN, Brand)
    Class-->>Orch: Classpath + 8-Digit UNSPSC
    Orch->>Sourcing: FetchOEMCutSheet(Canonical Brand, MPN)
    Sourcing-->>Orch: Verified Cut-Sheet Context + Provenance URL
    Orch->>Extr: ExtractAttributes(Context, Classpath LOV)
    Extr-->>Orch: Constrained Key-Value Triples
    Orch->>Synth: SynthesizeDescriptions(Specs, Formulas)
    Synth-->>Orch: 5 Multi-Channel Copy Formats
    Orch->>Gate: ValidateRecord(UPIR Record)
    Gate-->>Orch: Validation Report + Calibrated Confidence Score
```

1. **Taxonomy & UNSPSC Classification Agent**: Embeds input text using lightweight local embeddings (`FastEmbed BGE-Small`, 100% offline, $0.00) and performs hierarchical category tree traversal.
2. **OEM Sourcing & Cut-Sheet RAG Agent**: Queries authorized OEM domains (`*.frigidaire.com`, `*.moen.com`, `*.parker.com`), fetches technical cut-sheet PDFs, and extracts tabular specifications. Marketplaces (Amazon, eBay) are strictly blocked.
3. **Constrained Attribute Extraction Agent**: Employs Grammar-Guided JSON Decoding powered by **Groq Free API (Llama 3.3 70B at 500+ tok/sec)** or **Local Ollama (Qwen 2.5 7B)**, forcing output values to match `Unicat_Lov_v1_0`.
4. **Multi-Channel Formula Synthesis Agent**: Compiles the 5 required description formats following deterministic construction formulas.

### 2.4 Layer 4: Quality Plane (5-Tier Gatekeeper Firewall)
Every enriched record must pass 5 sequential validation checks before delivery:
1. **Tier 1 (Syntax & Length)**: Invoice $\le 40$ chars, Mobile $60\text{--}80$ chars, Title $\le 150$ chars, UNSPSC 8 digits.
2. **Tier 2 (Controlled LOV)**: 100% membership check for Brand, Manufacturer, and Categorical Attribute values.
3. **Tier 3 (UOM & Fractions)**: Approved UOM abbreviations, number-unit space rule (`24 in`), 64th compound fraction check (`50-1/4 in`).
4. **Tier 4 (Formula & Casing)**: Invoice ALL UPPERCASE, legal symbol placement (`®`/`™`).
5. **Tier 5 (Lineage & Anomaly)**: Sourcing provenance verification, physical outlier rejection.

### 2.5 Layer 5: Experience & Delivery Plane
* **252-Column Delivery Exporter**: Writes enriched records into formatted Excel spreadsheets matching `Unilog-Sample_200_Items-Input-vs-Output.xlsx`.
* **Streamlit HITL Review Dashboard**: Interactive web interface featuring side-by-side visual diffs, cut-sheet PDF snippet previews, confidence color-coding, and 1-click overrides.
* **Immutable Audit Trace Store**: Persists complete JSONL execution trajectories for full regulatory auditability.

---

## 3. The Evidence Graph Architecture

```mermaid
graph LR
    P[Product: PDSH4816AF] -->|CLASSIFIED_AS| C[Classpath: Built-In Dishwashers]
    P -->|PRODUCED_BY| M[Manufacturer: Rheem Manufacturing]
    P -->|BRANDED_AS| B[Brand: FRIGIDAIRE®]
    P -->|HAS_ATTRIBUTE| A1[Attribute: Sound Level]
    A1 -->|HAS_VALUE| V1[Value: 47 dBA]
    V1 -->|EXTRACTED_FROM| D1[Cut-Sheet: PDSH4816AF.pdf, Page 2]
    D1 -->|HOSTED_AT| S1[OEM Domain: frigidaire.com]
    
    P -->|HAS_ATTRIBUTE| A2[Attribute: Depth Open]
    A2 -->|HAS_VALUE| V2[Value: 50-1/4 in]
    V2 -->|NORMALIZED_BY| R1[Rule: Decimal_Fraction 0.25 -> 1/4]
```

---

## 4. Technical Stack Selection (100% Free & Open-Source Tier)

| Layer | Component | Technology Choice | Why Chosen & Cost |
| :--- | :--- | :--- | :--- |
| **Orchestration** | Multi-Agent DAG | **Python 3.11+ / AsyncIO** | Lightweight, stateful agent execution with async batching for 1,000 items. (**$0.00**) |
| **Symbolic Indexing** | Brand & LOV Lookups | **RapidFuzz + SymSpell + Trie** | Ultra-fast in-memory lookup ($<0.5\text{ ms}$) over 27k brands and 161k LOVs on local CPU. (**$0.00**) |
| **Vector Embeddings** | Taxonomy Classification | **FastEmbed (`bge-small-en-v1.5`)** | 100% offline local embeddings running on CPU in $<2\text{ ms}$; zero API cost. (**$0.00**) |
| **LLM & Reasoning** | Constrained Extraction | **Groq Free API (Llama 3.3 70B / 3.1 8B)** | 500+ tokens/second ultra-fast inference with free tier (30 RPM / 14,400 RPD). (**$0.00**) |
| **Local Offline LLM** | Air-Gapped Fallback | **Ollama (`qwen2.5:7b` / `llama3.2:3b`)** | 100% offline fallback running locally on developer laptop GPU/CPU. (**$0.00**) |
| **Multimodal Vision** | Cut-Sheet Diagram Parsing | **Google AI Studio Free Tier (Gemini 2.5 Flash)** | 1,500 free requests per day for PDF cut-sheet parsing. (**$0.00**) |
| **Schema Validation** | Type & Data Contracts | **Pydantic v2** | Strict runtime validation, Rust-based serialization, zero malformed JSON errors. (**$0.00**) |
| **Data Lake & OLAP** | Storage & Aggregation | **DuckDB + Polars** | Columnar in-process OLAP engine handling 252-column wide schema transformations. (**$0.00**) |
| **HITL Dashboard** | Reviewer Interface | **Streamlit** | Rapid interactive triage dashboard with visual diffs and Excel export. (**$0.00**) |
