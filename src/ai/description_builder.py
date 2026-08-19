"""
PartForge Multi-Channel Description Builder.

Generates 5 description formats per Unilog Content Guidelines:
  1. Invoice Desc: <=40 chars, ALL CAPS
  2. Mobile Desc: 60-80 chars, Title Case
  3. Short Desc / Product Title: <=150 chars, Title Case, preserves (R) (TM)
  4. Long Description: Full technical narrative
  5. Feature Bullets: PDP highlights
"""

import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models import EnrichedProductRecord, MultiChannelDescriptions


# Abbreviation dictionary for invoice compression
ABBREV_DICT = {
    "DISHWASHER": "DISHW",
    "STAINLESS STEEL": "SST",
    "STAINLESS": "SST",
    "COUPLING": "CPLG",
    "ELBOW": "ELB",
    "ADAPTER": "ADPT",
    "ASSEMBLY": "ASSY",
    "BEARING": "BRG",
    "BRACKET": "BRKT",
    "BUSHING": "BUSH",
    "CYLINDER": "CYL",
    "COMMERCIAL": "COMM",
    "RESIDENTIAL": "RES",
    "INDUSTRIAL": "IND",
    "PROFESSIONAL": "PRO",
    "GALVANIZED": "GALV",
    "CHROME": "CHR",
    "MOUNTING": "MTG",
    "CONNECTOR": "CONN",
    "REGULATOR": "REG",
    "COMPRESSOR": "COMPR",
    "REFRIGERATOR": "REFRIG",
    "TEMPERATURE": "TEMP",
    "ELECTRICAL": "ELEC",
}


