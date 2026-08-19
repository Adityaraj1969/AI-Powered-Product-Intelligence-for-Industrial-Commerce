import re
from typing import Optional
from src.config import ALL_PLACEHOLDERS, OFFICIAL_PLACEHOLDERS
from src.models import RawProductInput

def is_placeholder(value: Optional[str]) -> bool:
    if not value or not isinstance(value, str):
        return True
    val_upper = value.strip().upper()
    
    # Check exact match against official/all
    for p in ALL_PLACEHOLDERS:
        if val_upper == p.upper():
            return True
            
    if re.match(r'^--\s*.*\s*--$', value.strip()):
        return True
    return False

def strip_placeholders(raw: RawProductInput) -> RawProductInput:
    cleaned = raw.model_copy()
    if is_placeholder(cleaned.e1_brand):
        cleaned.e1_brand = None
    if is_placeholder(cleaned.unilog_brand):
        cleaned.unilog_brand = None
    if is_placeholder(cleaned.dib_brand):
        cleaned.dib_brand = None
    return cleaned

def resolve_brand_fallback(raw: RawProductInput) -> Optional[str]:
    if not is_placeholder(raw.e1_brand) and raw.e1_brand is not None:
        return raw.e1_brand
    if not is_placeholder(raw.unilog_brand) and raw.unilog_brand is not None:
        return raw.unilog_brand
    if not is_placeholder(raw.dib_brand) and raw.dib_brand is not None:
        return raw.dib_brand
    
    if raw.part_manuf and not is_placeholder(raw.part_manuf):
        # strip parenthesized code suffix
        val = raw.part_manuf.strip()
        val = re.sub(r'\s*\([^)]*\)$', '', val)
        return val.strip()
    return None

if __name__ == "__main__":
    test_raw = RawProductInput(
        mfg_part_num="123",
        part_desc="Test Part",
        e1_brand="UNKNOWN",
        unilog_brand="-- NONE --",
        dib_brand="TBD",
        part_manuf="Freud Inc (2435)"
    )
    print("Original:")
    print(test_raw)
    cleaned = strip_placeholders(test_raw)
    print("Cleaned:")
    print(cleaned)
    fallback = resolve_brand_fallback(test_raw)
    print("Fallback:", fallback)
    assert cleaned.e1_brand is None
    assert cleaned.unilog_brand is None
    assert cleaned.dib_brand is None
    assert fallback == "Freud Inc"
    print("placeholder.py tests passed!")
