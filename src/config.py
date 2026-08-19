"""
PartForge Configuration — Centralized paths, constants, and delivery schema.

All 252 delivery column names are sourced directly from the verified
`Unihack_ Expected Output - Delivery Format.csv` header row.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Dynamic Robust Project Root ───────────────────────────────────────────────
def find_project_root() -> Path:
    p = Path(__file__).resolve().parent
    for _ in range(4):
        if (p / "src").exists() and (p / "data").exists():
            return p
        p = p.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
EVAL_DIR = PROJECT_ROOT / "eval"
OUTPUT_DIR = PROJECT_ROOT / "output"

# ── High-Performance API Configuration ────────────────────────────────────────
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

# ── Quality Gatekeeper Thresholds ────────────────────────────────────────────
CONFIDENCE_AUTO_PASS = 0.95   # Green tier threshold
CONFIDENCE_AMBER = 0.80       # Amber tier threshold

# ── Content Field Constraints (Unilog Rules) ──────────────────────────────────
INVOICE_DESC_MAX_LEN = 40
MOBILE_DESC_MIN_LEN = 60
MOBILE_DESC_MAX_LEN = 80
TITLE_DESC_MAX_LEN = 150
UNSPSC_DIGITS = 8

# ── Confidence Scoring Weights ───────────────────────────────────────────────
CONFIDENCE_WEIGHT_BRAND = 0.20
CONFIDENCE_WEIGHT_TAXONOMY = 0.25
CONFIDENCE_WEIGHT_ATTRIBUTES = 0.35
CONFIDENCE_WEIGHT_PROVENANCE = 0.20

# ── Full 252 Delivery Column Names (Verified Ground Truth) ───────────────────
DELIVERY_COLUMNS = [
    'MFR URL', 'Ref URL 1', 'Ref URL 2', 'Ref URL 3', 'Ref URL 4', 'Ref URL 5',
    'PART_NUMBER', 'Dept', 'Class', 'Fine', 'SKU - MY_PART_NUMBER', 'Mfg_Part_Num',
    'Part_Desc', 'E1_Brand', 'Unilog_Brand', 'DIB_Brand', 'Part_Manuf',
    'MANUFACTURER_NAME', 'BRAND_NAME', 'TRADE_NAME', 'MANUFACTURER_PART_NUMBER',
    'ALTERNATE_PART_NUMBER', 'Classpath', 'MOBILE_DESC', 'INVOICE_DESC',
    'SHORT_DESC', 'LONG_DESC1', 'RETAIL_DESC', 'MARKETING_DESCRIPTION',
    'ITEM_FEATURES_1', 'ITEM_FEATURES_2', 'ITEM_FEATURES_3', 'ITEM_FEATURES_4',
    'ITEM_FEATURES_5', 'ITEM_FEATURES_6', 'ITEM_FEATURES_7', 'ITEM_FEATURES_8',
    'ITEM_FEATURES_9', 'ITEM_FEATURES_10', 'ITEM_FEATURES_11', 'ITEM_FEATURES_12',
    'ITEM_FEATURES_13', 'ITEM_FEATURES_14', 'ITEM_FEATURES_15', 'ITEM_FEATURES_16',
    'ITEM_FEATURES_17', 'ITEM_FEATURES_18', 'ITEM_FEATURES_19', 'ITEM_FEATURES_20',
    'With', 'Standard/Approvals', 'Prop 65', 'Application', 'Includes', 'Product Name',
]

# Add 50 attribute triples (150 columns) — interleaved: LABEL, VALUE, UOM
for _i in range(1, 51):
    DELIVERY_COLUMNS.extend([
        f'ATTRIBUTE_LABEL {_i}',
        f'ATTRIBUTE_VALUE {_i}',
        f'ATTRIBUTE_UOM {_i}',
    ])

# Remaining post-attribute columns (46 columns)
DELIVERY_COLUMNS.extend([
    'UPC', 'EAN', 'GTIN', 'UNSPSC', 'Warranty', 'List Price',
    'Selling Qty', 'Selling UOM', 'Standard Packaging Information',
    'LENGTH', 'LENGTH_UOM', 'HEIGHT', 'HEIGHT_UOM',
    'WIDTH', 'WIDTH_UOM', 'WEIGHT', 'WEIGHT_UOM',
    'VOLUME', 'VOLUME_UOM',
    'Product Image',
    'Alternate Image 1', 'Alternate Image 2', 'Alternate Image 3', 'Alternate Image 4',
    'SDS', 'SDS_1', 'Warranty Information', 'Catalog',
    'Specification Sheet', 'Instruction/Installation Manual',
    'Service Manual', 'Owners/User Manual', 'Line Drawing',
    'MTR', 'RoHS', 'Full Engineering Drawing', 'Energy Star Guide',
    'Technical Bulletin', 'Submittal', 'Compatibility Chart',
    'Size Chart', 'Product Label/Insert',
    'Video Link', 'Video Link 1',
    'Country Of Origin', 'Discontinued', 'Actual Image (Yes/No)',
])

assert len(DELIVERY_COLUMNS) == 252, f"Expected 252 columns, got {len(DELIVERY_COLUMNS)}"
