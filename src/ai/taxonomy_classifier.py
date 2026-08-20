"""
PartForge Taxonomy Classification Engine.

Hierarchical 4-Level Classification: Department > Class > Fine Class > Leaf Node
coupled with standard 8-Digit UNSPSC Code mapping.
"""

import sys
import os
import re
from typing import Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models import EnrichedProductRecord, ProvenanceRecord, SourcingTier, TaxonomyNode

# Comprehensive 30+ Category Master Taxonomy & UNSPSC Rules
TAXONOMY_RULES = [
    # Tape & Adhesives
    (r'\b(vinyl elect tape|elect tape|electrical tape|deck joist tape|emseal tape|tape|protecto wrap|weather lk|flashing tape)\b',
     'Electrical & Hardware', 'Adhesives & Tapes', 'Electrical & Construction Tapes', 'Electrical & Sealing Tapes', '31201502'),
    # Automotive & Tire Gauges
    (r'\b(tire pressure|inflator gauge|jumpstart|pwr supply|grease gun)\b',
     'Tools & Hardware', 'Automotive Tools', 'Tire & Maintenance Equipment', 'Tire Gauges & Lubrication', '25172605'),
    # Abrasives & Sanding
    (r'\b(sanding belt|sanding sponge|hiolit|abranet|cubitron|stikit|sandpaper|abrasive|sander|iridium|deos)\b',
     'Tools & Abrasives', 'Abrasives', 'Sanding Belts & Sheets', 'Sanding Belts', '31191501'),
    (r'\b(cut-off disc|cut off disc|grinding wheel|metal cut off|masonry cut off|grind disc|diamond blade|tile blade|saw blade|dado|hole dozer|sawzall blade)\b',
     'Tools & Abrasives', 'Abrasives', 'Cutting & Grinding Wheels', 'Cut-Off Wheels & Blades', '31191600'),
    # Appliances
    (r'\b(dishwasher)\b',
     'Appliances', 'Kitchen Appliances', 'Dishwashers', 'Built-In Dishwashers', '48101601'),
    (r'\b(dryer|elect dryer|gas dryer)\b',
     'Appliances', 'Laundry Appliances', 'Clothes Dryers', 'Residential Dryers', '52141602'),
    (r'\b(washer|laundry center)\b',
     'Appliances', 'Laundry Appliances', 'Washing Machines', 'Residential Washers', '52141601'),
    (r'\b(fridge|refrigerator|freezer|beverage center)\b',
     'Appliances', 'Refrigeration', 'Refrigerators & Freezers', 'Residential Refrigerators', '52141501'),
    (r'\b(range|cooktop|wall oven|microwave|toaster|espresso|coffee maker|heater kit)\b',
     'Appliances', 'Kitchen Appliances', 'Cooking Equipment', 'Ranges & Ovens', '52141543'),
    # Decking & Railing
    (r'\b(decking|fascia|trex|azek|timbertech|transcend|lineage|enhance|select 2\.0|vintage|landmark|harvest)\b',
     'Building Materials', 'Decking & Railing', 'Composite & PVC Decking', 'Deck Boards & Fascia', '30151508'),
    (r'\b(rail kit|balusters|post sleeve|post trim|post cap|post wrap|gate|support post|t-rail|finyline|select classic|westbury)\b',
     'Building Materials', 'Decking & Railing', 'Railing Systems', 'Railing Kits & Posts', '30151510'),
    (r'\b(skylt|skylight|access door|patio dr|slider|window|gliding patio|hopper|ecolite)\b',
     'Building Materials', 'Doors & Windows', 'Windows & Skylights', 'Residential Windows & Doors', '30171500'),
    (r'\b(threshold|door sweep|weatherstrip)\b',
     'Building Materials', 'Doors & Windows', 'Door Hardware', 'Thresholds & Weatherstripping', '30171505'),
    (r'\b(drywall|sheathing|osb|sub floor|rainscreen|soffit|siding|hardieplank|hardiepanel|smartside|smart lap|smart pan|lumber|doug fir|pine|fine fissured)\b',
     'Building Materials', 'Siding & Sheathing', 'Wall & Floor Panels', 'Exterior Siding & Sheathing', '30151600'),
    (r'\b(mortar|cement|concrete)\b',
     'Building Materials', 'Masonry', 'Mortar & Cements', 'Type N Mortar', '30111500'),
    (r'\b(premier rib|eaveguard|mat 2sq|ice guard|duration trudef|shingle)\b',
     'Building Materials', 'Roofing & Weatherization', 'Roof Panels & Underlayment', 'Roofing & Flashing', '30151500'),
    # Electrical & Wiring Devices
    (r'\b(load cntr|load center|panelboard|breaker box|homeline|hom2040|hom3060)\b',
     'Electrical', 'Power Distribution', 'Load Centers', 'Residential Load Centers', '39121101'),
    (r'\b(dimmer|switch|timer|outlet|receptacle|gfci|gfi|wallplate|box cover|plug in dimmer|cord conn|cord grip|welder outet|decor plate)\b',
     'Electrical', 'Wiring Devices', 'Switches & Outlets', 'Wiring Devices & Controls', '39122200'),
    (r'\b(cable|wire|triplex|cord|entrance cable|stranded wire|cat5e|romex)\b',
     'Electrical', 'Wire & Cable', 'Building Wire', 'Electrical Wire & Cable', '26121600'),
    (r'\b(oct box|square box|junction box|hanger|adjust hanger|box w/bracket|box w/hanger)\b',
     'Electrical', 'Enclosures & Boxes', 'Metallic Junction Boxes', 'Electrical Boxes', '39121300'),
    # Lighting & Lamps
    (r'\b(chandelier|pendant|wall lt|wall light|ceiling lt|ceiling light|downlight|down light|highbay|strip light|motion lt|flood lt|bath light|wrap light|flat panel|shop light|wall sconce|post lt|headlight|flashlight|clip light|work light)\b',
     'Lighting & Fans', 'Luminaires', 'Commercial & Residential Lighting', 'Light Fixtures', '39111500'),
    (r'\b(bulb|led bulb|halogen|incan|lamp|edison|par38|par20|par16|br30|br40|a19|a15|a21|a23|st19|mr16|ubulb|sodium med)\b',
     'Lighting & Fans', 'Lamps & Bulbs', 'LED & Incandescent Lamps', 'Light Bulbs & Lamps', '39101600'),
    (r'\b(ceiling fan|fan)\b',
     'Lighting & Fans', 'Fans & Ventilation', 'Ceiling Fans', 'Residential Ceiling Fans', '40101600'),
    # Power Tools, Bits & Measuring
    (r'\b(drill|impact driver|impact wrench|drill press|hammer drill|driver drill|ratchet|die grinder|rotary tool|router|jointer|planer|vacuum|blower|speaker)\b',
     'Tools & Hardware', 'Power Tools', 'Cordless & Corded Power Tools', 'Power Tools', '27112700'),
    (r'\b(nailer|stapler|finish nail|staple|brad nailer|framing nailer)\b',
     'Tools & Hardware', 'Fastening Tools', 'Nailers & Staplers', 'Pneumatic & Cordless Fastening', '27112713'),
    (r'\b(battery|charger|starter kit|power source|flexvolt|battery mount)\b',
     'Tools & Hardware', 'Tool Accessories', 'Batteries & Chargers', 'Power Tool Batteries & Chargers', '26111700'),
    (r'\b(drive bit|torx|phillips|square drive|socket adapter|screw setter|bit set|socket set|wrench|router bit|plug cutter|countersink|file bstd|folding knife|snip|bit holder|mechanics set)\b',
     'Tools & Hardware', 'Hand Tools & Accessories', 'Screwdriving & Fastening', 'Bits, Sockets & Hand Tools', '27111700'),
    (r'\b(laser|laser level|rafter square|caliper|mason line|chalk & reel|voltage detector|bigcal|t-square|fence|miter sled)\b',
     'Tools & Hardware', 'Measuring & Layout', 'Layout & Marking Tools', 'Levels & Measuring Tools', '27111800'),
    (r'\b(safety glasses|gloves|heated hoodie|heated glove|ear protection|hearing protector|dust extractor|respirator|fire extinguisher|smoke & co alarm|kneeling pad|mechanical pencil|holster|tool chest|organizer|packout)\b',
     'Safety & Storage', 'Safety & PPE', 'Protective Equipment & Storage', 'Safety Gear & Jobsite Storage', '46181500'),
]


