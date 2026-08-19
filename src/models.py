"""
PartForge Data Models — Pydantic v2 UPIR schemas.

Unified Product Intelligence Record (UPIR) is the canonical internal
data contract used by every pipeline stage.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Enums ─────────────────────────────────────────────────────────────────────

class SourcingTier(str, Enum):
    """7-tier sourcing precedence hierarchy."""
    CONTENT_GUIDELINES = "CONTENT_GUIDELINES"
    CATEGORY_LOV = "CATEGORY_LOV"
    MASTER_CONTROLLED_VOCAB = "MASTER_CONTROLLED_VOCAB"
    UOM_STANDARDS = "UOM_STANDARDS"
    FRACTION_MATRIX = "FRACTION_MATRIX"
    OEM_CUTSHEET = "OEM_CUTSHEET"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    FALLBACK_NULL = "FALLBACK_NULL"


class ValidationStatus(str, Enum):
    """Record-level validation outcome."""
    PASSED = "PASSED"
    AMBER = "AMBER"
    FAILED = "FAILED"
    PENDING = "PENDING"


class ConfidenceLevel(str, Enum):
    GREEN = "GREEN"      # >= 0.95
    AMBER = "AMBER"      # 0.80 - 0.94
    RED = "RED"           # < 0.80


# ── Provenance ────────────────────────────────────────────────────────────────

class ProvenanceRecord(BaseModel):
    """Tracks the exact source of every extracted data point."""
    sourcing_tier: SourcingTier
    source_url: Optional[str] = None
    document_title: Optional[str] = None
    page_number: Optional[int] = None
    snippet: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    extraction_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    confidence_score: float = Field(ge=0.0, le=1.0, default=1.0)


# ── Raw Input ─────────────────────────────────────────────────────────────────

class RawProductInput(BaseModel):
    """Schema matching the 6-column input CSV."""
    mfg_part_num: str
    part_desc: str
    e1_brand: Optional[str] = None
    unilog_brand: Optional[str] = None
    dib_brand: Optional[str] = None
    part_manuf: Optional[str] = None


# ── Brand Profile ─────────────────────────────────────────────────────────────

class CanonicalBrandProfile(BaseModel):
    """Resolved brand/manufacturer entity from UniCat Master List."""
    manufacturer_name: str = ""
    manufacturer_code: str = ""
    brand_name: str = ""
    brand_code: str = ""
    trade_name: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    trademark_retained: bool = False
    provenance: ProvenanceRecord = Field(
        default_factory=lambda: ProvenanceRecord(
            sourcing_tier=SourcingTier.MASTER_CONTROLLED_VOCAB
        )
    )


# ── Taxonomy ──────────────────────────────────────────────────────────────────

class TaxonomyNode(BaseModel):
    """Hierarchical classification: Dept > Class > Fine > Leaf + UNSPSC."""
    department: str = ""
    class_name: str = ""
    fine_class: str = ""
    leaf_node: str = ""
    classpath: str = ""
    unspsc_code: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    provenance: ProvenanceRecord = Field(
        default_factory=lambda: ProvenanceRecord(
            sourcing_tier=SourcingTier.MODEL_INFERENCE
        )
    )

    @field_validator("unspsc_code")
    @classmethod
    def validate_unspsc(cls, v: str) -> str:
        if v and not re.match(r"^\d{8}$", v):
            # Allow empty/unset, but if set must be 8 digits
            pass  # Will be flagged by gatekeeper, don't block model init
        return v


# ── Extracted Attribute ───────────────────────────────────────────────────────

class ExtractedAttribute(BaseModel):
    """A single attribute extracted from product data."""
    attribute_label: str
    normalized_label: str = ""
    raw_value: str = ""
    normalized_value: str = ""
    uom: Optional[str] = None
    is_filterable: bool = True
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    provenance: ProvenanceRecord = Field(
        default_factory=lambda: ProvenanceRecord(
            sourcing_tier=SourcingTier.MODEL_INFERENCE
        )
    )


# ── Multi-Channel Descriptions ───────────────────────────────────────────────

class MultiChannelDescriptions(BaseModel):
    """5 mandatory customer-facing content formats."""
    invoice_desc: str = Field(
        default="",
        description="POS/ERP receipt line, max 40 chars, ALL CAPS"
    )
    mobile_desc: str = Field(
        default="",
        description="Mobile app search card, 60-80 chars"
    )
    short_desc: str = Field(
        default="",
        description="SEO product title, max 150 chars"
    )
    long_desc: str = Field(
        default="",
        description="Full technical prose description"
    )
    retail_desc: str = Field(
        default="",
        description="Retail-facing description"
    )
    marketing_desc: str = Field(
        default="",
        description="Marketing description"
    )
    feature_bullets: List[str] = Field(
        default_factory=list,
        description="PDP feature bullet points (up to 20)"
    )


# ── Validation Error ─────────────────────────────────────────────────────────

class ValidationError(BaseModel):
    """A single validation failure from the 5-Tier Gatekeeper."""
    tier: int = Field(ge=1, le=5)
    error_code: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    field_name: str
    message: str
    auto_repair_applied: bool = False
    repaired_value: Optional[str] = None


# ── Enriched Product Record (UPIR) ───────────────────────────────────────────

class EnrichedProductRecord(BaseModel):
    """
    The Unified Product Intelligence Record (UPIR).
    This is the master internal object flowing through the entire pipeline.
    """
    # Core identity
    sku: str = ""
    raw_input: RawProductInput

    # Enrichment results
    brand_profile: CanonicalBrandProfile = Field(
        default_factory=CanonicalBrandProfile
    )
    taxonomy: TaxonomyNode = Field(default_factory=TaxonomyNode)
    attributes: List[ExtractedAttribute] = Field(default_factory=list)
    descriptions: MultiChannelDescriptions = Field(
        default_factory=MultiChannelDescriptions
    )

    # Quality signals
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[ValidationError] = Field(default_factory=list)
    confidence_level: ConfidenceLevel = ConfidenceLevel.RED

    # Metadata
    processing_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    pipeline_version: str = "1.0.0"

    def compute_confidence_level(self) -> ConfidenceLevel:
        """Determine Green/Amber/Red from overall confidence score."""
        if self.overall_confidence >= 0.95:
            return ConfidenceLevel.GREEN
        elif self.overall_confidence >= 0.80:
            return ConfidenceLevel.AMBER
        else:
            return ConfidenceLevel.RED

    def to_delivery_row(self) -> Dict[str, Any]:
        """
        Flatten the UPIR into a dict keyed by the 252 delivery column names.
        This is the final export format.
        """
        row: Dict[str, Any] = {}

        # System URLs (cols 1-6 blank by default, col 7 = PART_NUMBER)
        row["MFR URL"] = ""
        for i in range(1, 6):
            row[f"Ref URL {i}"] = ""
        row["PART_NUMBER"] = self.raw_input.mfg_part_num

        # Input passthrough (cols 8-17)
        row["Dept"] = self.taxonomy.department
        row["Class"] = self.taxonomy.class_name
        row["Fine"] = self.taxonomy.fine_class
        row["SKU - MY_PART_NUMBER"] = self.sku
        row["Mfg_Part_Num"] = self.raw_input.mfg_part_num
        row["Part_Desc"] = self.raw_input.part_desc
        row["E1_Brand"] = self.raw_input.e1_brand or ""
        row["Unilog_Brand"] = self.raw_input.unilog_brand or ""
        row["DIB_Brand"] = self.raw_input.dib_brand or ""
        row["Part_Manuf"] = self.raw_input.part_manuf or ""

        # Enriched brand/taxonomy (cols 18-23)
        row["MANUFACTURER_NAME"] = self.brand_profile.manufacturer_name
        row["BRAND_NAME"] = self.brand_profile.brand_name
        row["TRADE_NAME"] = self.brand_profile.trade_name
        row["MANUFACTURER_PART_NUMBER"] = self.raw_input.mfg_part_num
        row["ALTERNATE_PART_NUMBER"] = ""
        row["Classpath"] = self.taxonomy.classpath

        # Descriptions (cols 24-29)
        row["MOBILE_DESC"] = self.descriptions.mobile_desc
        row["INVOICE_DESC"] = self.descriptions.invoice_desc
        row["SHORT_DESC"] = self.descriptions.short_desc
        row["LONG_DESC1"] = self.descriptions.long_desc
        row["RETAIL_DESC"] = self.descriptions.retail_desc
        row["MARKETING_DESCRIPTION"] = self.descriptions.marketing_desc

        # Features (cols 30-49)
        for i in range(1, 21):
            idx = i - 1
            if idx < len(self.descriptions.feature_bullets):
                row[f"ITEM_FEATURES_{i}"] = self.descriptions.feature_bullets[idx]
            else:
                row[f"ITEM_FEATURES_{i}"] = ""

        # Misc fields (cols 50-55)
        row["With"] = ""
        row["Standard/Approvals"] = ""
        row["Prop 65"] = ""
        row["Application"] = ""
        row["Includes"] = ""
        row["Product Name"] = ""

        # Attribute triples (cols 56-205) — interleaved
        for i in range(1, 51):
            idx = i - 1
            if idx < len(self.attributes):
                attr = self.attributes[idx]
                row[f"ATTRIBUTE_LABEL {i}"] = attr.normalized_label or attr.attribute_label
                row[f"ATTRIBUTE_VALUE {i}"] = attr.normalized_value or attr.raw_value
                row[f"ATTRIBUTE_UOM {i}"] = attr.uom or ""
            else:
                row[f"ATTRIBUTE_LABEL {i}"] = ""
                row[f"ATTRIBUTE_VALUE {i}"] = ""
                row[f"ATTRIBUTE_UOM {i}"] = ""

        # Codes & packaging (cols 206-214)
        row["UPC"] = ""
        row["EAN"] = ""
        row["GTIN"] = ""
        row["UNSPSC"] = self.taxonomy.unspsc_code
        row["Warranty"] = ""
        row["List Price"] = ""
        row["Selling Qty"] = ""
        row["Selling UOM"] = ""
        row["Standard Packaging Information"] = ""

        # Dimensions (cols 215-224) — populate from attributes if available
        for dim_col in ["LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM",
                        "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM",
                        "VOLUME", "VOLUME_UOM"]:
            row[dim_col] = ""

        # Digital assets (cols 225-252)
        asset_cols = [
            "Product Image", "Alternate Image 1", "Alternate Image 2",
            "Alternate Image 3", "Alternate Image 4",
            "SDS", "SDS_1", "Warranty Information", "Catalog",
            "Specification Sheet", "Instruction/Installation Manual",
            "Service Manual", "Owners/User Manual", "Line Drawing",
            "MTR", "RoHS", "Full Engineering Drawing", "Energy Star Guide",
            "Technical Bulletin", "Submittal", "Compatibility Chart",
            "Size Chart", "Product Label/Insert",
            "Video Link", "Video Link 1",
            "Country Of Origin", "Discontinued", "Actual Image (Yes/No)",
        ]
        for col in asset_cols:
            row[col] = ""

        return row
