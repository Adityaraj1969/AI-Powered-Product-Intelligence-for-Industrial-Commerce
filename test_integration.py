"""Full integration test: Ingest -> Enrich -> Validate -> Export."""

import sys
sys.path.insert(0, ".")

from pathlib import Path
from src.ingestion.parser import load_input_csv
from src.knowledge.placeholder import strip_placeholders, resolve_brand_fallback
from src.knowledge.fraction_matrix import convert_dimension
from src.knowledge.uom_engine import standardize_uom, format_measurement
from src.ai.description_builder import DescriptionBuilder
from src.rules.gatekeeper import Gatekeeper
from src.export.delivery_exporter import DeliveryExporter
from src.models import (
    EnrichedProductRecord, CanonicalBrandProfile, TaxonomyNode,
    ExtractedAttribute, ProvenanceRecord, SourcingTier, ConfidenceLevel
)
from src.config import DELIVERY_COLUMNS

print("=" * 60)
print("PARTFORGE INTEGRATION TEST")
print("=" * 60)

# 1. Load input
print("\n[1/6] Loading input CSV...")
records_raw = load_input_csv(Path("data/Unihack_ Sample Dataset - Input.csv"))
print(f"  Loaded {len(records_raw)} raw records")

# 2. Process first 10 items through full pipeline
print("\n[2/6] Processing first 10 items through pipeline...")
builder = DescriptionBuilder()
gatekeeper = Gatekeeper()
enriched_records = []

for i, raw in enumerate(records_raw[:10]):
    # Strip placeholders
    cleaned = strip_placeholders(raw)
    
    # Resolve brand
    brand_name = resolve_brand_fallback(cleaned)
    
    # Create enriched record
    record = EnrichedProductRecord(
        sku=cleaned.mfg_part_num,
        raw_input=cleaned,
    )
    record.brand_profile = CanonicalBrandProfile(
        manufacturer_name=brand_name,
        brand_name=brand_name,
        confidence=0.90,
    )
    
    # Build descriptions
    record.descriptions = builder.build_all(record)
    
    # Validate through gatekeeper
    record = gatekeeper.validate(record)
    
    enriched_records.append(record)
    
    # Print summary
    level_tag = {"GREEN": "[GREEN]", "AMBER": "[AMBER]", "RED": "[ RED ]"}.get(record.confidence_level.value, "[????]")
    inv_len = len(record.descriptions.invoice_desc) if record.descriptions.invoice_desc else 0
    mob_len = len(record.descriptions.mobile_desc) if record.descriptions.mobile_desc else 0
    print(f"  {level_tag} [{i+1:2d}] MPN={record.raw_input.mfg_part_num[:20]:20s} | "
          f"Brand={record.brand_profile.brand_name[:20]:20s} | "
          f"Inv={inv_len:2d}/40 | Mob={mob_len:2d}/80 | "
          f"Conf={record.overall_confidence:.0%} | "
          f"Errs={len(record.validation_errors)}")

# 3. Export to CSV
print("\n[3/6] Exporting to 252-column CSV...")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
exporter = DeliveryExporter()
exporter.export_to_csv(enriched_records, output_dir / "test_delivery.csv")

# 4. Verify CSV columns
print("\n[4/6] Verifying export column count...")
import pandas as pd
df_out = pd.read_csv(output_dir / "test_delivery.csv")
print(f"  Output columns: {len(df_out.columns)} (expected: 252)")
assert len(df_out.columns) == 252, f"Column count mismatch: {len(df_out.columns)} != 252"
print(f"  Output rows: {len(df_out)}")

# 5. Fraction matrix extra tests
print("\n[5/6] Testing fraction matrix edge cases...")
tests = [
    (50.25, "in", "50-1/4 in"),
    (0.375, "in", "3/8 in"),
    (24.0, "in", "24 in"),
    (24.75, "in", "24-3/4 in"),
    (0.5, "in", "1/2 in"),
    (0.015625, "in", "1/64 in"),
    (12.0625, "in", "12-1/16 in"),
]
all_pass = True
for val, uom, expected in tests:
    result = convert_dimension(val, uom)
    status = "OK" if result == expected else "FAIL"
    if result != expected:
        all_pass = False
    print(f"  {status} convert_dimension({val}, '{uom}') = '{result}' (expected '{expected}')")

# 6. Summary
print("\n" + "=" * 60)
print("INTEGRATION TEST RESULTS")
print("=" * 60)
print(f"  Records loaded:     {len(records_raw)}")
print(f"  Records enriched:   {len(enriched_records)}")
print(f"  Export columns:     {len(df_out.columns)} / 252 OK")
print(f"  Fraction tests:     {'ALL PASS' if all_pass else 'SOME FAILED'}")

green = sum(1 for r in enriched_records if r.confidence_level == ConfidenceLevel.GREEN)
amber = sum(1 for r in enriched_records if r.confidence_level == ConfidenceLevel.AMBER)
red = sum(1 for r in enriched_records if r.confidence_level == ConfidenceLevel.RED)
print(f"  Green:              {green}")
print(f"  Amber:              {amber}")
print(f"  Red:                {red}")
print("=" * 60)
print("INTEGRATION TEST COMPLETE!")
