"""
PartForge Industrial Taxonomy & UNSPSC Classifier.

Classifies industrial catalog products into 4-level taxonomy hierarchy:
  Department > Class > Fine Class > Leaf Node + 8-Digit UNSPSC Code.
Combines high-speed rule-based keyword patterns with semantic categorization.
"""

import re
from typing import Tuple, Dict, Any
from src.models import TaxonomyNode, ProvenanceRecord, SourcingTier


# Comprehensive Taxonomy & UNSPSC Knowledge Base
TAXONOMY_RULES = [
    # Abrasives & Sanding
    (r"\b(sanding belt|sanding sponge|hiolit|abranet|cubitron|stikit|sandpaper|abrasive|sander)\b",
     "Tools & Abrasives", "Abrasives", "Sanding Belts & Sheets", "Sanding Belts", "31191501"),
    (r"\b(cut-off disc|cut off disc|grinding wheel|metal cut off|masonry cut off|grind disc)\b",
     "Tools & Abrasives", "Abrasives", "Cutting & Grinding Wheels", "Cut-Off Wheels", "31191600"),
     
    # Appliances - Kitchen & Laundry
    (r"\b(dishwasher)\b",
     "Appliances", "Kitchen Appliances", "Dishwashers", "Built-In Dishwashers", "48101601"),
    (r"\b(dryer|elect dryer|gas dryer)\b",
     "Appliances", "Laundry Appliances", "Clothes Dryers", "Residential Dryers", "52141602"),
    (r"\b(washer|laundry center)\b",
     "Appliances", "Laundry Appliances", "Washing Machines", "Residential Washers", "52141601"),
    (r"\b(fridge|refrigerator|freezer)\b",
     "Appliances", "Refrigeration", "Refrigerators & Freezers", "Residential Refrigerators", "52141501"),
    (r"\b(range|cooktop|wall oven|microwave|toaster|espresso|coffee maker)\b",
     "Appliances", "Kitchen Appliances", "Cooking Equipment", "Ranges & Ovens", "52141543"),
     
    # Building Materials, Decking & Railing
    (r"\b(decking|fascia|trex|azek|timbertech|transcend|lineage)\b",
     "Building Materials", "Decking & Railing", "Composite & PVC Decking", "Deck Boards", "30151508"),
    (r"\b(rail kit|balusters|post sleeve|post trim|post cap|post wrap|gate)\b",
     "Building Materials", "Decking & Railing", "Railing Systems", "Railing Kits & Components", "30151510"),
    (r"\b(skylt|skylight|access door|patio dr|slider|window)\b",
     "Building Materials", "Doors & Windows", "Windows & Skylights", "Residential Windows", "30171500"),
    (r"\b(drywall|sheathing|osb|sub floor|rainscreen|soffit|siding|hardieplank|hardiepanel|smartside)\b",
     "Building Materials", "Siding & Sheathing", "Wall & Floor Panels", "Exterior Siding & Sheathing", "30151600"),
    (r"\b(mortar|cement|concrete)\b",
     "Building Materials", "Masonry", "Mortar & Cements", "Type N Mortar", "30111500"),
     
    # Electrical & Lighting
    (r"\b(load cntr|load center|panelboard|breaker box)\b",
     "Electrical", "Power Distribution", "Load Centers", "Residential Load Centers", "39121101"),
    (r"\b(dimmer|switch|timer|outlet|receptacle|gfci|gfi|wallplate|box cover|plug in dimmer)\b",
     "Electrical", "Wiring Devices", "Switches & Outlets", "Wiring Devices & Controls", "39122200"),
    (r"\b(cable|wire|triplex|cord|entrance cable)\b",
     "Electrical", "Wire & Cable", "Building Wire", "Electrical Wire & Cable", "26121600"),
    (r"\b(chandelier|pendant|wall lt|wall light|ceiling lt|ceiling light|downlight|down light|highbay|strip light|motion lt|flood lt)\b",
     "Lighting & Fans", "Luminaires", "Commercial & Residential Lighting", "Light Fixtures", "39111500"),
    (r"\b(bulb|led bulb|halogen|incan|lamp|edison)\b",
     "Lighting & Fans", "Lamps & Bulbs", "LED & Incandescent Lamps", "Light Bulbs", "39101600"),
    (r"\b(ceiling fan|fan)\b",
     "Lighting & Fans", "Fans & Ventilation", "Ceiling Fans", "Residential Ceiling Fans", "40101600"),
     
    # Power Tools & Accessories
    (r"\b(drill|impact driver|impact wrench|drill press|hammer drill|driver drill)\b",
     "Tools & Hardware", "Power Tools", "Drills & Drivers", "Cordless Drills & Drivers", "27112700"),
    (r"\b(saw|saw blade|circ saw|miter saw|recip saw|jig saw|bandsaw|track saw|table saw)\b",
     "Tools & Hardware", "Power Tools", "Saws & Saw Blades", "Power Saws & Blades", "27112800"),
    (r"\b(nailer|stapler|finish nail|staple)\b",
     "Tools & Hardware", "Fastening Tools", "Nailers & Staplers", "Pneumatic & Cordless Nailers", "27112713"),
    (r"\b(grinder|die grinder|rotary tool|router|jointer|planer)\b",
     "Tools & Hardware", "Power Tools", "Machining & Cutting Tools", "Power Grinders & Planers", "27112704"),
    (r"\b(battery|charger|starter kit|power source|flexvolt)\b",
     "Tools & Hardware", "Tool Accessories", "Batteries & Chargers", "Power Tool Batteries", "26111700"),
    (r"\b(drive bit|torx|phillips|square drive|socket adapter|screw setter|bit set|socket set|wrench)\b",
     "Tools & Hardware", "Hand Tools", "Screwdriving & Fastening", "Bits & Sockets", "27111700"),
    (r"\b(laser|laser level|rafter square|caliper|mason line|chalk & reel|voltage detector)\b",
     "Tools & Hardware", "Measuring & Layout", "Layout & Marking Tools", "Levels & Measuring Tools", "27111800"),
    (r"\b(safety glasses|gloves|heated hoodie|heated glove|ear protection|hearing protector|dust extractor|respirator)\b",
     "Safety & Facility", "Personal Protective Equipment", "Safety Gear & Workwear", "Safety Wear", "46181500"),
     
    # Plumbing & Hardware
    (r"\b(faucet|sink faucet|commercial faucet)\b",
     "Plumbing", "Faucets & Fixtures", "Kitchen & Bath Faucets", "Sink Faucets", "30181702"),
    (r"\b(coupling|cplg|elbow|tee|union|adapter|bushing|fitting|nipple)\b",
     "Plumbing", "Pipes, Tubes & Fittings", "Pipe & Hose Fittings", "Pipe Couplings & Fittings", "40171500"),
]


