"""
PartForge Configuration — Centralized paths, constants, and delivery schema.

All 252 delivery column names are sourced directly from the verified
`Unihack_ Expected Output - Delivery Format.csv` header row.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project Root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVAL_DIR = PROJECT_ROOT / "eval"

# ── High-Performance API Configuration ────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# ── LLM Model IDs ────────────────────────────────────────────────────────────
GROQ_MODEL_PRIMARY = "llama-3.3-70b-versatile"
GROQ_MODEL_FAST = "llama-3.1-8b-instant"
GEMINI_MODEL = "gemini-2.5-flash"

# ── Dataset File Paths ────────────────────────────────────────────────────────
INPUT_CSV = DATA_DIR / "Unihack_ Sample Dataset - Input.csv"
DELIVERY_CSV = DATA_DIR / "Unihack_ Expected Output - Delivery Format.csv"

# ── Placeholder Strings (Official + Heuristic) ───────────────────────────────
OFFICIAL_PLACEHOLDERS = frozenset([
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --",
])

HEURISTIC_PLACEHOLDERS = frozenset([
    "Unbranded", "Generic", "None", "N/A", "NA", "TBD", "Blank",
    "Unknown", "Not Specified", "Not Available",
])

ALL_PLACEHOLDERS = OFFICIAL_PLACEHOLDERS | HEURISTIC_PLACEHOLDERS

# ── Character Limit Constants ─────────────────────────────────────────────────
INVOICE_DESC_MAX_LEN = 40
MOBILE_DESC_MIN_LEN = 60
MOBILE_DESC_MAX_LEN = 80
TITLE_DESC_MAX_LEN = 150
UNSPSC_DIGITS = 8

# ── Fuzzy Match Thresholds ────────────────────────────────────────────────────
BRAND_FUZZY_THRESHOLD = 88  # RapidFuzz score out of 100
BRAND_AMBIGUITY_MARGIN = 5  # Minimum gap between top-2 candidates

# ── Confidence Score Weights ──────────────────────────────────────────────────
CONFIDENCE_WEIGHT_BRAND = 0.20
CONFIDENCE_WEIGHT_TAXONOMY = 0.20
CONFIDENCE_WEIGHT_ATTRIBUTES = 0.40
CONFIDENCE_WEIGHT_PROVENANCE = 0.20

# ── Confidence Thresholds ─────────────────────────────────────────────────────
CONFIDENCE_AUTO_PASS = 0.95
CONFIDENCE_AMBER = 0.80

# ── Rate Limiting (Enterprise Tier) ─────────────────────────────────────────────────
GROQ_RPM_LIMIT = 25  # Stay under 30 RPM hybrid inference tier cap
GROQ_PAUSE_SECONDS = 2.5  # Delay between batched requests
BATCH_CONCURRENT_WORKERS = 4

# ── Input CSV Columns ─────────────────────────────────────────────────────────
INPUT_COLUMNS = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf",
]

# ── Full 252 Delivery Column Schema ──────────────────────────────────────────
# Verified character-for-character from `Unihack_ Expected Output - Delivery Format.csv`
DELIVERY_COLUMNS = [
    # Cols 1-7: System Identifiers & OEM URLs
    "MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4",
    "Ref URL 5", "PART_NUMBER",
    # Cols 8-23: Brand, Taxonomy & Classpath
    "Dept", "Class", "Fine", "SKU - MY_PART_NUMBER", "Mfg_Part_Num",
    "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf",
    "MANUFACTURER_NAME", "BRAND_NAME", "TRADE_NAME",
    "MANUFACTURER_PART_NUMBER", "ALTERNATE_PART_NUMBER", "Classpath",
    # Cols 24-29: Multi-Channel Descriptions
    "MOBILE_DESC", "INVOICE_DESC", "SHORT_DESC", "LONG_DESC1",
    "RETAIL_DESC", "MARKETING_DESCRIPTION",
    # Cols 30-55: Features, Approvals, Application, Includes, Product Name
    "ITEM_FEATURES_1", "ITEM_FEATURES_2", "ITEM_FEATURES_3",
    "ITEM_FEATURES_4", "ITEM_FEATURES_5", "ITEM_FEATURES_6",
    "ITEM_FEATURES_7", "ITEM_FEATURES_8", "ITEM_FEATURES_9",
    "ITEM_FEATURES_10", "ITEM_FEATURES_11", "ITEM_FEATURES_12",
    "ITEM_FEATURES_13", "ITEM_FEATURES_14", "ITEM_FEATURES_15",
    "ITEM_FEATURES_16", "ITEM_FEATURES_17", "ITEM_FEATURES_18",
    "ITEM_FEATURES_19", "ITEM_FEATURES_20",
    "With", "Standard/Approvals", "Prop 65", "Application",
    "Includes", "Product Name",
    # Cols 56-205: 50 Attribute Triples (Label, Value, UOM) — INTERLEAVED
    # Real CSV layout: LABEL 1, VALUE 1, UOM 1, LABEL 2, VALUE 2, UOM 2, ...
    *[col for i in range(1, 51)
      for col in (f"ATTRIBUTE_LABEL {i}", f"ATTRIBUTE_VALUE {i}", f"ATTRIBUTE_UOM {i}")],
    # Cols 206-214: Codes, Packaging & Warranty
    "UPC", "EAN", "GTIN", "UNSPSC", "Warranty", "List Price",
    "Selling Qty", "Selling UOM", "Standard Packaging Information",
    # Cols 215-224: Dimensions & Weight
    "LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM",
    "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM",
    "VOLUME", "VOLUME_UOM",
    # Cols 225-252: Digital Assets & Audit Metadata
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

# Sanity check
assert len(DELIVERY_COLUMNS) == 252, (
    f"Delivery schema expected 252 columns, got {len(DELIVERY_COLUMNS)}"
)