class TaxonomyClassifier:
    """Classifies catalog items into 4-level taxonomy hierarchy + 8-digit UNSPSC."""

    def __init__(self):
        self.rules = TAXONOMY_RULES

    def classify(self, record: EnrichedProductRecord) -> TaxonomyNode:
        """Determines taxonomy node and UNSPSC code for record."""
        part_desc = record.raw_input.part_desc or ""
        mpn = record.raw_input.mfg_part_num or ""
        brand = record.brand_profile.brand_name or ""
        manuf = record.brand_profile.manufacturer_name or ""

        text = f"{part_desc} {mpn} {brand} {manuf}".lower()

        for pattern, dept, cls_name, fine, leaf, unspsc in self.rules:
            if re.search(pattern, text, re.IGNORECASE):
                classpath = f"{dept} > {cls_name} > {fine} > {leaf}"
                return TaxonomyNode(
                    department=dept,
                    class_name=cls_name,
                    fine_class=fine,
                    leaf_node=leaf,
                    classpath=classpath,
                    unspsc_code=unspsc,
                    confidence=0.96,
                    provenance=ProvenanceRecord(
                        sourcing_tier=SourcingTier.MODEL_INFERENCE,
                        confidence_score=0.96,
                        snippet=f"Taxonomy Classification: {classpath}"
                    )
                )

        # Fallback General MRO
        dept = "Industrial MRO"
        cls_name = "Hardware & Supplies"
        fine = "General Maintenance"
        leaf = "Industrial Supplies"
        classpath = f"{dept} > {cls_name} > {fine} > {leaf}"
        return TaxonomyNode(
            department=dept,
            class_name=cls_name,
            fine_class=fine,
            leaf_node=leaf,
            classpath=classpath,
            unspsc_code="31160000",
            confidence=0.75,
            provenance=ProvenanceRecord(
                sourcing_tier=SourcingTier.FALLBACK_NULL,
                confidence_score=0.75
            )
        )
