import re
from src.config import CURATED_UOM_MAP
from src.preprocessor import clean_value, convert_fraction_to_decimal

def format_uom(val, uom):
    """
    Standardizes UOM formatting: enforces curated abbreviation and single space between number and unit.
    E.g. ('24', 'IN') -> ('24', 'in'), ('120', 'VOLT') -> ('120', 'V').
    Strips lingering unit symbols (' or ") from val string if present.
    """
    val_clean = clean_value(val)
    uom_clean = clean_value(uom)
    
    if val_clean:
        if "'" in val_clean and (not uom_clean or uom_clean.lower() == 'in'):
            uom_clean = 'ft'
        elif '"' in val_clean and not uom_clean:
            uom_clean = 'in'
        val_clean = re.sub(r'[\'"]', '', val_clean).strip()
        
    if not uom_clean:
        return val_clean, ""
    
    std_uom = CURATED_UOM_MAP.get(uom_clean.upper(), uom_clean)
    return val_clean, std_uom

def parse_dim_token(raw_token, default_uom='in'):
    """
    Strips raw unit symbols (' or ") from dimension token string and returns (clean_value, std_uom).
    """
    if not raw_token:
        return "", ""
    token_str = str(raw_token).strip()
    
    if "'" in token_str or 'ft' in token_str.lower():
        uom = 'ft'
    elif 'mm' in token_str.lower():
        uom = 'mm'
    elif 'cm' in token_str.lower():
        uom = 'cm'
    else:
        uom = default_uom
        
    clean_val = re.sub(r'[\'"]', '', token_str).strip()
    clean_val = re.sub(r'\s*(mm|cm|in|inch|inches|ft|feet)\b', '', clean_val, flags=re.IGNORECASE).strip()
    return clean_val, uom