class DescriptionBuilder:
    """Generates all 5 multi-channel descriptions from an enriched record."""

    def __init__(self):
        self.abbrev_dict = ABBREV_DICT

    def _get_brand(self, record: EnrichedProductRecord) -> str:
        return record.brand_profile.brand_name or record.brand_profile.manufacturer_name or ""

    def _get_manuf(self, record: EnrichedProductRecord) -> str:
        return record.brand_profile.manufacturer_name or ""

    def _get_mpn(self, record: EnrichedProductRecord) -> str:
        return record.raw_input.mfg_part_num or ""

    def _get_desc(self, record: EnrichedProductRecord) -> str:
        return record.raw_input.part_desc or ""

    def _apply_abbreviations(self, text: str) -> str:
        for full, abbr in self.abbrev_dict.items():
            text = re.sub(rf'\b{re.escape(full)}\b', abbr, text, flags=re.IGNORECASE)
        return text

    def _strip_trademark_symbols(self, text: str) -> str:
        return text.replace("®", "").replace("™", "").replace("(R)", "").replace("(TM)", "")

    def build_invoice_desc(self, record: EnrichedProductRecord) -> str:
        """Invoice Description: <=40 chars, ALL CAPS, no punctuation."""
        brand = self._strip_trademark_symbols(self._get_brand(record))
        desc = self._get_desc(record)

        mpn = self._get_mpn(record)
        if desc.upper().startswith(mpn.upper()):
            desc = desc[len(mpn):].strip()

        invoice = f"{desc}".upper()
        invoice = self._apply_abbreviations(invoice)
        invoice = re.sub(r'\s+', ' ', invoice).strip()

        if len(invoice) > 40:
            invoice = invoice[:40].rsplit(' ', 1)[0]

        return invoice.upper()

    def build_mobile_desc(self, record: EnrichedProductRecord) -> str:
        """Mobile Description: 60-80 chars, Title Case."""
        manuf = self._get_manuf(record)
        brand = self._get_brand(record)
        desc = self._get_desc(record)
        mpn = self._get_mpn(record)

        clean_desc = desc
        if clean_desc.upper().startswith(mpn.upper()):
            clean_desc = clean_desc[len(mpn):].strip()
        clean_desc = re.sub(r'\s*-\s*', ', ', clean_desc)

        if manuf and brand and manuf != brand:
            mobile = f"{manuf} {brand}, {clean_desc}, {mpn}"
        elif brand:
            mobile = f"{brand}, {clean_desc}, {mpn}"
        else:
            mobile = f"{clean_desc}, {mpn}"

        mobile = mobile.title()

        if len(mobile) > 80:
            mobile = mobile[:80].rsplit(',', 1)[0].strip()
        elif len(mobile) < 60:
            if manuf and manuf not in mobile:
                mobile = f"{manuf}, {mobile}"
            if len(mobile) < 60:
                mobile = mobile + ", " + mpn[:60 - len(mobile) - 2]

        return mobile[:80]

    def build_short_desc(self, record: EnrichedProductRecord) -> str:
        """Short Description / Product Title: <=150 chars, Title Case, (R)(TM) preserved."""
        brand = self._get_brand(record)
        desc = self._get_desc(record)
        mpn = self._get_mpn(record)

        clean_desc = desc
        if clean_desc.upper().startswith(mpn.upper()):
            clean_desc = clean_desc[len(mpn):].strip()

        parts = [brand, mpn, clean_desc]
        title = " ".join(p for p in parts if p)
        title = title.title()
        title = re.sub(r'\s+', ' ', title).strip()

        return title[:150]

    def build_long_desc(self, record: EnrichedProductRecord) -> str:
        """Long Description: Full technical narrative without duplicate units."""
        brand = self._get_brand(record)
        desc = self._get_desc(record)
        mpn = self._get_mpn(record)

        parts = []
        if brand:
            parts.append(brand)
        parts.append(desc)
        if mpn and mpn not in desc:
            parts.append(f"Part Number: {mpn}")

        for attr in record.attributes:
            val = str(attr.normalized_value or attr.raw_value).strip()
            uom = attr.uom.strip() if attr.uom else ""
            
            # Prevent duplicate unit suffix (e.g. 18 in in)
            if uom and not val.endswith(uom) and uom not in val:
                val_display = f"{val} {uom}"
            else:
                val_display = val
                
            label = attr.normalized_label or attr.attribute_label
            parts.append(f"{label}: {val_display}")

        return ", ".join(parts)

    def build_feature_bullets(self, record: EnrichedProductRecord) -> list:
        """Feature Bullets: PDP marketing highlights without duplicate units."""
        bullets = []
        for attr in record.attributes[:20]:
            val = str(attr.normalized_value or attr.raw_value).strip()
            uom = attr.uom.strip() if attr.uom else ""
            if uom and not val.endswith(uom) and uom not in val:
                val_display = f"{val} {uom}"
            else:
                val_display = val
            label = attr.normalized_label or attr.attribute_label
            bullets.append(f"{label}: {val_display}")
        return bullets

    def build_all(self, record: EnrichedProductRecord) -> MultiChannelDescriptions:
        """Build all 5 description formats."""
        return MultiChannelDescriptions(
            invoice_desc=self.build_invoice_desc(record),
            mobile_desc=self.build_mobile_desc(record),
            short_desc=self.build_short_desc(record),
            long_desc=self.build_long_desc(record),
            retail_desc=self.build_short_desc(record),
            marketing_desc=self.build_long_desc(record),
            feature_bullets=self.build_feature_bullets(record),
        )


if __name__ == "__main__":
    from src.models import RawProductInput, CanonicalBrandProfile, ExtractedAttribute

    raw = RawProductInput(
        mfg_part_num="DCB518ASTS06G",
        part_desc="DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc",
        e1_brand=None,
        part_manuf="Freud Inc (2435)",
    )
    record = EnrichedProductRecord(sku="DCB518ASTS06G", raw_input=raw)
    record.brand_profile = CanonicalBrandProfile(
        manufacturer_name="Freud Inc",
        brand_name="DIABLO®",
        confidence=0.95,
    )
    record.attributes = [
        ExtractedAttribute(attribute_label="Package Quantity", normalized_value="6", uom="pc"),
        ExtractedAttribute(attribute_label="Dimensions", normalized_value="1/2 in x 18 in", uom="in"),
    ]

    builder = DescriptionBuilder()
    descs = builder.build_all(record)

    print("Long Desc:", descs.long_desc)
    print("Bullets:  ", descs.feature_bullets)
    assert "18 in in" not in descs.long_desc
    print("Unit formatting verified!")
