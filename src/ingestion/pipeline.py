"""
PartForge Ingestion Pipeline — Loads raw items, strips placeholders, and initializes UPIR records.
"""

import sys
import os
from pathlib import Path
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ingestion.parser import load_input_csv
from src.knowledge.placeholder import strip_placeholders, resolve_brand_fallback
from src.models import EnrichedProductRecord, CanonicalBrandProfile, RawProductInput


def ingest_raw_items(path: Path) -> List[EnrichedProductRecord]:
    """
    Ingests raw catalog items from CSV/Excel, cleans placeholders,
    and initializes CanonicalBrandProfile and EnrichedProductRecord.
    """
    raw_inputs = load_input_csv(path)
    enriched_records = []
    
    for raw in raw_inputs:
        # Strip placeholders from brand fields
        cleaned_raw = strip_placeholders(raw)
        
        # Resolve brand name using fallback hierarchy
        brand_name = resolve_brand_fallback(cleaned_raw) or "UNKNOWN"
        
        # Initialize UPIR record
        record = EnrichedProductRecord(
            sku=cleaned_raw.mfg_part_num,
            raw_input=cleaned_raw,
        )
        record.brand_profile = CanonicalBrandProfile(
            manufacturer_name=brand_name,
            brand_name=brand_name,
            confidence=0.90 if brand_name != "UNKNOWN" else 0.30,
        )
        enriched_records.append(record)
        
    return enriched_records


if __name__ == "__main__":
    test_path = Path("data/Unihack_ Sample Dataset - Input.csv")
    if test_path.exists():
        records = ingest_raw_items(test_path)
        print(f"Loaded and initialized {len(records)} records.")
        for r in records[:5]:
            print(f"MPN: {r.raw_input.mfg_part_num:20s} | Brand: {r.brand_profile.brand_name}")
    else:
        print(f"Test path {test_path} does not exist.")
