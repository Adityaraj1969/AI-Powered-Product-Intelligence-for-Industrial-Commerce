import sys
import os
import re
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models import EnrichedProductRecord, ExtractedAttribute
from src.ai.llm_client import FreeLLMClient

class AttributeExtractor:
    def __init__(self):
        self.llm_client = FreeLLMClient()

    def extract_attributes(self, record: EnrichedProductRecord, lov_constraints: dict = None) -> List[ExtractedAttribute]:
        desc = getattr(record, 'cleaned_description', getattr(record, 'Part_Desc', ''))
        
        system_prompt = "You are a product data extraction expert. Extract attributes from the product description as a JSON array of objects with keys: name, value, unit."
        if lov_constraints:
            system_prompt += f"\nConstraint: Only use values from these lists if applicable: {lov_constraints}"
            
        user_prompt = f"Product Description: {desc}"
        
        try:
            response_json = self.llm_client.generate_json(system_prompt, user_prompt)
            attributes = []
            
            # Handling various mock/dummy responses or actual responses
            if "mock" in response_json:
                return self.extract_from_description(desc)
                
            # Assuming LLM returns a list in "attributes" key or directly
            items = response_json.get("attributes", [])
            if not items and isinstance(response_json, list):
                items = response_json
                
            for item in items:
                attributes.append(ExtractedAttribute(
                    name=item.get("name", ""),
                    value=item.get("value", ""),
                    unit=item.get("unit")
                ))
            return attributes
        except Exception as e:
            print(f"LLM extraction failed: {e}. Falling back to heuristics.")
            return self.extract_from_description(desc)

    def extract_from_description(self, part_desc: str) -> List[ExtractedAttribute]:
        attributes = []
        if not part_desc:
            return attributes
            
        # Regex heuristics for dimensions, voltage, amperage
        dim_matches = re.finditer(r'(\d+(?:\.\d+)?)\s*(inch|in|"|mm|cm)', part_desc, re.IGNORECASE)
        for m in dim_matches:
            attributes.append(ExtractedAttribute(name="Dimension", value=m.group(1), unit=m.group(2)))
            
        volt_matches = re.finditer(r'(\d+(?:\.\d+)?)\s*(V|Volt|Volts|VAC|VDC)', part_desc, re.IGNORECASE)
        for m in volt_matches:
            attributes.append(ExtractedAttribute(name="Voltage", value=m.group(1), unit=m.group(2)))
            
        amp_matches = re.finditer(r'(\d+(?:\.\d+)?)\s*(A|Amp|Amps)', part_desc, re.IGNORECASE)
        for m in amp_matches:
            attributes.append(ExtractedAttribute(name="Amperage", value=m.group(1), unit=m.group(2)))
            
        return attributes

if __name__ == "__main__":
    class MockRecord:
        pass
    
    mock = MockRecord()
    mock.cleaned_description = "Heavy Duty Motor 120V 15A with 2.5 inch shaft"
    mock.Part_Desc = mock.cleaned_description
    
    extractor = AttributeExtractor()
    attrs = extractor.extract_attributes(mock)
    for attr in attrs:
        print(f"{attr.name}: {attr.value} {attr.unit or ''}")