class TaxonomyClassifier:
    """Classifies products into standard taxonomy and 8-digit UNSPSC code."""

    def __init__(self):
        self.rules = TAXONOMY_RULES

    def classify(self, part_desc: str, mfg_part_num: str = "", brand: str = "") -> TaxonomyNode:
        text = f"{part_desc} {mfg_part_num} {brand}".lower()

        for pattern, dept, cls, fine, leaf, unspsc in self.rules:
            if re.search(pattern, text, re.IGNORECASE):
                classpath = f"{dept} > {cls} > {fine} > {leaf}"
                return TaxonomyNode(
                    department=dept,
                    class_name=cls,
                    fine_class=fine,
                    leaf_node=leaf,
                    classpath=classpath,
                    unspsc_code=unspsc,
                    confidence=0.95,
                    provenance=ProvenanceRecord(
                        sourcing_tier=SourcingTier.CONTENT_GUIDELINES,
                        confidence_score=0.95,
                    )
                )

        # Fallback general classification
        return TaxonomyNode(
            department="Industrial MRO",
            class_name="Hardware & Supplies",
            fine_class="General Maintenance",
            leaf_node="Industrial Supplies",
            classpath="Industrial MRO > Hardware & Supplies > General Maintenance > Industrial Supplies",
            unspsc_code="31160000",
            confidence=0.70,
            provenance=ProvenanceRecord(
                sourcing_tier=SourcingTier.MODEL_INFERENCE,
                confidence_score=0.70,
            )
        )


if __name__ == "__main__":
    classifier = TaxonomyClassifier()
    test_cases = [
        "PDSH4816AF Dishwasher SS - Display Only",
        "DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc",
        "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
        "543140016 1nx6-16' Biscayne Sq Edge - Trex Transcend Lineage Decking",
        "AYCL-153PH-WH Lutron Dimmer Wh",
        "3/8 CPLG BRS 150# Parker Coupling",
    ]
    for tc in test_cases:
        res = classifier.classify(tc)
        print(f"\nText: {tc}")
        print(f"  Classpath: {res.classpath}")
        print(f"  UNSPSC:    {res.unspsc_code} (Conf: {res.confidence:.0%})")
