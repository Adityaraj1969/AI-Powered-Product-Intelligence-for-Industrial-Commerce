"""
PartForge — Main CLI Entry Point.

Usage:
    python main.py enrich-single --mpn "PDSH4816AF" --desc "PDSH4816AF Dishwasher SS"
    python main.py enrich-batch --input data/input.csv --output output/delivery.csv
    python main.py evaluate --ground-truth data/gt.csv --predictions output/delivery.csv
    python main.py ui
"""

import sys
import argparse
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def cmd_enrich_single(args):
    """Enrich a single product record."""
    from src.models import RawProductInput, EnrichedProductRecord
    from src.knowledge.placeholder import strip_placeholders, resolve_brand_fallback
    from src.knowledge.fraction_matrix import convert_dimension
    from src.knowledge.uom_engine import format_measurement
    from src.ai.description_builder import DescriptionBuilder

    raw = RawProductInput(
        mfg_part_num=args.mpn,
        part_desc=args.desc,
        e1_brand=args.brand,
        unilog_brand=None,
        dib_brand=None,
        part_manuf=args.manuf,
    )

    # Strip placeholders
    raw = strip_placeholders(raw)

    # Resolve brand fallback
    brand_name = resolve_brand_fallback(raw)

    # Create enriched record
    record = EnrichedProductRecord(
        sku=raw.mfg_part_num,
        raw_input=raw,
    )
    record.brand_profile.manufacturer_name = brand_name
    record.brand_profile.brand_name = brand_name
    record.brand_profile.confidence = 0.90

    # Build descriptions
    builder = DescriptionBuilder()
    record.descriptions = builder.build_all(record)

    # Print result
    print("\n" + "=" * 60)
    print("PARTFORGE ENRICHMENT RESULT")
    print("=" * 60)
    print(f"MPN:              {record.raw_input.mfg_part_num}")
    print(f"Brand:            {record.brand_profile.brand_name}")
    print(f"Manufacturer:     {record.brand_profile.manufacturer_name}")
    print(f"Invoice Desc:     {record.descriptions.invoice_desc} ({len(record.descriptions.invoice_desc)} chars)")
    print(f"Mobile Desc:      {record.descriptions.mobile_desc} ({len(record.descriptions.mobile_desc)} chars)")
    print(f"Short Desc:       {record.descriptions.short_desc} ({len(record.descriptions.short_desc)} chars)")
    print(f"Long Desc:        {record.descriptions.long_desc[:100]}...")
    print(f"Confidence:       {record.overall_confidence:.0%}")
    print("=" * 60)

    return record


def cmd_enrich_batch(args):
    """Batch enrich all items from a CSV file."""
    from src.ingestion.parser import load_input_csv
    from src.ingestion.pipeline import ingest_raw_items
    from src.ai.description_builder import DescriptionBuilder
    from src.rules.gatekeeper import Gatekeeper
    from src.export.delivery_exporter import DeliveryExporter

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading input: {input_path}")
    records = ingest_raw_items(input_path)
    print(f"Loaded {len(records)} records")

    # Build descriptions for each record
    builder = DescriptionBuilder()
    gatekeeper = Gatekeeper()

    for i, record in enumerate(records):
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(records)}...")
        record.descriptions = builder.build_all(record)
        record = gatekeeper.validate(record)
        records[i] = record

    # Export
    exporter = DeliveryExporter()
    if output_path.suffix == ".xlsx":
        exporter.export_to_excel(records, output_path)
    else:
        exporter.export_to_csv(records, output_path)

    print(f"\nExported {len(records)} records to {output_path}")

    # Print summary
    from src.models import ConfidenceLevel
    green = sum(1 for r in records if r.confidence_level == ConfidenceLevel.GREEN)
    amber = sum(1 for r in records if r.confidence_level == ConfidenceLevel.AMBER)
    red = sum(1 for r in records if r.confidence_level == ConfidenceLevel.RED)
    print(f"  [GREEN] Auto-pass: {green}")
    print(f"  [AMBER] Triage:    {amber}")
    print(f"  [ RED ] Review:    {red}")


def cmd_evaluate(args):
    """Run evaluation benchmark."""
    sys.path.insert(0, str(PROJECT_ROOT / "eval"))
    from eval.run_eval import BenchmarkEvaluator

    evaluator = BenchmarkEvaluator(args.ground_truth, args.predictions)
    evaluator.print_scorecard()


def cmd_ui(args):
    """Launch the Streamlit HITL dashboard."""
    import subprocess
    app_path = PROJECT_ROOT / "src" / "ui" / "app.py"
    print(f"Launching PartForge Dashboard: {app_path}")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


def main():
    parser = argparse.ArgumentParser(
        description="PartForge — AI-Powered Product Intelligence Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py enrich-single --mpn "PDSH4816AF" --desc "Dishwasher SS"
  python main.py enrich-batch --input data/input.csv --output output/delivery.csv
  python main.py evaluate --ground-truth data/gt.csv --predictions output/pred.csv
  python main.py ui
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # enrich-single
    p_single = subparsers.add_parser("enrich-single", help="Enrich a single product")
    p_single.add_argument("--mpn", required=True, help="Manufacturer Part Number")
    p_single.add_argument("--desc", required=True, help="Raw part description")
    p_single.add_argument("--brand", default=None, help="Brand name (or placeholder)")
    p_single.add_argument("--manuf", default=None, help="Manufacturer name")

    # enrich-batch
    p_batch = subparsers.add_parser("enrich-batch", help="Batch enrich from CSV")
    p_batch.add_argument("--input", required=True, help="Input CSV path")
    p_batch.add_argument("--output", required=True, help="Output CSV/XLSX path")

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Run benchmark evaluation")
    p_eval.add_argument("--ground-truth", required=True, help="Ground truth CSV/XLSX")
    p_eval.add_argument("--predictions", required=True, help="Predictions CSV/XLSX")

    # ui
    p_ui = subparsers.add_parser("ui", help="Launch Streamlit dashboard")

    args = parser.parse_args()

    if args.command == "enrich-single":
        cmd_enrich_single(args)
    elif args.command == "enrich-batch":
        cmd_enrich_batch(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "ui":
        cmd_ui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