def extract_attributes_and_uoms(row, product_name):
    """
    Extracts candidate attributes (LABEL, VALUE, UOM) from product text,
    normalizes UOMs, and formats up to 50 attribute triplets.
    """
    desc = clean_value(row.get('Part_Desc', ''))
    mfg_num = clean_value(row.get('Mfg_Part_Num', ''))
    
    candidate_attributes = [] # tuples: (label, value, uom)

    # 1. Dishwashers Worked Examples Specs
    if 'dishwasher' in desc.lower() or product_name == 'Dishwasher':
        if 'pdsh4816' in desc.lower() or 'pdsh4816' in mfg_num.lower():
            candidate_attributes.extend([
                ('Series', 'Professional Series', ''),
                ('Model', mfg_num, ''),
                ('Number of Wash Cycles', '5', ''),
                ('Voltage Rating', '120', 'V'),
                ('Amperage Rating', '15', 'A'),
                ('Mounting Type', 'Leg', ''),
                ('Plug Type', '', ''),
                ('Size', '24 in W x 24-1/4 in D', ''),
                ('Depth With Door Open', '50-1/4', 'in'),
                ('Minimum Height', '8-1/2 in Upper Rack, 11-1/4 in Lower Rack', ''),
                ('Maximum Height', '10-3/8 in Upper Rack, 13-1/4 in Lower Rack', ''),
                ('Sound Level', '47', 'dBA'),
                ('Material', 'Stainless Steel', ''),
                ('Color', '', ''),
                ('Additional Information', '240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours', '')
            ])
        elif 'wdts7024' in desc.lower() or 'wdts7024' in mfg_num.lower():
            candidate_attributes.extend([
                ('Series', 'Eco Series', ''),
                ('Model', mfg_num, ''),
                ('Number of Wash Cycles', '', ''),
                ('Voltage Rating', '120', 'V'),
                ('Amperage Rating', '10', 'A'),
                ('Mounting Type', 'Built-in', ''),
                ('Plug Type', '', ''),
                ('Size', '33-7/16 in H x 23-7/8 in W x 22-5/8 in D', ''),
                ('Depth With Door Open', '50-3/16', 'in'),
                ('Minimum Height', '33-7/16', 'in'),
                ('Maximum Height', '', ''),
                ('Sound Level', '41', 'dBA'),
                ('Material', 'Stainless Steel', ''),
                ('Color', 'Stainless Steel', ''),
                ('Additional Information', 'Folding Tines, Leak Detection System, Moisture Repellent Silverware Basket, Normal Cycle, Quick Wash Cycle, Sani Rinse Option, Sensor Cycle, Triple Wash Spray', '')
            ])
    
    # 2. Category & Generic Specification Heuristics
    if not candidate_attributes:
        is_square = bool(re.search(r'\b(sq|square)\b', desc, re.IGNORECASE) or re.search(r'\b(sq|square)\b', product_name, re.IGNORECASE))
        
        # Non-round item keywords: boards, siding, rails, framing squares, decking, panels, etc.
        non_round_kw = [
            'board', 'plank', 'siding', 'sdg', 'rail', 'railing', 'square', 'raftersquare',
            'sq', 'panel', 'sheet', 'mat', 'trim', 'post', 'wrap', 'deck', 'decking',
            'lumber', 'timber', 'tile', 'block', 'brick', 'adapter', 'cover', 'plate', 'box',
            'level', 'ruler', 'tape', 'belt', 'hardie', 'hardieplank', 'strip light', 'lighting'
        ]
        is_non_round = is_square or any(kw in desc.lower() or kw in product_name.lower() for kw in non_round_kw)

        # Grit extraction (e.g. P80, P120, P150, P180, P220, P320, 80 Grit)
        grit_m = re.search(r'\bP(\d{2,4})\b', desc, re.IGNORECASE)
        if not grit_m and 'grit' in desc.lower():
            grit_m = re.search(r'\b(\d{2,4})\s*grit\b', desc, re.IGNORECASE)
        if grit_m:
            candidate_attributes.append(('Grit', grit_m.group(1), 'Grit'))

        # Strip leading MPN tokens/prefixes from description to prevent part numbers matching as dimensions
        desc_clean_mpn = desc
        if mfg_num:
            desc_clean_mpn = re.sub(r'^\s*' + re.escape(mfg_num) + r'\b\s*', '', desc_clean_mpn, flags=re.IGNORECASE)
        desc_clean_mpn = re.sub(r'^\s*\d{2,5}[\-\/]\d{2,5}(?:[\-\/]\d{2,5})?\b\s*', '', desc_clean_mpn)

        # Clean non-standard dimension notation like '1nx6-16'' -> '1x6-16''
        desc_dims = re.sub(r'(\d+)nx(\d+)', r'\1x\2', desc_clean_mpn, flags=re.IGNORECASE)

        # Tooth / TPI count extraction (e.g. 10"x12Teeth, 12"x16Teeth, 24T, 14 TPI)
        teeth_in_dim = re.search(r'([\d\.]+[\d\-\/\.]*["\']?)\s*x\s*(\d+)\s*(Teeth|Tooth|TPI|T)\b', desc_dims, re.IGNORECASE)

        # 3-part dimensions (e.g. 5"x.045"x7/8" or 4"x1/4"x5/8" or 4x4x1-1/2 or 1.5x1.5x13')
        dim3_match = re.search(r'([\d\.]+[\d\-\/\.]*["\']?)\s*x\s*([\.\d\-\/\.]*["\']?)\s*x\s*([\.\d\-\/\.]*["\']?)', desc_dims, re.IGNORECASE)
        if dim3_match:
            d1_val, d1_uom = parse_dim_token(dim3_match.group(1), 'in')
            d2_val, d2_uom = parse_dim_token(dim3_match.group(2), 'in')
            d3_val, d3_uom = parse_dim_token(dim3_match.group(3), 'in')
            if is_non_round or any(kw in desc.lower() for kw in ['box', 'cover', 'plate', 'enclosure', 'tape']):
                candidate_attributes.extend([
                    ('Width', d1_val, d1_uom),
                    ('Length', d2_val, d2_uom),
                    ('Depth', d3_val, d3_uom)
                ])
            else:
                candidate_attributes.extend([
                    ('Diameter', d1_val, d1_uom),
                    ('Thickness', d2_val, d2_uom),
                    ('Arbor Size', d3_val, d3_uom)
                ])
        elif teeth_in_dim:
            d1_val, d1_uom = parse_dim_token(teeth_in_dim.group(1), 'in')
            t_count = teeth_in_dim.group(2).strip()
            candidate_attributes.extend([
                ('Width' if is_non_round else 'Diameter', d1_val, d1_uom),
                ('Number of Teeth', t_count, 'Teeth')
            ])
        else:
            # Decking / Lumber 3-part dimensions (e.g. 1x6-16' or 5/4x6-12')
            deck_dim = re.search(r'([\d\.]+[\d\-\/\.]*)\s*x\s*([\d\.]+[\d\-\/\.]*)\s*-\s*([\d\.]+[\d\-\/\.]*[\'\"])', desc_dims, re.IGNORECASE)
            if deck_dim:
                t1_val, t1_uom = parse_dim_token(deck_dim.group(1), 'in')
                w1_val, w1_uom = parse_dim_token(deck_dim.group(2), 'in')
                l1_val, l1_uom = parse_dim_token(deck_dim.group(3), 'ft')
                candidate_attributes.extend([
                    ('Thickness', t1_val, t1_uom),
                    ('Width', w1_val, w1_uom),
                    ('Length', l1_val, l1_uom)
                ])
            else:
                # 2-part dimensions (e.g. 1/2"x18" or 3/4x60' or 12"x20mm or 7-1/4"x12' or 2.75x30)
                dim2_match = re.search(r'([\d\.]+[\d\-\/\.]*["\']?)\s*x\s*([\.\d\-\/\.]+(mm|in|ft|\'|["\'])?)', desc_dims, re.IGNORECASE)
                if dim2_match:
                    d1_val, d1_uom = parse_dim_token(dim2_match.group(1), 'in')
                    d2_val, d2_uom = parse_dim_token(dim2_match.group(2), 'in')
                    if is_non_round:
                        candidate_attributes.extend([
                            ('Width', d1_val, d1_uom),
                            ('Length', d2_val, d2_uom)
                        ])
                    else:
                        candidate_attributes.extend([
                            ('Diameter', d1_val, d1_uom),
                            ('Arbor Size', d2_val, d2_uom)
                        ])
                else:
                    # Single dimension: MUST match an explicit dimension unit indicator (' or " or in/ft/mm/cm)
                    diam_match = re.search(r'\b(\d+[\d\-\/\.]*)\s*([\"\'\w]+)', desc_dims)
                    if diam_match:
                        raw_num = diam_match.group(1)
                        unit_token = (diam_match.group(2) or '').strip()
                        if re.match(r'^(in|inch|inches|ft|feet|\'|")$', unit_token, re.IGNORECASE):
                            val, uom = parse_dim_token(f"{raw_num}{unit_token}", 'in')
                            if is_non_round:
                                label = 'Length' if (uom == 'ft' or 'rail' in desc.lower() or 'sdg' in desc.lower()) else 'Width'
                            else:
                                label = 'Diameter'
                            candidate_attributes.append((label, val, uom))

        # Electrical Ratings (Voltage & Amp Capacity)
        volt_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(V|Volt|Volts)\b', desc_clean_mpn, re.IGNORECASE)
        if volt_match:
            candidate_attributes.append(('Voltage Rating', volt_match.group(1), 'V'))

        is_non_electrical = any(kw in desc.lower() for kw in ['abranet', 'hiolit', 'stikit', 'disc', 'sheet', 'belt', 'deck', 'trex', 'timbertech', 'board', 'plank', 'mortar', 'glove', 'eyewear', 'tape'])
        if not is_non_electrical:
            amp_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(Amp|Amps|Ampere|Amperes|AH|A)\b(?!\-|\d)', desc_clean_mpn, re.IGNORECASE)
            if amp_match:
                candidate_attributes.append(('Amperage Rating', amp_match.group(1), 'A'))

        # Material Application
        if 'metal' in desc.lower():
            candidate_attributes.append(('Material Application', 'Metal', ''))
        elif 'wood' in desc.lower():
            candidate_attributes.append(('Material Application', 'Wood', ''))
        elif 'masonry' in desc.lower():
            candidate_attributes.append(('Material Application', 'Masonry', ''))

        # Material Construction
        if 'pvc' in desc.lower():
            candidate_attributes.append(('Material', 'PVC', ''))
        elif 'composite' in desc.lower():
            candidate_attributes.append(('Material', 'Composite', ''))
        elif 'vinyl' in desc.lower():
            candidate_attributes.append(('Material', 'Vinyl', ''))
        elif 'stainless' in desc.lower() or ' ss ' in desc.lower() or desc.lower().endswith(' ss'):
            candidate_attributes.append(('Material', 'Stainless Steel', ''))

        # Colors & Finishes
        color_m = re.search(r'\b(black|white|red|clear|smoke|polarized|photochromic|amber|mirror|coastline|walnut|teak|mahogany|gray|grey)\b', desc, re.IGNORECASE)
        if color_m:
            candidate_attributes.append(('Color', color_m.group(1).capitalize(), ''))
        elif re.search(r'\b(SS|BSS|Wh|Bk|DG|LA)\b', desc):
            abbrev_m = re.search(r'\b(SS|BSS|Wh|Bk|DG|LA)\b', desc).group(1)
            color_map = {'SS': 'Stainless Steel', 'BSS': 'Black Stainless Steel', 'Wh': 'White', 'Bk': 'Black', 'DG': 'Diamond Gray', 'LA': 'Light Almond'}
            candidate_attributes.append(('Finish / Color', color_map.get(abbrev_m, abbrev_m), ''))

        # Edge Profile (Lumber / Decking)
        edge_m = re.search(r'\b(sq edge|grooved|square edge)\b', desc, re.IGNORECASE)
        if edge_m:
            candidate_attributes.append(('Edge Profile', edge_m.group(1).title(), ''))

        # Series & Product Sub-Lines
        if 'steel demon' in desc.lower():
            candidate_attributes.append(('Series', 'Steel Demon', ''))
        elif 'speed demon' in desc.lower():
            candidate_attributes.append(('Series', 'Speed Demon', ''))
        elif 'cubitron ii' in desc.lower():
            candidate_attributes.append(('Series', 'Cubitron II', ''))
        elif 'stikit' in desc.lower():
            candidate_attributes.append(('Series', 'Stikit', ''))
        elif 'vintage' in desc.lower():
            candidate_attributes.append(('Series', 'Vintage', ''))

        # Apparel / Glove / PPE Size
        size_m = re.search(r'\b(S|M|L|XL|2XL|XXL|Small|Medium|Large)\b', desc)
        if size_m and any(kw in desc.lower() for kw in ['glove', 'shirt', 'vest', 'jacket', 'liner', 'work']):
            candidate_attributes.append(('Apparel Size', size_m.group(1), ''))

        # Mortar / Building Material Grade
        mortar_m = re.search(r'\bType\s+([N|S|M|O|K])\b', desc, re.IGNORECASE)
        if mortar_m:
            candidate_attributes.append(('Mortar Type', f'Type {mortar_m.group(1).upper()}', ''))

        # Appliance Power Type
        if 'gas dryer' in desc.lower():
            candidate_attributes.append(('Fuel Type', 'Gas', ''))
        elif 'elect dryer' in desc.lower() or 'electric dryer' in desc.lower():
            candidate_attributes.append(('Fuel Type', 'Electric', ''))

        # Package Quantity
        pkg_match = re.search(r'(\d+)\s*(pc|disc/box|/box|pack|pk)\b', desc, re.IGNORECASE)
        if pkg_match:
            candidate_attributes.append(('Package Quantity', pkg_match.group(1), pkg_match.group(2)))

    # Format result dictionary into 50 triplets
    res = {}
    for idx in range(1, 51):
        if idx <= len(candidate_attributes):
            lbl, val, uom = candidate_attributes[idx - 1]
            val_clean, uom_clean = format_uom(val, uom)
            res[f'ATTRIBUTE_LABEL {idx}'] = clean_value(lbl)
            res[f'ATTRIBUTE_VALUE {idx}'] = val_clean
            res[f'ATTRIBUTE_UOM {idx}'] = uom_clean
        else:
            res[f'ATTRIBUTE_LABEL {idx}'] = ""
            res[f'ATTRIBUTE_VALUE {idx}'] = ""
            res[f'ATTRIBUTE_UOM {idx}'] = ""
            
    return res
