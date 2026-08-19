# System & UX Design Specification (`Design.md`)

**Project:** **PartForge** — AI-Powered Product Intelligence Pipeline for Industrial Commerce  
**Hackathon:** UniHack 2026 · Unilog × Hack2Skill  
**Infrastructure Target:** **Enterprise Neuro-Symbolic & Local-First Stack ($0.00 Total API Cost)**  
**Companion Documents:** `PRD.md` · `Architecture.md` · `Rules.md` · `Validation.md` · `Evaluation.md`  

---

## 1. Internal Canonical Data Model (The UPIR Schema)

PartForge serializes all internal product intelligence into a unified object: the **Unified Product Intelligence Record (UPIR)**. It is implemented using **Pydantic v2** with strict runtime validation and serialization.

```mermaid
classDiagram
    class RawProductInput {
        +str mfg_part_num
        +str part_desc
        +Optional[str] e1_brand
        +Optional[str] unilog_brand
        +Optional[str] dib_brand
        +Optional[str] part_manuf
        +Optional[str] dept
        +Optional[str] class_name
        +Optional[str] fine_class
        +Optional[str] sku
    }

    class CanonicalBrandProfile {
        +str manufacturer_name
        +str manufacturer_code
        +str brand_name
        +str brand_code
        +float confidence
        +bool trademark_retained
    }

    class TaxonomyNode {
        +str department
        +str class_name
        +str fine_class
        +str leaf_node
        +str classpath
        +str unspsc_code
        +float confidence
    }

    class ProvenanceMetadata {
        +str source_type
        +str source_url
        +Optional[int] page_number
        +Optional[str] snippet
        +Optional[List[float]] bounding_box
        +str extraction_timestamp
        +float confidence_score
    }

    class ExtractedAttribute {
        +str raw_label
        +str normalized_label
        +str raw_value
        +str normalized_value
        +Optional[str] uom
        +bool is_filterable
        +float confidence
        +ProvenanceMetadata provenance
    }

    class MultiChannelDescriptions {
        +str invoice_desc_40
        +str mobile_desc_80
        +str product_title_150
        +str long_description
        +List[str] feature_bullets
    }

    class EnrichedProductRecord {
        +str sku
        +RawProductInput raw_input
        +CanonicalBrandProfile brand_profile
        +TaxonomyNode taxonomy
        +List[ExtractedAttribute] attributes
        +MultiChannelDescriptions descriptions
        +float overall_confidence
        +str validation_status
        +Dict[str, Any] delivery_252_columns
    }

    RawProductInput --> EnrichedProductRecord
    CanonicalBrandProfile --> EnrichedProductRecord
    TaxonomyNode --> EnrichedProductRecord
    ExtractedAttribute --> EnrichedProductRecord
    MultiChannelDescriptions --> EnrichedProductRecord
    ProvenanceMetadata --> ExtractedAttribute
```

### 1.1 Core Pydantic Implementation

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from enum import Enum
import re

class SourcingTier(str, Enum):
    OEM_OFFICIAL_PDF = "OEM_OFFICIAL_PDF"
    OEM_OFFICIAL_WEB = "OEM_OFFICIAL_WEB"
    MASTER_CATALOG_LOV = "MASTER_CATALOG_LOV"
    DISTRIBUTOR_FALLBACK = "DISTRIBUTOR_FALLBACK"
    HEURISTIC_PARSER = "HEURISTIC_PARSER"

class ProvenanceMetadata(BaseModel):
    sourcing_tier: SourcingTier
    source_url: Optional[str] = None
    document_title: Optional[str] = None
    page_number: Optional[int] = None
    snippet: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    extraction_timestamp: str
    confidence_score: float = Field(ge=0.0, le=1.0)

class ExtractedAttribute(BaseModel):
    attribute_label: str
    normalized_label: str
    raw_value: str
    normalized_value: str
    uom: Optional[str] = None
    is_filterable: bool = True
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: ProvenanceMetadata

