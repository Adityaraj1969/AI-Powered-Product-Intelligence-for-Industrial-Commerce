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
                    raw_value=str(raw_val),
                    normalized_value=str(norm_val),
                    uom=standardize_uom(uom) if uom else None,
                    is_filterable=True,
                    confidence=0.95,
                    provenance=ProvenanceRecord(
                        sourcing_tier=tier,
                        confidence_score=0.95,
                        snippet=f"{label}: {norm_val} {uom or ''}".strip()
                    )
                ))

        text = f"{part_desc} {mfg_part_num}".strip()

        # 1. Grit / Abrasive Grade (e.g. P150, P120, P80, 220 Grit)
        grit_match = re.search(r'\b(P\d{2,4}|\d{2,4}\s*Grit)\b', text, re.IGNORECASE)
        if grit_match:
            val = grit_match.group(1).upper()
            add_attr("Grit", val, val)

        # 2. Pack / Package Quantity (e.g. 6pc, 50 Disc/Box, 10pc, 4pk, 2pk, 4M)
        pack_match = re.search(r'\b(\d+)\s*(pc|pk|pack|Disc/Box|Sheets/Box|CT|box)\b', text, re.IGNORECASE)
        if pack_match:
            qty = pack_match.group(1)
            uom_str = pack_match.group(2)
            add_attr("Package Quantity", qty, qty, uom_str)

        # 3. Voltage Rating (e.g. 120V, 20V, 18V, 60V, 125V, 230V, 115V, 40V)
        volt_match = re.search(r'\b(\d{1,3})\s*(V|Volt|Volts|VAC|VDC)\b', text, re.IGNORECASE)
        if volt_match:
            v_val = volt_match.group(1)
            add_attr("Voltage", v_val, f"{v_val} V", "V")

        # 4. Amperage Rating (e.g. 15A, 200A, 225A, 100A, 4 Amp)
        amp_match = re.search(r'\b(\d{1,3})\s*(A|Amp|Amps|Amperes)\b', text, re.IGNORECASE)
        if amp_match and not volt_match:  # avoid false positives
            a_val = amp_match.group(1)
            add_attr("Amperage", a_val, f"{a_val} A", "A")

        # 5. Horsepower (e.g. 1.75HP, 2HP, 3HP, 5HP)
        hp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*HP\b', text, re.IGNORECASE)
        if hp_match:
            hp_val = hp_match.group(1)
            add_attr("Horsepower", hp_val, f"{hp_val} HP", "HP")

        # 6. Flow Rate (e.g. 1.5 gpm, 1.8GPM, 2.2 gpm)
        flow_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(GPM|gpm|gal/min)\b', text, re.IGNORECASE)
        if flow_match:
            f_val = flow_match.group(1)
            add_attr("Flow Rate", f_val, f"{f_val} gpm", "gpm")

        # 7. Pressure Rating (e.g. 150#, 150 psi, 300 psi)
        psi_match = re.search(r'\b(\d+)\s*(#|psi|PSI|lb|lbs)\b', text, re.IGNORECASE)
        if psi_match:
            p_val = psi_match.group(1)
            add_attr("Pressure Rating", p_val, f"{p_val} psi", "psi")

        # 8. Sound Level (e.g. 47 dBA, 44 dBA, 50 dB)
        sound_match = re.search(r'\b(\d{2})\s*(dBA|dba|db|DB)\b', text, re.IGNORECASE)
        if sound_match:
            s_val = sound_match.group(1)
            add_attr("Sound Level", s_val, f"{s_val} dBA", "dBA")

        # 9. Multi-Dimensions (e.g. 1/2"x18", 5"x.045"x7/8", 6'x36", 1x6-16', 2.75x30, 24x48, 4x4-108)
        dim_3d = re.search(r'(\d+(?:[/-]\d+)?(?:(?:\.\d+)?))\s*["\']?\s*x\s*(\.?\d+(?:[/-]\d+)?)\s*["\']?\s*x\s*(\d+(?:[/-]\d+)?)["\']?', text)
        if dim_3d:
            d1, d2, d3 = dim_3d.group(1), dim_3d.group(2), dim_3d.group(3)
            add_attr("Dimensions", f"{d1} x {d2} x {d3}", f"{d1} in x {d2} in x {d3} in", "in")
        else:
            dim_2d = re.search(r'(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*["\']?\s*x\s*(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*["\']?', text)
            if dim_2d:
                d1, d2 = dim_2d.group(1), dim_2d.group(2)
                add_attr("Dimensions", f"{d1} x {d2}", f"{d1} in x {d2} in", "in")

        # Single Diameter / Length (e.g. 12" Blade, 7" Disc, 16' Decking, 500')
        inch_single = re.search(r'\b(\d+(?:-\d+/\d+|\.\d+)?)\s*(?:""|"|inch|inches)\b', text, re.IGNORECASE)
        if inch_single and "Dimensions" not in seen_labels:
            raw_len = inch_single.group(1)
            try:
                frac_len = convert_dimension(float(raw_len), "in")
            except Exception:
                frac_len = f"{raw_len} in"
            add_attr("Diameter / Length", raw_len, frac_len, "in")

        foot_single = re.search(r"\b(\d+)\s*(?:'|ft|feet)\b", text, re.IGNORECASE)
        if foot_single and "Length (Feet)" not in seen_labels:
            f_len = foot_single.group(1)
            add_attr("Length (Feet)", f_len, f"{f_len} ft", "ft")

        # 10. Color / Finish (e.g. SS, Stainless Steel, Black, White, Chrome, Brushed Nickel, Charcoal, Coastline)
        if re.search(r'\b(SS|Stainless Steel|SST)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "SS", "Stainless Steel")
        elif re.search(r'\b(Bk|Black|BLK)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Black", "Black")
        elif re.search(r'\b(Wh|White|WHT)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "White", "White")
        elif re.search(r'\b(Chrome|CHR)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Chrome", "Chrome")
        elif re.search(r'\b(Brushed Nickel|BN|NI)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Brushed Nickel", "Brushed Nickel")
        elif re.search(r'\b(Charcoal)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Charcoal", "Charcoal")
        elif re.search(r'\b(Coastline)\b', text, re.IGNORECASE):
            add_attr("Finish / Color", "Coastline", "Coastline")

        # 11. Material Type (e.g. Brass, Stainless Steel, PVC, Aluminum, Ceramic, Cast Stone, Composite)
        if re.search(r'\b(Brass|BRS)\b', text, re.IGNORECASE):
            add_attr("Material", "Brass", "Brass")
        elif re.search(r'\b(PVC|Vinyl)\b', text, re.IGNORECASE):
            add_attr("Material", "PVC", "PVC")
        elif re.search(r'\b(Alum|Aluminum)\b', text, re.IGNORECASE):
            add_attr("Material", "Aluminum", "Aluminum")
        elif re.search(r'\b(Composite)\b', text, re.IGNORECASE):
            add_attr("Material", "Composite", "Composite")

        # 12. Features & Compliance
        if re.search(r'\b(ADA)\b', text, re.IGNORECASE):
            add_attr("ADA Compliant", "Yes", "Yes")
        if re.search(r'\b(Energy Star)\b', text, re.IGNORECASE):
            add_attr("Energy Star Certified", "Yes", "Yes")
        if re.search(r'\b(GFCI|GFI)\b', text, re.IGNORECASE):
            add_attr("Circuit Protection", "GFCI", "Ground Fault Circuit Interrupter (GFCI)")

        return attributes

    def extract_attributes(self, record: EnrichedProductRecord, lov_constraints: dict = None) -> List[ExtractedAttribute]:
        """Extracts attributes from record data."""
        part_desc = record.raw_input.part_desc or ""
        mpn = record.raw_input.mfg_part_num or ""
        return self.extract_from_description(part_desc, mpn)


if __name__ == "__main__":
    extractor = AttributeExtractor()
    test_cases = [
        ("PDSH4816AF Dishwasher SS - Display Only 120V 15A 47 dBA", "PDSH4816AF"),
        ("DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc P150", "DCB518ASTS06G"),
        ("49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc 10pc", "49-94-0013"),
        ("3/8 CPLG BRS 150# Parker Coupling", "3/8 CPLG BRS 150#"),
        ("543140016 1nx6-16' Biscayne Sq Edge - Trex Transcend Lineage Decking", "543140016"),
    ]
    for desc, mpn in test_cases:
        print(f"\nProduct: {desc}")
        attrs = extractor.extract_from_description(desc, mpn)
        for a in attrs:
            print(f"  • {a.attribute_label}: {a.normalized_value} (UOM: {a.uom or '—'})")
