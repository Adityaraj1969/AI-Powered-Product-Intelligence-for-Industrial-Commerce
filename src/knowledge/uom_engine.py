import re

UOM_MAP = {
    # Length
    'inch': 'in', 'inches': 'in', '"': 'in', 'in.': 'in', 'in': 'in',
    # Linear
    'foot': 'ft', 'feet': 'ft', "'": 'ft', 'ft.': 'ft', 'ft': 'ft',
    # Flow
    'gallons per minute': 'gpm', 'gpm': 'gpm', 'gal/min': 'gpm',
    # Pressure
    'pounds per square inch': 'psi', 'lbs per square inch': 'psi',
    'psi': 'psi', 'lb': 'lb', 'lbs': 'lb', 'pounds': 'lb', '#': 'psi',
    # Sound
    'decibels': 'dBA', 'db': 'dBA', 'dba': 'dBA',
    # Voltage
    'volts': 'V', 'volt': 'V', 'v': 'V', 'vac': 'V', 'vdc': 'V',
    # Amperage
    'amps': 'A', 'ampere': 'A', 'amperes': 'A', 'a': 'A', 'amp': 'A',
    # Frequency
    'hertz': 'Hz', 'hz': 'Hz',
    # Temperature
    'degrees fahrenheit': 'deg F', 'deg f': 'deg F', 'fahrenheit': 'deg F',
    'degrees celsius': 'deg C', 'deg c': 'deg C', 'celsius': 'deg C',
    # Energy
    'kilowatt hour': 'kW-hr', 'kwh': 'kW-hr', 'kw-hr': 'kW-hr',
    # Weight
    'oz': 'oz', 'ounce': 'oz', 'ounces': 'oz',
    'kg': 'kg', 'kilogram': 'kg', 'kilograms': 'kg',
    'g': 'g', 'gram': 'g', 'grams': 'g',
}

def standardize_uom(raw_uom: str) -> str:
    if not raw_uom:
        return ""
    normalized = raw_uom.strip().lower()
    return UOM_MAP.get(normalized, raw_uom.strip())

def format_measurement(value: float | str, raw_uom: str) -> str:
    std_uom = standardize_uom(raw_uom)
    return f"{value} {std_uom}"

def validate_uom_spacing(text: str) -> bool:
    # A simple regex to check for digit immediately followed by a letter
    if re.search(r'\d[a-zA-Z]', text):
        return False
    return True

if __name__ == "__main__":
    assert standardize_uom("inches") == "in"
    assert standardize_uom("Hz") == "Hz"
    assert format_measurement(24, 'inches') == '24 in'
    assert validate_uom_spacing("24 in") == True
    assert validate_uom_spacing("24in") == False
    print("uom_engine.py tests passed!")
