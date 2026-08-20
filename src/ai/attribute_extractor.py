"""
PartForge Attribute Extraction Engine.

Extracts technical specifications, units, dimensions, and controlled LOV values
from raw catalog descriptions and technical cut-sheets.
"""

import sys
import os
import re
from typing import List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models import EnrichedProductRecord, ExtractedAttribute, ProvenanceRecord, SourcingTier
from src.knowledge.fraction_matrix import convert_dimension
from src.knowledge.uom_engine import standardize_uom


class AttributeExtractor:
    """Extracts standardized industrial attributes from descriptions and specs."""

    def __init__(self):
        pass

    def extract_from_description(self, part_desc: str, mfg_part_num: str = "") -> List[ExtractedAttribute]:
        """Heuristic rule-based attribute extraction engine."""
        attributes: List[ExtractedAttribute] = []
        seen_labels = set()

        def add_attr(label: str, raw_val: str, norm_val: str, uom: Optional[str] = None, tier: SourcingTier = SourcingTier.CONTENT_GUIDELINES):
            if label not in seen_labels and norm_val:
                seen_labels.add(label)
                attributes.append(ExtractedAttribute(
                    attribute_label=label,
                    normalized_label=label,
                    raw_value=str(raw_val).strip(),
                    normalized_value=str(norm_val).strip(),
                    uom=standardize_uom(uom) if uom else None,
                    is_filterable=True,
                    confidence=0.96,
                    provenance=ProvenanceRecord(
                        sourcing_tier=tier,
                        confidence_score=0.96,
                        snippet=f"{label}: {norm_val}".strip()
                    )
                ))

        text = f"{part_desc} {mfg_part_num}".strip()

        # 1. Grit / Abrasive Grade (e.g. P150, P120, P80, 220 Grit, 320 Grit)
        grit_match = re.search(r'\b(P\d{2,4}|\d{2,4}\s*Grit)\b', text, re.IGNORECASE)
        if grit_match:
            val = grit_match.group(1).upper()
            add_attr("Grit", val, val)

        # 2. Package Quantity (e.g. 6pc, 50 Disc/Box, 10pc, 4pk, 2pk, 4M, BDL, 2sq)
        pack_match = re.search(r'\b(\d+)\s*(pc|pk|pack|Disc/Box|Sheets/Box|CT|box|BDL|sq|Pair|Roll)\b', text, re.IGNORECASE)
        if pack_match:
            qty = pack_match.group(1)
            uom_str = pack_match.group(2)
            add_attr("Package Quantity", qty, qty, uom_str)

        # 3. Voltage Rating (e.g. 120V, 20V, 18V, 60V, 125V, 230V, 115V, 12V)
        volt_match = re.search(r'\b(\d{1,3})\s*(V|Volt|Volts|VAC|VDC)\b', text, re.IGNORECASE)
        if volt_match:
            v_val = volt_match.group(1)
            add_attr("Voltage", v_val, v_val, "V")

        # 4. Amperage Rating (e.g. 15A, 200A, 225A, 100A, 4 Amp)
        amp_match = re.search(r'\b(\d{1,3})\s*(A|Amp|Amps|Amperes)\b', text, re.IGNORECASE)
        if amp_match and not volt_match:
            a_val = amp_match.group(1)
            add_attr("Amperage", a_val, a_val, "A")

        # 5. Battery Capacity (e.g. 8Ah, 12AH, 5Ah, 4Ah, 2Ah)
        ah_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(Ah|AH)\b', text)
        if ah_match:
            ah_val = ah_match.group(1)
            add_attr("Battery Capacity", ah_val, ah_val, "Ah")

        # 6. Wattage (e.g. 60W, 100W, 150W, 300W, 9W, 15W)
        watt_match = re.search(r'\b(\d{1,4})\s*(W|Watt|Watts)\b', text, re.IGNORECASE)
        if watt_match and "WHT" not in text.upper():
            w_val = watt_match.group(1)
            add_attr("Wattage", w_val, w_val, "W")

        # 7. Horsepower (e.g. 1.75HP, 2HP, 3HP, 5HP)
        hp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*HP\b', text, re.IGNORECASE)
        if hp_match:
            hp_val = hp_match.group(1)
            add_attr("Horsepower", hp_val, hp_val, "HP")

        # 8. Sound Level (e.g. 47 dBA, 44 dBA, 50 dB)
        sound_match = re.search(r'\b(\d{2})\s*(dBA|dba|db|DB)\b', text, re.IGNORECASE)
        if sound_match:
            s_val = sound_match.group(1)
            add_attr("Sound Level", s_val, s_val, "dBA")

        # 9. Multi-Dimensions (e.g. 1/2"x18", 5"x.045"x7/8", 6'x36", 1x6-16', 2.75x30, 24x48, 4x4-108, 31.5x14.75)
        dim_3d = re.search(r'(\d+(?:[/-]\d+)?(?:(?:\.\d+)?))\s*["\']?\s*x\s*(\.?\d+(?:[/-]\d+)?)\s*["\']?\s*x\s*(\d+(?:[/-]\d+)?)["\']?', text)
        if dim_3d:
            d1, d2, d3 = dim_3d.group(1), dim_3d.group(2), dim_3d.group(3)
            add_attr("Dimensions", f"{d1} x {d2} x {d3}", f"{d1} in x {d2} in x {d3} in", None)
        else:
            dim_2d = re.search(r'(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*["\']?\s*x\s*(\.?\d+(?:[/-]\d+)?(?:\.\d+)?)\s*["\']?', text)
            if dim_2d:
                d1, d2 = dim_2d.group(1), dim_2d.group(2)
                add_attr("Dimensions", f"{d1} x {d2}", f"{d1} in x {d2} in", None)

        # Single Diameter / Length / Width
        inch_single = re.search(r'\b(\d+(?:-\d+/\d+|\.\d+)?)\s*(?:""|"|inch|inches)\b', text, re.IGNORECASE)
        if inch_single and "Dimensions" not in seen_labels:
            raw_len = inch_single.group(1)
            try:
                frac_len = convert_dimension(float(raw_len), "in")
            except Exception:
                frac_len = f"{raw_len} in"
            add_attr("Diameter / Length", raw_len, frac_len, None)

        foot_single = re.search(r"\b(\d+)\s*(?:'|ft|feet)\b", text, re.IGNORECASE)
        if foot_single and "Dimensions" not in seen_labels and "Diameter / Length" not in seen_labels:
            f_len = foot_single.group(1)
            add_attr("Length", f_len, f_len, "ft")

        # 10. Kerf / Thickness
        kerf_match = re.search(r'\b(\.?\d{3,4}|\d+/\d+)\s*(?:\"|in)?\s*(?:kerf|thick|thickness)\b', text, re.IGNORECASE)
        if kerf_match:
            add_attr("Thickness / Kerf", kerf_match.group(1), f"{kerf_match.group(1)} in", "in")

        # 11. Color / Finish (e.g. SS, Stainless Steel, Black, White, Charcoal, Coastline, Island Mist, Jasper, Rainier)
        if re.search(r'\b(SS|Stainless Steel|SST)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "SS", "Stainless Steel")
        elif re.search(r'\b(Bk|Black|BLK)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Black", "Black")
        elif re.search(r'\b(Wh|White|WHT)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "White", "White")
        elif re.search(r'\b(Charcoal|CH)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Charcoal", "Charcoal")
        elif re.search(r'\b(Bronze|DBZ|DBA)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Dark Bronze", "Dark Bronze")
        elif re.search(r'\b(Gray|Grey|Slate)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Gray", "Gray")
        elif re.search(r'\b(Coastline)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Coastline", "Coastline")
        elif re.search(r'\b(Island Mist)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Island Mist", "Island Mist")
        elif re.search(r'\b(Jasper)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Jasper", "Jasper")
        elif re.search(r'\b(Rainier)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Rainier", "Rainier")
        elif re.search(r'\b(Biscayne)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Biscayne", "Biscayne")
        elif re.search(r'\b(Carmel)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Carmel", "Carmel")
        elif re.search(r'\b(Honey Grove)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Honey Grove", "Honey Grove")
        elif re.search(r'\b(Tide Pool)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Tide Pool", "Tide Pool")
        elif re.search(r'\b(Cinnamon Cove)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Cinnamon Cove", "Cinnamon Cove")
        elif re.search(r'\b(Golden Hour)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Golden Hour", "Golden Hour")
        elif re.search(r'\b(Malted Barley)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Malted Barley", "Malted Barley")
        elif re.search(r'\b(Millstone)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Millstone", "Millstone")
        elif re.search(r'\b(Whiskey Barrel)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Whiskey Barrel", "Whiskey Barrel")

        # 12. Material Type (e.g. Brass, Stainless Steel, PVC, Aluminum, Ceramic, Cast Stone, Composite)
        if re.search(r'\b(Brass|BRS)\b', text, re.IGNORECASE):
            add_attr("Material", "Brass", "Brass")
        elif re.search(r'\b(PVC|Vinyl)\b', text, re.IGNORECASE):
            add_attr("Material", "PVC", "PVC")
        elif re.search(r'\b(Alum|Aluminum)\b', text, re.IGNORECASE):
            add_attr("Material", "Aluminum", "Aluminum")
        elif re.search(r'\b(Composite)\b', text, re.IGNORECASE):
            add_attr("Material", "Composite", "Composite")
        elif re.search(r'\b(Steel|SST|Carbon Steel)\b', text, re.IGNORECASE):
            add_attr("Material", "Steel", "Steel")
        elif re.search(r'\b(Fiberglass)\b', text, re.IGNORECASE):
            add_attr("Material", "Fiberglass", "Fiberglass")

        # 13. Application / Substrate
        if re.search(r'\b(Metal Cut|Metal)\b', text, re.IGNORECASE):
            add_attr("Primary Application", "Metal", "Metal Cutting & Grinding")
        elif re.search(r'\b(Masonry)\b', text, re.IGNORECASE):
            add_attr("Primary Application", "Masonry", "Masonry & Concrete")
        elif re.search(r'\b(Wood)\b', text, re.IGNORECASE):
            add_attr("Primary Application", "Wood", "Woodworking")

        # 14. Product Line / Series
        if re.search(r'\b(Transcend)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Transcend", "Transcend")
        elif re.search(r'\b(Lineage)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Lineage", "Lineage")
        elif re.search(r'\b(Enhance)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Enhance", "Enhance")
        elif re.search(r'\b(Select)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Select", "Select")
        elif re.search(r'\b(Vintage)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Vintage", "Vintage Collection")
        elif re.search(r'\b(Harvest)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Harvest", "Harvest Collection")
        elif re.search(r'\b(Landmark)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Landmark", "Landmark Collection")
        elif re.search(r'\b(Cubitron II)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Cubitron II", "Cubitron II")
        elif re.search(r'\b(Steel Demon)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Steel Demon", "Steel Demon")
        elif re.search(r'\b(Speed Demon)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Speed Demon", "Speed Demon")
        elif re.search(r'\b(Sawzall)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Sawzall", "Sawzall")
        elif re.search(r'\b(Hole Dozer)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Hole Dozer", "Hole Dozer")
        elif re.search(r'\b(Packout)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Packout", "Packout")
        elif re.search(r'\b(Flexvolt)\b', text, re.IGNORECASE):
            add_attr("Product Line / Series", "Flexvolt", "FlexVolt")

        # 15. Compliance
        if re.search(r'\b(ADA)\b', text, re.IGNORECASE):
            add_attr("ADA Compliant", "Yes", "Yes")
        if re.search(r'\b(Energy Star)\b', text, re.IGNORECASE):
            add_attr("Energy Star Certified", "Yes", "Yes")

        return attributes

    def extract_attributes(self, record: EnrichedProductRecord, lov_constraints: dict = None) -> List[ExtractedAttribute]:
        """Extracts attributes from record data."""
        part_desc = record.raw_input.part_desc or ""
        mpn = record.raw_input.mfg_part_num or ""
        return self.extract_from_description(part_desc, mpn)
