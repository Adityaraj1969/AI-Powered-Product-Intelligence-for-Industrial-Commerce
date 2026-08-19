import re
from typing import List

from src.models import EnrichedProductRecord, ValidationError, ValidationStatus
from src.config import (
    INVOICE_DESC_MAX_LEN,
    MOBILE_DESC_MIN_LEN,
    MOBILE_DESC_MAX_LEN,
    TITLE_DESC_MAX_LEN,
    UNSPSC_DIGITS,
    ALL_PLACEHOLDERS,
    CONFIDENCE_WEIGHT_BRAND,
    CONFIDENCE_WEIGHT_TAXONOMY,
    CONFIDENCE_WEIGHT_ATTRIBUTES,
    CONFIDENCE_WEIGHT_PROVENANCE
)

class Gatekeeper:
    def tier1_syntax(self, record: EnrichedProductRecord) -> List[ValidationError]:
        errors = []
        # Check placeholders
        for field in ["e1_brand", "unilog_brand", "dib_brand", "part_manuf"]:
            val = getattr(record.raw_input, field)
            if val in ALL_PLACEHOLDERS:
                errors.append(ValidationError(
                    tier=1,
                    error_code="PLACEHOLDER_LEAK",
                    severity="HIGH",
                    field_name=field,
                    message=f"Placeholder '{val}' leaked into output."
                ))
        
        # Check character limits
        inv_len = len(record.descriptions.invoice_desc)
        if inv_len > INVOICE_DESC_MAX_LEN:
            errors.append(ValidationError(
                tier=1,
                error_code="INVOICE_TOO_LONG",
                severity="CRITICAL",
                field_name="invoice_desc",
                message=f"Invoice description length {inv_len} exceeds {INVOICE_DESC_MAX_LEN}."
            ))
            
        mob_len = len(record.descriptions.mobile_desc)
        if mob_len < MOBILE_DESC_MIN_LEN or mob_len > MOBILE_DESC_MAX_LEN:
            if mob_len > 0: # Only if it's set
                errors.append(ValidationError(
                    tier=1,
                    error_code="MOBILE_DESC_LENGTH",
                    severity="HIGH",
                    field_name="mobile_desc",
                    message=f"Mobile description length {mob_len} not between {MOBILE_DESC_MIN_LEN}-{MOBILE_DESC_MAX_LEN}."
                ))
            
        title_len = len(record.descriptions.short_desc)
        if title_len > TITLE_DESC_MAX_LEN:
            errors.append(ValidationError(
                tier=1,
                error_code="SHORT_DESC_TOO_LONG",
                severity="HIGH",
                field_name="short_desc",
                message=f"Title length {title_len} exceeds {TITLE_DESC_MAX_LEN}."
            ))
            
        unspsc = record.taxonomy.unspsc_code
        if unspsc and not re.match(r"^\d{8}$", unspsc):
            errors.append(ValidationError(
                tier=1,
                error_code="INVALID_UNSPSC",
                severity="HIGH",
                field_name="unspsc_code",
                message=f"UNSPSC code '{unspsc}' must be exactly 8 digits."
            ))
            
        return errors

    def tier2_lov_membership(self, record: EnrichedProductRecord) -> List[ValidationError]:
        errors = []
        # Stub for brand/manuf LOV check
        return errors

    def tier3_uom_fractions(self, record: EnrichedProductRecord) -> List[ValidationError]:
        errors = []
        # Check UOM spacing (e.g., "10in" -> "10 in")
        for i, attr in enumerate(record.attributes):
            val = attr.normalized_value or attr.raw_value
            if re.search(r"\d[a-zA-Z]", val) and not attr.uom:
                # Naive check for missing space between number and unit
                repaired = re.sub(r"(\d)([a-zA-Z]+)", r"\1 \2", val)
                attr.normalized_value = repaired
                errors.append(ValidationError(
                    tier=3,
                    error_code="MISSING_UOM_SPACE",
                    severity="MEDIUM",
                    field_name=f"attributes[{i}]",
                    message=f"Missing space in UOM '{val}'. Repaired to '{repaired}'.",
                    auto_repair_applied=True,
                    repaired_value=repaired
                ))
        return errors

    def tier4_formula_casing(self, record: EnrichedProductRecord) -> List[ValidationError]:
        errors = []
        inv_desc = record.descriptions.invoice_desc
        if inv_desc and inv_desc != inv_desc.upper():
            repaired = inv_desc.upper()
            record.descriptions.invoice_desc = repaired
            errors.append(ValidationError(
                tier=4,
                error_code="INVOICE_NOT_UPPERCASE",
                severity="MEDIUM",
                field_name="invoice_desc",
                message="Invoice description must be ALL CAPS.",
                auto_repair_applied=True,
                repaired_value=repaired
            ))
        return errors

    def tier5_sourcing_anomaly(self, record: EnrichedProductRecord) -> List[ValidationError]:
        errors = []
        # Check provenance exists
        if record.brand_profile.provenance.sourcing_tier.name == "FALLBACK_NULL" and record.brand_profile.manufacturer_name:
             errors.append(ValidationError(
                tier=5,
                error_code="MISSING_PROVENANCE",
                severity="MEDIUM",
                field_name="brand_profile",
                message="Provenance tier is FALLBACK_NULL but data exists."
            ))
        return errors

    def validate(self, record: EnrichedProductRecord) -> EnrichedProductRecord:
        all_errors = []
        all_errors.extend(self.tier1_syntax(record))
        all_errors.extend(self.tier2_lov_membership(record))
        all_errors.extend(self.tier3_uom_fractions(record))
        all_errors.extend(self.tier4_formula_casing(record))
        all_errors.extend(self.tier5_sourcing_anomaly(record))
        
        record.validation_errors = all_errors
        
        # Determine status
        if not all_errors:
            record.validation_status = ValidationStatus.PASSED
        elif any(e.severity == "CRITICAL" for e in all_errors):
            record.validation_status = ValidationStatus.FAILED
        else:
            record.validation_status = ValidationStatus.AMBER
            
        # Compute confidence score based on weights
        # (This is just a simple mocked aggregation for the sake of the exercise)
        score = (
            record.brand_profile.confidence * CONFIDENCE_WEIGHT_BRAND +
            record.taxonomy.confidence * CONFIDENCE_WEIGHT_TAXONOMY +
            (sum([a.confidence for a in record.attributes]) / max(len(record.attributes), 1)) * CONFIDENCE_WEIGHT_ATTRIBUTES +
            0.9 * CONFIDENCE_WEIGHT_PROVENANCE # Dummy provenance score
        )
        record.overall_confidence = min(score, 1.0)
        record.confidence_level = record.compute_confidence_level()
        
        return record

if __name__ == "__main__":
    from src.models import RawProductInput, CanonicalBrandProfile, MultiChannelDescriptions, ExtractedAttribute, TaxonomyNode
    
    # Deliberately broken record
    raw = RawProductInput(mfg_part_num="123", part_desc="Test", e1_brand="-- Unbranded --")
    record = EnrichedProductRecord(
        sku="TEST-SKU",
        raw_input=raw,
        descriptions=MultiChannelDescriptions(
            invoice_desc="This is too long for an invoice description which should be <= 40 and also lowercase",
            mobile_desc="Too short",
            short_desc="Valid Title"
        ),
        taxonomy=TaxonomyNode(unspsc_code="1234"),
        attributes=[ExtractedAttribute(attribute_label="Length", raw_value="10in", confidence=0.8)]
    )
    
    gk = Gatekeeper()
    gk.validate(record)
    
    print(f"Validation Status: {record.validation_status}")
    print(f"Confidence Level: {record.confidence_level}")
    for err in record.validation_errors:
        print(f"[{err.severity}] Tier {err.tier}: {err.error_code} - {err.message} (Repaired: {err.auto_repair_applied})")
