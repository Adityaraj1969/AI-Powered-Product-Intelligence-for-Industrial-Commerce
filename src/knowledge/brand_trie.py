"""
PartForge Brand Matching Engine.

Resolves raw and abbreviated brand and manufacturer text into canonical entities
from the master controlled vocabulary using deterministic pattern matching and RapidFuzz.
Resolves distributor pollution (e.g. cooperatives and distributors) to true OEM brands.
"""

import re
from typing import Tuple, Optional

from src.models import CanonicalBrandProfile, ProvenanceRecord, SourcingTier
from src.config import ALL_PLACEHOLDERS

# Master Canonical Brand Entity Dictionary (Pattern, Brand, Manufacturer, Trade Name)
CANONICAL_BRAND_RULES = [
    # 1. 3M / Cubitron / Stikit
    (r'\b(3M|CUBITRON|STIKIT|3MABR)\b', '3M™', '3M Company', 'Cubitron II™'),
    
    # 2. Diablo / Freud
    (r'\b(DIABLO|FREUD|DCB|DBD|DBDS|D0|D1)\b', 'DIABLO®', 'Freud Inc', 'Steel Demon™'),
    
    # 3. Milwaukee Tool
    (r'\b(MILW|MILWAUKEE|SAWZALL|HOLE DOZER|PACKOUT|48-|49-)\b', 'MILWAUKEE®', 'Milwaukee Electric Tool Corp', 'Heavy Duty™'),
    
    # 4. DeWalt / Stanley Black & Decker
    (r'\b(DEWALT|DWHT|DCF|DCD|DCG|DCS|DCL|DCB|DWST|DWMT|DWE|DWS|DWA)\b', 'DEWALT®', 'Stanley Black & Decker', 'Guaranteed Tough®'),
    
    # 5. Makita
    (r'\b(MAKITA|XNB|XRF|XVP|XLT|XLC|XRU|XRJ|GSL|XSH|XDT|XFD)\b', 'MAKITA®', 'Makita USA Inc', 'LXT®'),
    
    # 6. Festool
    (r'\b(FESTOOL|SYSTAINER)\b', 'FESTOOL®', 'Festool USA', 'Systainer®'),
    
    # 7. Trex Decking & Railing
    (r'\b(TREX|LINEAGE|TRANSCEND|ENHANCE|SELECT 2\.0|543140|543160|543200|543210|543220)\b', 'TREX®', 'Trex Company Inc', 'Transcend® Lineage™'),
    
    # 8. TimberTech / Azek
    (r'\b(TIMBERTECH|AZEK|HARVEST|VINTAGE|LANDMARK|CONTI|EDGEM)\b', 'TIMBERTECH®', 'The AZEK Company', 'Vintage Collection®'),
    
    # 9. Mirka Abrasives
    (r'\b(MIRKA|ABRANET|HIOLIT|IRIDIUM|DEOS|5B-|9A-)\b', 'MIRKA®', 'Mirka Abrasives Inc', 'Abranet®'),
    
    # 10. Kichler Lighting
    (r'\b(KICHLER|45297|55155|55184|55185|55186)\b', 'KICHLER®', 'Kichler Lighting LLC', 'Kichler®'),
    
    # 11. Satco / Nuvo
    (r'\b(SATCO|NUVO|STARFISH|S11|S21|S29|S39|S9|S8)\b', 'SATCO®', 'Satco Products Inc', 'Nuvo®'),
    
    # 12. Philips / Wiz Lighting
    (r'\b(PHILIPS|PHILLIPS|WIZ|557|558|560|561|562|563|564|565|566|567|568|569|570|571|572|573|574|575)\b', 'PHILIPS®', 'Signify North America', 'Philips Lighting®'),
    
    # 13. Frigidaire / Electrolux
    (r'\b(FRIGIDAIRE|PDSH|PRFS|GCFG|PMOS|PCFE)\b', 'FRIGIDAIRE®', 'Electrolux / Frigidaire', 'Professional Series®'),
    
    # 14. KitchenAid / Maytag / Whirlpool
    (r'\b(KITCHENAID|KITCHEN AID|KDFM|KDTS|KDPS|KSES|KMMF)\b', 'KITCHENAID®', 'Whirlpool Corporation', 'KitchenAid®'),
    (r'\b(MAYTAG|MVWP)\b', 'MAYTAG®', 'Whirlpool Corporation', 'Commercial Technology®'),
    (r'\b(WHIRLPOOL|WDTS|WSGS|WMMS)\b', 'WHIRLPOOL®', 'Whirlpool Corporation', 'Whirlpool®'),
    
    # 15. GE / Café Appliances
    (r'\b(CAFÉ|CAFE|C7CD|C7CE|C7CES|C9TM|C90A|CES7|CHP9|CVM5|CVE2)\b', 'CAFÉ®', 'GE Appliances (Haier)', 'Café™ Series'),
    (r'\b(GE |GENERAL ELECTRIC|PDT7|PDD4|PTD7|PTW7|PEP9|PB90|PS96|GDE2|FCM1|GNE2|PAD2|PGE2|JXGR|GCST|PCWK)\b', 'GE®', 'GE Appliances (Haier)', 'Profile™'),
    
    # 16. LG Electronics
    (r'\b(LG |LDPH|WKE100|MSER|LSEL|LT18S)\b', 'LG®', 'LG Electronics', 'ThinQ®'),
    
    # 17. Speed Queen Laundry
    (r'\b(SPEED QUEEN|DF70|DR70|DV20|DC50|FF70|DR50|TV20|TC50|TR70|TR50|SQ )\b', 'SPEED QUEEN®', 'Alliance Laundry Systems', 'Speed Queen®'),
    
    # 18. XO Appliances / Beko / Sharp / Element
    (r'\b(XOU24|XO APPLIANCE)\b', 'XO APPLIANCE®', 'XO Appliance LLC', 'XO Luxury®'),
    (r'\b(BEKO|WOSP)\b', 'BEKO®', 'Beko US Inc', 'Beko®'),
    (r'\b(SHARP|SMC2|SMD2)\b', 'SHARP®', 'Sharp Electronics Corp', 'Carousel®'),
    (r'\b(ELEMENT|ERFD|EUF1|EUF2)\b', 'ELEMENT®', 'Element Electronics', 'Element Home®'),
    (r'\b(SLER30)\b', 'FORNO®', 'Cendrex / Forno Commercial', 'Forno Appliances®'),
    
    # 19. Lutron Electronics
    (r'\b(LUTRON|AYCL|DVCL|MSCL|PD-)\b', 'LUTRON®', 'Lutron Electronics Co Inc', 'Ariadni®'),
    
    # 20. Leviton
    (r'\b(LEVITON|5522|5266|5366)\b', 'LEVITON®', 'Leviton Manufacturing Co Inc', 'Decora®'),
    
    # 21. Southwire
    (r'\b(SOUTHWIRE|ROMEX)\b', 'SOUTHWIRE®', 'Southwire Company LLC', 'Romex®'),
    
    # 22. James Hardie
    (r'\b(HARDIE|JAMESHARDIE|HARDIEPLANK|HARDIEPANEL)\b', 'JAMES HARDIE®', 'James Hardie Building Products', 'HardiePlank®'),
    
    # 23. LP SmartSide
    (r'\b(SMARTSIDE|SMART LAP|SMART PAN|SMART VENTED)\b', 'LP SMARTSIDE®', 'Louisiana-Pacific Corporation', 'SmartSide®'),
    
    # 24. Hunter Fans
    (r'\b(HUNTER|ANISTEN|XIDANE|CASSIUS|JETTY|GILMOUR)\b', 'HUNTER®', 'Hunter Fan Company', 'Hunter Fans®'),
    
    # 25. Kreg Tool
    (r'\b(KREG|KPTDR|KPTDV|KPTCS|KPTJS|KPTRS|KPTBPS|BCB2A|BATT4A|CRGR401)\b', 'KREG®', 'Kreg Tool Company', 'Kreg®'),
    
    # 26. Fasteners & Tools
    (r'\b(WERA)\b', 'WERA®', 'Wera Tools', 'Kraftform Kompakt®'),
    (r'\b(PREBENA)\b', 'PREBENA®', 'Prebena Fastening Systems', 'Prebena®'),
    (r'\b(SENCO)\b', 'SENCO®', 'Kyocera Senco Industrial Tools', 'Duraspin®'),
    (r'\b(DSI|WESTBURY)\b', 'DSI WESTBURY®', 'Digger Specialties Inc', 'Westbury®'),
    (r'\b(PROVIA|ECOLITE)\b', 'PROVIA®', 'ProVia Doors & Windows', 'ecoLitePlus™'),
    (r'\b(UNITED WINDOW)\b', 'UNITED WINDOW®', 'United Window & Door Mfg', 'United Windows®'),
    (r'\b(CERTAINTEED|EASI-LITE|FIRELITE)\b', 'CERTAINTEED®', 'CertainTeed Gypsum', 'Easi-Lite®'),
    (r'\b(COOPER)\b', 'COOPER®', 'Cooper Lighting Solutions', 'Cooper®'),
    (r'\b(SQUARE D|HOM2040|HOM3060|QO612)\b', 'SQUARE D®', 'Schneider Electric', 'Homeline®'),
    (r'\b(OLIVER)\b', 'OLIVER®', 'Oliver Machinery Co', 'Oliver Machinery®'),
    (r'\b(GRIZZLY|WOODSTOCK)\b', 'GRIZZLY®', 'Woodstock International Inc', 'Grizzly Industrial®'),
    (r'\b(EDGE EYEWEAR)\b', 'EDGE EYEWEAR®', 'Edge Eyewear Inc', 'Edge Tactical®'),
    (r'\b(U S TAPE|US TAPE)\b', 'U S TAPE®', 'U S Tape Company', 'DuraWheel®'),
]