class MultiChannelDescriptions(BaseModel):
    invoice_desc_40: str = Field(
        max_length=40,
        description="POS/ERP receipt line, max 40 chars, ALL CAPS"
    )
    mobile_desc_80: str = Field(
        min_length=50,
        max_length=80,
        description="Mobile app search card summary, 60-80 chars"
    )
    product_title_150: str = Field(
        max_length=150,
        description="SEO-optimized title: Brand + Series + MPN + Type + Key Attrs"
    )
    long_description: str = Field(
        max_length=2000,
        description="Full technical prose detailing all electrical, dimensional, mounting specs"
    )
    feature_bullets: List[str] = Field(
        default_factory=list,
        description="PDP marketing feature-benefit bullet points"
    )

    @field_validator("invoice_desc_40")
    @classmethod
    def validate_invoice(cls, v: str) -> str:
        if v != v.upper():
            raise ValueError(f"Invoice Description must be ALL CAPS: '{v}'")
        if len(v) > 40:
            raise ValueError(f"Invoice Description exceeds 40 characters ({len(v)}): '{v}'")
        return v

    @field_validator("mobile_desc_80")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not (50 <= len(v) <= 80):
            raise ValueError(f"Mobile Description length out of bounds ({len(v)}): '{v}'")
        return v
```

---

## 2. Master 252-Column Delivery Schema Mapping

The delivery format directly replicates the 252-column schema of `Unilog-Sample_200_Items-Input-vs-Output.xlsx` and `Unihack_ Expected Output - Delivery Format.csv`:

```mermaid
graph TD
    subgraph Delivery_Matrix_252 [252-Column Master Export Structure]
        C1["Cols 1 - 7: System Identifiers & Verified OEM URLs"]
        C2["Cols 8 - 23: Taxonomy Hierarchy, Cleaned Brands & Classpath"]
        C3["Cols 24 - 29: 5 Multi-Channel Copy Formats (Invoice, Mobile, Title, Long)"]
        C4["Cols 30 - 55: Key Product Features, 'With', Standards & Approvals"]
        C5["Cols 56 - 205: 50 Dynamic Attribute Triples (Label, Value, UOM) = 150 Cols"]
        C6["Cols 206 - 214: Industry Codes, Packaging & Warranty (UNSPSC, UPC, GTIN)"]
        C7["Cols 215 - 224: Core Dimensions & Weights (Length, Width, Height, Weight + UOMs)"]
        C8["Cols 225 - 252: Digital Assets, Cut-Sheet Links & Audit Lineage Metadata"]
    end
