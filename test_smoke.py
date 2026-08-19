"""Quick smoke test for all PartForge knowledge plane modules."""

import sys
sys.path.insert(0, ".")

# Test 1: Placeholder stripping
print("=== TEST 1: Placeholder Stripping ===")
from src.knowledge.placeholder import is_placeholder, strip_placeholders, resolve_brand_fallback
from src.models import RawProductInput

print(f'is_placeholder("-- Unbranded --"): {is_placeholder("-- Unbranded --")}')
print(f'is_placeholder("FRIGIDAIRE"): {is_placeholder("FRIGIDAIRE")}')
print(f'is_placeholder("-- No Unilog Brand --"): {is_placeholder("-- No Unilog Brand --")}')

raw = RawProductInput(
    mfg_part_num="PDSH4816AF",
    part_desc="PDSH4816AF Dishwasher SS",
    e1_brand="-- Unbranded --",
    unilog_brand="-- No Unilog Brand --",
    dib_brand="-- No DIB Brand --",
    part_manuf="Appliance Dealers Cooperative (APPDE)",
)
cleaned = strip_placeholders(raw)
print(f"After strip: e1_brand={cleaned.e1_brand}, unilog={cleaned.unilog_brand}")
fallback = resolve_brand_fallback(cleaned)
print(f"Brand fallback: {fallback}")
print()

# Test 2: Fraction Matrix
print("=== TEST 2: Fraction Matrix ===")
from src.knowledge.fraction_matrix import convert_dimension
tests = [(50.25, "in"), (0.375, "in"), (24.0, "in"), (24.75, "in"), (0.5, "in")]
for val, uom in tests:
    result = convert_dimension(val, uom)
    print(f"  {val} {uom} -> {result}")
print()

# Test 3: UOM Engine
print("=== TEST 3: UOM Engine ===")
from src.knowledge.uom_engine import standardize_uom, format_measurement
uom_tests = [("inches", "in"), ("GPM", "gpm"), ("Volts", "V"), ("PSI", "psi")]
for raw_uom, expected in uom_tests:
    result = standardize_uom(raw_uom)
    print(f'  standardize_uom("{raw_uom}") -> "{result}" (expected: "{expected}")')

fmt_tests = [(24, "inches"), (120, "Volts"), (1.5, "GPM")]
for val, uom in fmt_tests:
    result = format_measurement(val, uom)
    print(f'  format_measurement({val}, "{uom}") -> "{result}"')
print()

# Test 4: Ingestion parser
print("=== TEST 4: Ingestion Parser ===")
from src.ingestion.parser import load_input_csv
from pathlib import Path
records = load_input_csv(Path("data/Unihack_ Sample Dataset - Input.csv"))
print(f"Loaded {len(records)} records from input CSV")
for r in records[:3]:
    print(f"  MPN={r.mfg_part_num}, Desc={r.part_desc[:50]}, Brand={r.e1_brand}")
print()

print("ALL TESTS PASSED!")