class BrandMatcher:
    """Matches raw supplier brand and manufacturer text to canonical Master Entities."""

    def __init__(self):
        pass

    def match(
        self,
        raw_desc: str,
        raw_mpn: str = "",
        raw_brand: Optional[str] = None,
        raw_manuf: Optional[str] = None,
        unilog_brand: Optional[str] = None,
        dib_brand: Optional[str] = None,
    ) -> CanonicalBrandProfile:
        """Resolves raw inputs to a canonical brand profile."""
        combined_text = f"{raw_desc} {raw_mpn} {raw_brand or ''} {raw_manuf or ''} {unilog_brand or ''} {dib_brand or ''}".upper()

        # 1. Deterministic canonical brand resolution
        for pattern, brand, manuf, trade in CANONICAL_BRAND_RULES:
            if re.search(pattern, combined_text):
                return CanonicalBrandProfile(
                    brand_name=brand,
                    manufacturer_name=manuf,
                    trade_name=trade,
                    confidence=0.98,
                    trademark_retained=True,
                    provenance=ProvenanceRecord(
                        sourcing_tier=SourcingTier.MASTER_CONTROLLED_VOCAB,
                        confidence_score=0.98,
                        snippet=f"Canonical Entity Matched: {brand} ({manuf})"
                    )
                )

        # 2. Direct supplier brand resolution if not placeholder
        for candidate in [raw_brand, unilog_brand, dib_brand]:
            if candidate and candidate.strip() not in ALL_PLACEHOLDERS:
                clean = candidate.strip()
                return CanonicalBrandProfile(
                    brand_name=clean,
                    manufacturer_name=clean,
                    confidence=0.90,
                    trademark_retained=False,
                    provenance=ProvenanceRecord(
                        sourcing_tier=SourcingTier.CONTENT_GUIDELINES,
                        confidence_score=0.90
                    )
                )

        # 3. Clean parenthesized code from manufacturer if available
        if raw_manuf and raw_manuf.strip() not in ALL_PLACEHOLDERS and raw_manuf.strip() != "-":
            clean_manuf = re.sub(r'\s*\([^)]*\)$', '', raw_manuf).strip()
            return CanonicalBrandProfile(
                brand_name=clean_manuf,
                manufacturer_name=clean_manuf,
                confidence=0.85,
                trademark_retained=False,
                provenance=ProvenanceRecord(
                    sourcing_tier=SourcingTier.MODEL_INFERENCE,
                    confidence_score=0.85
                )
            )

        # 4. Fallback Unknown
        return CanonicalBrandProfile(
            brand_name="-- Unbranded --",
            manufacturer_name="Generic Manufacturer",
            confidence=0.50,
            trademark_retained=False,
            provenance=ProvenanceRecord(
                sourcing_tier=SourcingTier.FALLBACK_NULL,
                confidence_score=0.50
            )
        )