```

| Column Range | Section Name | Key Column Names | Mandatory / Validation Rules |
| :--- | :--- | :--- | :--- |
| **Cols 001 – 007** | **System & URLs** | `MFR URL`, `Ref URL 1`...`5`, `PART_NUMBER` | Must be valid OEM URL or NULL; no marketplace URLs. |
| **Cols 008 – 023** | **Brand & Taxonomy** | `Dept`, `Class`, `Fine`, `SKU`, `Mfg_Part_Num`, `Part_Desc`, `MANUFACTURER_NAME`, `BRAND_NAME`, `Classpath` | Exact match with UniCat Master List; legal casing & `®`/`™` preserved. |
| **Cols 024 – 029** | **Content Suite** | `MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION` | Invoice $\le 40$ CAPS, Mobile $60\text{--}80$, Short Desc $\le 150$, Long Desc full prose. |
| **Cols 030 – 055** | **Features & Approvals** | `ITEM_FEATURES_1`...`20`, `With`, `Standard/Approvals`, `Prop 65`, `Product Name` | Standards formatted as pipe-separated string (e.g. `cUL Listed\|ENERGY STAR Certified`). |
| **Cols 056 – 205** | **50 Attribute Triples** | `ATTRIBUTE_LABEL 1`...`50`, `ATTRIBUTE_VALUE 1`...`50`, `ATTRIBUTE_UOM 1`...`50` | 100% compliance with `Unicat_Lov_v1_0`; UOMs mapped to Master Standards. |
| **Cols 206 – 214** | **Codes & Packaging** | `UPC`, `EAN`, `GTIN`, `UNSPSC`, `Warranty`, `List Price`, `Selling Qty`, `Selling UOM` | UNSPSC must be 8 numeric digits. |
| **Cols 215 – 224** | **Dimensions** | `LENGTH`, `LENGTH_UOM`, `HEIGHT`, `HEIGHT_UOM`, `WIDTH`, `WIDTH_UOM`, `WEIGHT`, `WEIGHT_UOM` | Converted to trade fractional inches (`Decimal_Fraction.xlsx`). |
| **Cols 225 – 252** | **Digital Assets** | `Product Image`, `Alternate Image 1`...`4`, `Specification Sheet`, `Line Drawing`, `Actual Image (Yes/No)` | Filename formatted as `BRAND_MPN.jpg` / `.pdf`. |

---

## 3. Human-in-the-Loop (HITL) UI/UX Specification

The PartForge HITL Workbench is implemented in **Streamlit / FastHTML**, designed specifically for catalog engineers who need to process exceptions at high speed.

```mermaid
graph TD
    subgraph Dashboard_Layout [Streamlit HITL Review Dashboard Layout]
        NAV[Top Bar: Batch KPIs, Ingestion Progress, Filter: All / Amber / Red / High Conf]
        
        subgraph Split_Panel [Main Split-Screen Workspace]
            LEFT[Left View: Raw Supplier Input + PDF Cut-Sheet Preview with Bounding Boxes]
            CENTER[Center View: 5 Generated Multi-Channel Descriptions + Real-Time Linter Chips]
            RIGHT[Right View: 50-Attribute LOV Data Grid with 1-Click Dropdown Overrides]
        end
        
        FOOTER[Bottom Action Bar: 1-Click Approve, Auto-Repair All, Reject, Export 252-Col Master Excel]
    end
    
    NAV --> Split_Panel
    Split_Panel --> FOOTER
```

### 3.1 Confidence Scoring & Visual Hierarchy
* 🟢 **Green Queue ($\ge 0.95$ Confidence, 100% Rule Valid)**: Fast-tracked straight to production export without blocking human review.
* 🟡 **Amber Queue ($0.80 \text{--} 0.94$ Confidence, Minor Warning)**: Highlighted with yellow badge (e.g. `"Fuzzy Brand Match (89%)"`); 1-click accept button.
* 🔴 **Red Queue ($<0.80$ Confidence or Rule Violation)**: Highlighted with red error chips (e.g. `"Invoice Desc > 40 chars"` or `"Unmapped Connection Type"`); auto-fix suggestion provided.

---

## 4. Provider-Agnostic Enterprise AI Architecture & REST API

```mermaid
sequenceDiagram
    participant App as Client / Streamlit UI
    participant API as FastAPI Gateway
    participant Cache as In-Memory Trie Cache
    participant LLM as LLM Engine (Groq / Ollama / AI Studio)
    participant DB as DuckDB Master Store

    App->>API: POST /api/v1/enrich/single (Raw SKU Row)
    API->>Cache: Check Local In-Memory Trie Cache ($0.00)
    alt Cache Hit (85% of queries)
        Cache-->>API: Return Standardized Brand, UOM, Fractions
    else Semantic Ambiguity (15% of queries)
        API->>LLM: Call LLM Engine API (Groq Llama 3.3 / Local Ollama)
        LLM-->>API: Constrained JSON Output
    end
    API->>DB: Persist Golden UPIR Record + Provenance
    API-->>App: 200 OK (252-Column JSON + Validation Chips)
```

### 4.1 Key Endpoints
1. `POST /api/v1/enrich/single`: Ingests a single raw catalog row; returns 252-column object and audit lineage in $<2$ seconds for **$0.00**.
2. `POST /api/v1/enrich/batch`: Ingests `Sample-1000_Items.xlsx` asynchronously with rate-limit throttling; provides live progress bar.
3. `POST /api/v1/validate`: Executes deterministic linting on candidate strings against character limits, casing, UOM, and LOV on local CPU.
4. `GET /api/v1/hitl/queue`: Fetches pending triage items sorted by confidence ascending.
5. `GET /api/v1/export/delivery-excel`: Generates the styled 252-column master Excel file matching the official ground truth delivery template.
