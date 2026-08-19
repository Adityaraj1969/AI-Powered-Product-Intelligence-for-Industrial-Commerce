import math
from typing import Optional

# Precompute 63-entry fraction lookup table
FRACTIONS = {}
for i in range(1, 64):
    num = i
    den = 64
    while num % 2 == 0 and den % 2 == 0:
        num //= 2
        den //= 2
    FRACTIONS[i / 64.0] = f"{num}/{den}"

def decimal_to_fraction(decimal_part: float, tolerance: float = 0.001) -> Optional[str]:
    sixty_fourths = round(decimal_part * 64)
    if sixty_fourths <= 0 or sixty_fourths >= 64:
        return None
    fraction_val = sixty_fourths / 64.0
    if abs(decimal_part - fraction_val) <= tolerance:
        return FRACTIONS[fraction_val]
    return None

def convert_dimension(value: float, uom: str = 'in') -> str:
    whole = int(value)
    frac = abs(value) - abs(whole)
    
    if frac == 0:
        return f"{whole} {uom}"
        
    fraction_str = decimal_to_fraction(frac)
    if fraction_str is None:
        return f"{value} {uom}"
        
    if whole == 0:
        return f"{fraction_str} {uom}"
        
    return f"{whole}-{fraction_str} {uom}"

if __name__ == "__main__":
    tests = [
        (50.25, 'in', '50-1/4 in'),
        (0.375, 'in', '3/8 in'),
        (24.0, 'in', '24 in'),
        (24.75, 'in', '24-3/4 in'),
        (0.015625, 'in', '1/64 in')
    ]
    for val, uom, expected in tests:
        res = convert_dimension(val, uom)
        print(f"convert_dimension({val}, '{uom}') -> '{res}' (expected '{expected}')")
        assert res == expected
    print("fraction_matrix.py tests passed!")
