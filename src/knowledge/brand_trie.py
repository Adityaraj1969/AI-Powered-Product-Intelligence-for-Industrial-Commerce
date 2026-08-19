import re
from typing import Optional, List, Dict, Any
from rapidfuzz import fuzz, process
from src.models import CanonicalBrandProfile

def normalize_name(name: str) -> str:
    return name.strip().lower() if name else ""

class BrandIndex:
    def __init__(self):
        self.brands: Dict[str, dict] = {}
        
    def load_from_csv(self, path: str):
        pass
        
    def load_from_list(self, brands: List[dict]):
        for b in brands:
            name = normalize_name(b.get("brand_name", ""))
            if name:
                self.brands[name] = b

    def _match(self, query: str, threshold: int = 88) -> Optional[dict]:
        if not query or not self.brands:
            return None
            
        norm_query = normalize_name(query)
        choices = list(self.brands.keys())
        
        res = process.extractOne(norm_query, choices, scorer=fuzz.token_sort_ratio)
        if res:
            match_str, score, _ = res
            if score >= threshold:
                b = self.brands[match_str].copy()
                b['confidence'] = score / 100.0
                return b
        return None

_global_index = BrandIndex()

def match_brand(query: str, threshold: int = 88) -> Optional[CanonicalBrandProfile]:
    res = _global_index._match(query, threshold)
    if res:
        # filter keys to match CanonicalBrandProfile
        from src.models import ProvenanceRecord, SourcingTier
        profile = CanonicalBrandProfile(
            manufacturer_name=res.get("manufacturer_name", ""),
            manufacturer_code=res.get("manufacturer_code", ""),
            brand_name=res.get("brand_name", ""),
            brand_code=res.get("brand_code", ""),
            trade_name=res.get("trade_name", ""),
            confidence=res.get("confidence", 0.0),
            trademark_retained=res.get("trademark_retained", False),
        )
        return profile
    return None

def match_manufacturer(query: str, threshold: int = 88) -> Optional[str]:
    res = _global_index._match(query, threshold)
    if res:
        return res.get("manufacturer_name")
    return None

if __name__ == "__main__":
    sample_brands = [
        {"brand_name": "Freud Inc", "manufacturer_name": "Freud Inc"},
        {"brand_name": "Acme Corp", "manufacturer_name": "Acme Corporation"},
        {"brand_name": "3M", "manufacturer_name": "3M Company"},
    ]
    _global_index.load_from_list(sample_brands)
    
    b_match = match_brand("Freud")
    assert b_match is not None and b_match.brand_name == "Freud Inc", f"Got {b_match}"
    m_match = match_manufacturer("Acme")
    assert m_match == "Acme Corporation"
    
    no_match = match_brand("XYZ Random", threshold=88)
    assert no_match is None
    print("brand_trie.py tests passed!")
