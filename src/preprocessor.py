import re
from fractions import Fraction
from src.config import PLACEHOLDERS

def clean_value(val):
    """
    Strips placeholder values like '-- Unbranded --', '-- No Unilog Brand --', 
    '--', '-', 'N/A', 'nan', etc. and returns a clean string or empty string.
    """
    if val is None or (isinstance(val, float) and str(val) == 'nan'):
        return ""
    val_str = str(val).strip()
    if val_str.lower() in PLACEHOLDERS or val_str.lower() == 'nan':
        return ""
    return val_str

def extract_clean_manufacturer(raw_manuf):
    """
    Cleans raw Part_Manuf strings such as 'Freud Inc (2435)' -> 'Freud Inc'
    or 'Jam Industrial Supply LLC (JAMIN)' -> 'Jam Industrial Supply LLC'.
    Strips trailing parenthetical vendor codes.
    """
    cleaned = clean_value(raw_manuf)
    if not cleaned:
        return ""
    cleaned = re.sub(r'\s*\([A-Za-z0-9]+\)\s*$', '', cleaned).strip()
    return cleaned

def convert_fraction_to_decimal(val):
    """
    Algorithmic conversion of fraction strings (e.g. '1/2' -> 0.5, '33-7/16' -> 33.4375).
    """
    val = clean_value(val)
    if not val:
        return ""
    
    mixed_match = re.match(r'^(\d+)[\s\-]+(\d+)/(\d+)$', val)
    if mixed_match:
        whole = int(mixed_match.group(1))
        num = int(mixed_match.group(2))
        den = int(mixed_match.group(3))
        if den != 0:
            return f"{whole + num / den:.4g}"
            
    frac_match = re.match(r'^(\d+)/(\d+)$', val)
    if frac_match:
        num = int(frac_match.group(1))
        den = int(frac_match.group(2))
        if den != 0:
            return f"{num / den:.4g}"
            
    return val

def convert_decimal_to_fraction(val):
    """
    Algorithmic conversion of decimal float to nearest 1/64 fraction.
    E.g. 0.5 -> '1/2', 0.4375 -> '7/16', 33.4375 -> '33-7/16'.
    """
    val_str = clean_value(val)
    if not val_str:
        return ""
    try:
        num = float(val_str)
        whole = int(num)
        remainder = abs(num - whole)
        if remainder < 1e-4:
            return str(whole)
        
        # Round to nearest 1/64
        fraction_64 = round(remainder * 64)
        if fraction_64 == 0:
            return str(whole)
        if fraction_64 == 64:
            return str(whole + (1 if num >= 0 else -1))
            
        frac = Fraction(fraction_64, 64)
        frac_str = f"{frac.numerator}/{frac.denominator}"
        if whole != 0:
            return f"{whole}-{frac_str}"
        return frac_str
    except ValueError:
        return val_str
