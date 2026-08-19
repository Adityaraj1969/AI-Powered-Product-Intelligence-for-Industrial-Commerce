"""
PartForge Ingestion & AI Enrichment Pipeline.

Loads raw catalog items, applies placeholder stripping, resolves canonical brands,
infers taxonomy/UNSPSC, extracts structured technical attributes, synthesizes 5-channel
descriptions, and runs 5-tier gatekeeper validation.
"""

import sys
import os
from pathlib import Path
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ingestion.parser import load_input_csv
from src.knowledge.placeholder import strip_placeholders, resolve_brand_fallback
from src.models import EnrichedProductRecord, CanonicalBrandProfile, RawProductInput
from src.ai.taxonomy_classifier import TaxonomyClassifier
from src.ai.attribute_extractor import AttributeExtractor
from src.ai.description_builder import DescriptionBuilder
from src.rules.gatekeeper import Gatekeeper


def enrich_single_item(
    raw: RawProductInput,
    classifier: TaxonomyClassifier = None,
    extractor: AttributeExtractor = None,
    builder: DescriptionBuilder = None,
    gatekeeper: Gatekeeper = None,
) -> EnrichedProductRecord:
    """Enriches a single raw catalog item through all pipeline layers."""
    classifier = classifier or TaxonomyClassifier()
    extractor = extractor or AttributeExtractor()
    builder = builder or DescriptionBuilder()
    gatekeeper = gatekeeper or Gatekeeper()

    # 1. Clean placeholders
    cleaned = strip_placeholders(raw)

    # 2. Resolve canonical brand & manufacturer
    brand_name = resolve_brand_fallback(cleaned) or "UNBRANDED"
    manuf_name = brand_name
    if cleaned.part_manuf:
        import re
        clean_manuf = re.sub(r'\s*\([^)]*\)$', '', cleaned.part_manuf).strip()
        if clean_manuf:
            manuf_name = clean_manuf

    # Special brand canonicalization mapping for key suppliers
    text_check = f"{cleaned.part_desc} {cleaned.mfg_part_num}".upper()
    trade_brand = brand_name
    if "FRIGIDAIRE" in text_check or "PDSH" in text_check:
        trade_brand = "FRIGIDAIRE®"
        manuf_name = "Rheem Manufacturing"
    elif "DIABLO" in text_check or "FREUD" in text_check:
        trade_brand = "DIABLO®"
        manuf_name = "Freud Inc"
    elif "MILW" in text_check or "MILWAUKEE" in text_check:
        trade_brand = "MILWAUKEE®"
        manuf_name = "Milwaukee Electric Tool"
    elif "TREX" in text_check:
        trade_brand = "TREX®"
        manuf_name = "Trex Company Inc"
    elif "DEWALT" in text_check:
        trade_brand = "DEWALT®"
        manuf_name = "Stanley Black & Decker"
    elif "MAKITA" in text_check:
        trade_brand = "MAKITA®"
        manuf_name = "Makita USA Inc"
    elif "MOEN" in text_check:
        trade_brand = "MOEN®"
        manuf_name = "Fortune Brands"
    elif "PARKER" in text_check:
        trade_brand = "PARKER®"
        manuf_name = "Parker Hannifin Corp"

    # 3. Create UPIR Record
    record = EnrichedProductRecord(
        sku=cleaned.mfg_part_num,
        raw_input=cleaned,
    )
    record.brand_profile = CanonicalBrandProfile(
        manufacturer_name=manuf_name,
        brand_name=trade_brand,
        confidence=0.96,
        trademark_retained="®" in trade_brand or "™" in trade_brand,
    )

    # 4. Taxonomy & UNSPSC
    record.taxonomy = classifier.classify(cleaned.part_desc, cleaned.mfg_part_num, trade_brand)

    # 5. Extract structured attributes
    record.attributes = extractor.extract_from_description(cleaned.part_desc, cleaned.mfg_part_num)

    # 6. Synthesize 5-channel descriptions
    record.descriptions = builder.build_all(record)

    # 7. Validate through 5-tier gatekeeper
    record = gatekeeper.validate(record)

    # 8. Compute calibrated confidence level
    record.confidence_level = record.compute_confidence_level()

    return record


def ingest_raw_items(path: Path) -> List[EnrichedProductRecord]:
    """
    Ingests and fully enriches raw catalog items from CSV/Excel.
    """
    raw_inputs = load_input_csv(path)
    classifier = TaxonomyClassifier()
    extractor = AttributeExtractor()
    builder = DescriptionBuilder()
    gatekeeper = Gatekeeper()

    enriched_records = []
    for raw in raw_inputs:
        record = enrich_single_item(raw, classifier, extractor, builder, gatekeeper)
        enriched_records.append(record)

    return enriched_records


if __name__ == "__main__":
    test_path = Path("data/Unihack_ Sample Dataset - Input.csv")
    if test_path.exists():
        records = ingest_raw_items(test_path)
        print(f"\nSuccessfully enriched {len(records)} items!")
        for r in records[:3]:
            print(f"\nMPN: {r.raw_input.mfg_part_num}")
            print(f"  Brand:        {r.brand_profile.brand_name}")
            print(f"  Manufacturer: {r.brand_profile.manufacturer_name}")
            print(f"  Classpath:    {r.taxonomy.classpath}")
            print(f"  UNSPSC:       {r.taxonomy.unspsc_code}")
            print(f"  Invoice Desc: {r.descriptions.invoice_desc} ({len(r.descriptions.invoice_desc)} chars)")
            print(f"  Mobile Desc:  {r.descriptions.mobile_desc} ({len(r.descriptions.mobile_desc)} chars)")
            print(f"  Short Desc:   {r.descriptions.short_desc}")
            print(f"  Attributes:   {len(r.attributes)} extracted")
            print(f"  Confidence:   {r.overall_confidence:.0%} ({r.confidence_level.value})")
    else:
        print(f"Test path {test_path} does not exist.")
