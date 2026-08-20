"""
PartForge Ingestion Pipeline — Loads, cleans, enriches, and validates raw items.
"""

from pathlib import Path
from typing import List

from src.models import (
    CanonicalBrandProfile,
    ConfidenceLevel,
    EnrichedProductRecord,
    RawProductInput,
    ValidationStatus,
)
from src.ingestion.parser import load_input_csv
from src.knowledge.placeholder import strip_placeholders
from src.knowledge.brand_trie import BrandMatcher
from src.ai.taxonomy_classifier import TaxonomyClassifier
from src.ai.attribute_extractor import AttributeExtractor
from src.ai.description_builder import DescriptionBuilder
from src.rules.gatekeeper import Gatekeeper


def enrich_single_item(
    raw: RawProductInput,
    brand_matcher: BrandMatcher = None,
    classifier: TaxonomyClassifier = None,
    extractor: AttributeExtractor = None,
    builder: DescriptionBuilder = None,
    gatekeeper: Gatekeeper = None,
) -> EnrichedProductRecord:
    """Enriches a single raw catalog item through all pipeline layers."""
    brand_matcher = brand_matcher or BrandMatcher()
    classifier = classifier or TaxonomyClassifier()
    extractor = extractor or AttributeExtractor()
    builder = builder or DescriptionBuilder()
    gatekeeper = gatekeeper or Gatekeeper()

    # 1. Clean placeholders
    cleaned = strip_placeholders(raw)

    # 2. Create UPIR Record
    record = EnrichedProductRecord(
        sku=cleaned.mfg_part_num,
        raw_input=cleaned,
    )

    # 3. Resolve canonical brand & manufacturer (filters distributors)
    record.brand_profile = brand_matcher.match(
        raw_desc=cleaned.part_desc,
        raw_mpn=cleaned.mfg_part_num,
        raw_brand=cleaned.e1_brand,
        raw_manuf=cleaned.part_manuf,
        unilog_brand=cleaned.unilog_brand,
        dib_brand=cleaned.dib_brand,
    )

    # 4. Taxonomy & UNSPSC
    record.taxonomy = classifier.classify(record)

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
    brand_matcher = BrandMatcher()
    classifier = TaxonomyClassifier()
    extractor = AttributeExtractor()
    builder = DescriptionBuilder()
    gatekeeper = Gatekeeper()

    records = []
    for raw in raw_inputs:
        record = enrich_single_item(
            raw,
            brand_matcher=brand_matcher,
            classifier=classifier,
            extractor=extractor,
            builder=builder,
            gatekeeper=gatekeeper,
        )
        records.append(record)

    return records
