# 🔧 PartForge — AI-Powered Product Intelligence Pipeline

**UniHack 2026 · Unilog × Hack2Skill**  
**100% Free Tier & Local-First Architecture ($0.00 API Cost)**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure free API keys (copy and edit)
cp .env.example .env
# Edit .env with your free Groq/Gemini API keys

# 3. Enrich a single product
python main.py enrich-single --mpn "PDSH4816AF" --desc "PDSH4816AF Dishwasher SS"

# 4. Batch enrich 1,000 items
python main.py enrich-batch --input "data/Unihack_ Sample Dataset - Input.csv" --output output/delivery.csv

# 5. Run evaluation benchmark
python main.py evaluate --ground-truth "data/Unihack_ Expected Output - Delivery Format.csv" --predictions output/delivery.csv

# 6. Launch interactive HITL dashboard
python main.py ui
```

---

## 📁 Project Structure

```
partforge/
├── main.py                          # CLI entry point
├── requirements.txt                 # Dependencies (all free/open-source)
├── .env.example                     # Free API key template
│
├── src/
│   ├── config.py                    # Centralized config & 252-column schema
│   ├── models.py                    # Pydantic v2 UPIR data models
│   │
│   ├── knowledge/                   # Symbolic Knowledge Plane (Local CPU, $0.00)
│   │   ├── placeholder.py           # Placeholder detection & stripping
│   │   ├── fraction_matrix.py       # 64th decimal-to-fraction converter
│   │   ├── uom_engine.py            # UOM standardization & spacing rules
│   │   ├── brand_trie.py            # Brand/Mfg fuzzy matching (RapidFuzz)
│   │   └── lov_index.py             # Controlled vocabulary LOV lookup
│   │
│   ├── ingestion/                   # Data Ingestion Pipeline
│   │   ├── parser.py                # Resilient CSV/Excel parser
│   │   └── pipeline.py              # End-to-end ingestion orchestrator
│   │
│   ├── ai/                          # AI Reasoning Core (Free Tier LLMs)
│   │   ├── llm_client.py            # FreeLLMClient (Groq/Gemini/Ollama)
│   │   ├── taxonomy_classifier.py   # Taxonomy & UNSPSC classification
│   │   ├── attribute_extractor.py   # Constrained LOV attribute extraction
│   │   └── description_builder.py   # 5-channel description synthesis
│   │
│   ├── rules/                       # Quality Gatekeeper
│   │   └── gatekeeper.py            # 5-Tier validation firewall
│   │
│   ├── export/                      # Delivery Export
│   │   └── delivery_exporter.py     # 252-column Excel/CSV exporter
│   │
│   └── ui/                          # HITL Dashboard
│       └── app.py                   # Streamlit interactive workbench
│
├── eval/
│   └── run_eval.py                  # Automated benchmark runner
│
├── data/                            # Datasets
│   ├── Unihack_ Sample Dataset - Input.csv
│   └── Unihack_ Expected Output - Delivery Format.csv
│
└── docs/                            # Specification Documents
    ├── PRD.md
    ├── Architecture.md
    ├── Rules.md
    ├── Design.md
    ├── Phases.md
    ├── AI_Strategy.md
    ├── Validation.md
    ├── Evaluation.md
    ├── Demo.md
    └── Verification_Checklist.md
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Data Ingestion (CSV/Excel Parser + Placeholder    │
│           Stripper + De-duplication)                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Symbolic Knowledge Plane (Local CPU, $0.00)       │
│  • Brand Trie (27k+ entries, RapidFuzz)                     │
│  • LOV Constraint Graph (161k+ rows)                        │
│  • UOM Engine (89 categories, 500+ abbreviations)           │
│  • 64th Fractional Matrix (63 exact lookups)                │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: AI Reasoning Core (Free Tier, $0.00)              │
│  • Groq Llama 3.3 70B (30 RPM free)                         │
│  • Google AI Studio Gemini (15 RPM free)                     │
│  • Local Ollama (Qwen 2.5 / Llama 3.2)                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: 5-Tier Quality Gatekeeper (Deterministic)         │
│  T1: Syntax │ T2: LOV │ T3: UOM │ T4: Casing │ T5: Source  │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Delivery & HITL (Streamlit + 252-Col Exporter)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Cost: $0.00

| Component | Technology | Cost |
|-----------|-----------|------|
| Symbolic Processing | Local CPU (FastEmbed, RapidFuzz, Trie) | **$0.00** |
| LLM Reasoning | Groq Free API / Local Ollama | **$0.00** |
| Multimodal | Google AI Studio Free Tier | **$0.00** |
| Dashboard | Streamlit | **$0.00** |
| **Total** | | **$0.00** |
