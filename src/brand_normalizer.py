import re
from src.preprocessor import clean_value, extract_clean_manufacturer

def strip_legal_suffix(name):
    """
    Strips legal entity suffixes ('Inc', 'LLC', 'Corp', 'Corporation', 'Co', 'Company')
    ONLY when they appear as a separate trailing word at the end of the string.
    """
    pattern = r'(?:,\s*|\s+)(?:Corporation|Company|Corp|Llc|Inc|Co)\.?$'
    prev = None
    curr = name.strip()
    while curr != prev:
        prev = curr
        curr = re.sub(pattern, '', curr, flags=re.IGNORECASE).strip()
    return curr

def normalize_brand_and_manufacturer(row):
    """
    Documented best-effort Manufacturer and Brand Normalizer:
    1. Extracts clean manufacturer and brand fields, stripping parenthetical vendor codes.
    2. Strips legal entity suffixes ('Inc', 'LLC', 'Corp', 'Corporation', 'Co', 'Company') for BRAND_NAME.
    3. Preserves or attaches ®/™ trademark symbols for verified industrial brand entities.
    4. Returns tuple (MANUFACTURER_NAME, BRAND_NAME, TRADE_NAME, confidence_score, flag_reason).
    """
    part_desc = clean_value(row.get('Part_Desc', ''))
    mfg_part_num = clean_value(row.get('Mfg_Part_Num', ''))
    raw_manuf = extract_clean_manufacturer(row.get('Part_Manuf', ''))
    e1_brand = clean_value(row.get('E1_Brand', ''))
    unilog_brand = clean_value(row.get('Unilog_Brand', ''))
    dib_brand = clean_value(row.get('DIB_Brand', ''))
    
    combined = f"{part_desc} {mfg_part_num} {raw_manuf} {e1_brand} {unilog_brand} {dib_brand}".strip()
    
    # 1. Standard Brand Mapping Rules
    BRAND_PATTERNS = [
        (r'diablo', 'Freud Inc', 'Diablo®', ''),
        (r'freud', 'Freud Inc', 'Freud®', ''),
        (r'3m|cubitron', '3M Company', '3M®', 'Cubitron II'),
        (r'milwaukee|milw', 'Milwaukee Tool', 'Milwaukee®', ''),
        (r'mirka|hiolit|abranet', 'Mirka USA', 'Mirka®', ''),
        (r'dewalt|dewlt', 'Stanley Black & Decker', 'DEWALT®', ''),
        (r'black & decker|black\+decker', 'Stanley Black & Decker', 'BLACK+DECKER®', ''),
        (r'makita', 'Makita U.S.A., Inc.', 'Makita®', ''),
        (r'festool', 'Festool USA', 'Festool®', ''),
        (r'kreg', 'Kreg Tool Company', 'Kreg®', ''),
        (r'edge eyewear', 'Edge Eyewear Inc', 'Edge Eyewear®', ''),
        (r'us tape|u s tape', 'U.S. Tape Company', 'U.S. Tape®', ''),
        (r'philips|phillips', 'Signify North America Corporation', 'Philips®', ''),
        (r'kichler', 'Kichler Lighting LLC', 'Kichler®', ''),
        (r'satco', 'Satco Products, Inc.', 'Satco®', ''),
        (r'leviton', 'Leviton Manufacturing Co., Inc.', 'Leviton®', ''),
        (r'southwire', 'Southwire Company, LLC', 'Southwire®', ''),
        (r'trex', 'Trex Company, Inc.', 'Trex®', ''),
        (r'timbertech', 'The AZEK Company', 'TimberTech®', ''),
        (r'boise cascade', 'Boise Cascade Company', 'Boise Cascade®', ''),
        (r'parksite', 'Parksite Inc', 'Parksite®', ''),
        (r'us lumber|u s lumber', 'U.S. Lumber Group', 'U.S. Lumber®', ''),
        (r'united window', 'United Window & Door', 'United Window & Door®', ''),
        (r'frigidaire', 'Rheem Manufacturing', 'FRIGIDAIRE®', ''),
        (r'whirlpool', 'Whirlpool Corporation', 'Whirlpool®', '')
    ]

    for pattern, mfr, brand, trade in BRAND_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return mfr, brand, trade, 1.0, ""

    # 2. Algorithmic Normalization if no specific brand pattern matched
    primary_manuf = raw_manuf or e1_brand or dib_brand or unilog_brand
    if primary_manuf:
        mfr_name = primary_manuf.title()
        # Strip legal suffix ONLY when appearing as a separate trailing word
        brand_clean = strip_legal_suffix(mfr_name)
        if brand_clean and not brand_clean.endswith(('®', '™')):
            brand_name = f"{brand_clean}®"
        else:
            brand_name = brand_clean
            
        # Check if generic or low confidence
        if mfr_name.lower() in ['commodity - unbranded', 'generic', 'unbranded']:
            return "Commodity Industrial", "-- Unbranded --", "", 0.4, "Generic or unbranded commodity item"
            
        return mfr_name, brand_name, "", 0.8, ""

    # Unbranded fallback
    return "Generic Industrial", "-- Unbranded --", "", 0.3, "Missing manufacturer and brand data"
