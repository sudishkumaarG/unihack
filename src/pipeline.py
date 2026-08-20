import os
import csv
import re
import pandas as pd

from src.config import INPUT_CSV_PATH, DELIVERY_HEADERS, OUTPUT_CSV_PATH
from src.preprocessor import clean_value, extract_clean_manufacturer
from src.brand_normalizer import normalize_brand_and_manufacturer
from src.taxonomy import classify_product
from src.attribute_extractor import extract_attributes_and_uoms
from src.description_builder import build_descriptions

def run_pipeline(input_path=INPUT_CSV_PATH, output_path=OUTPUT_CSV_PATH):
    """
    Executes the product intelligence processing pipeline on input records
    and outputs a standardized 252-column CSV file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    df_input = pd.read_csv(input_path)
    output_rows = []
    flagged_rows = []
    
    total_records = len(df_input)
    print(f"Processing {total_records} input records...")

    for idx, row in df_input.iterrows():
        row_dict = row.to_dict()
        
        # Preprocessing
        mfg_part_num = clean_value(row_dict.get('Mfg_Part_Num', ''))
        part_desc = clean_value(row_dict.get('Part_Desc', ''))
        e1_brand = clean_value(row_dict.get('E1_Brand', ''))
        unilog_brand = clean_value(row_dict.get('Unilog_Brand', ''))
        dib_brand = clean_value(row_dict.get('DIB_Brand', ''))
        part_manuf = extract_clean_manufacturer(row_dict.get('Part_Manuf', ''))
        
        # Taxonomy Classification
        dept, class_name, fine, classpath, product_name = classify_product(part_desc, mfg_part_num)
        
        # Brand & Manufacturer Normalization
        mfr_name, brand_name, trade_name, brand_conf, brand_flag = normalize_brand_and_manufacturer(row_dict)
        
        # Attribute & UOM Extraction
        attributes_dict = extract_attributes_and_uoms(row_dict, product_name)
        
        # Description Building
        descriptions_dict = build_descriptions(row_dict, mfr_name, brand_name, trade_name, product_name, attributes_dict)
        
        # Confidence Assessment & Flagging
        confidence_score = brand_conf
        flag_reasons = []
        if brand_flag:
            flag_reasons.append(brand_flag)
        if not attributes_dict.get('ATTRIBUTE_VALUE 1'):
            confidence_score -= 0.2
            flag_reasons.append("Sparse attribute values extracted from raw title")
            
        if confidence_score < 0.7 or brand_name == "-- Unbranded --":
            flagged_rows.append({
                'row_index': idx + 1,
                'Mfg_Part_Num': mfg_part_num,
                'Part_Desc': part_desc,
                'confidence_score': round(max(confidence_score, 0.0), 2),
                'flag_reasons': "; ".join(flag_reasons) if flag_reasons else "Uncertain brand alignment (Needs human review)"
            })

        # 252-Column Record Assembly
        part_id = str(10000000 + idx + 1)
        sku = str(1500000 + idx + 1)
        
        record = {h: "" for h in DELIVERY_HEADERS}
        
        record['PART_NUMBER'] = part_id
        record['Dept'] = dept
        record['Class'] = class_name
        record['Fine'] = fine
        record['SKU - MY_PART_NUMBER'] = sku
        record['Mfg_Part_Num'] = mfg_part_num
        record['Part_Desc'] = part_desc
        record['E1_Brand'] = e1_brand if e1_brand else "-- Unbranded --"
        record['Unilog_Brand'] = unilog_brand if unilog_brand else "-- No Unilog Brand --"
        record['DIB_Brand'] = dib_brand if dib_brand else "-- No DIB Brand --"
        record['Part_Manuf'] = row_dict.get('Part_Manuf', '')
        
        record['MANUFACTURER_NAME'] = mfr_name
        record['BRAND_NAME'] = brand_name
        record['TRADE_NAME'] = trade_name
        record['MANUFACTURER_PART_NUMBER'] = mfg_part_num
        record['Classpath'] = classpath
        record['Product Name'] = product_name
        
        record['MOBILE_DESC'] = descriptions_dict['MOBILE_DESC']
        record['INVOICE_DESC'] = descriptions_dict['INVOICE_DESC']
        record['SHORT_DESC'] = descriptions_dict['SHORT_DESC']
        record['LONG_DESC1'] = descriptions_dict['LONG_DESC1']
        record['RETAIL_DESC'] = descriptions_dict['RETAIL_DESC']
        record['MARKETING_DESCRIPTION'] = descriptions_dict['MARKETING_DESCRIPTION']
        record['With'] = descriptions_dict['With']
        
        for f_idx in range(1, 21):
            key = f'ITEM_FEATURES_{f_idx}'
            record[key] = descriptions_dict.get(key, '')

        for attr_key, attr_val in attributes_dict.items():
            record[attr_key] = attr_val

        # Dedicated Dimension Column Population (LENGTH, WIDTH, HEIGHT)
        # Grounded strictly in extracted attributes from Part_Desc
        for i in range(1, 51):
            lbl = clean_value(attributes_dict.get(f'ATTRIBUTE_LABEL {i}', ''))
            val = clean_value(attributes_dict.get(f'ATTRIBUTE_VALUE {i}', ''))
            uom = clean_value(attributes_dict.get(f'ATTRIBUTE_UOM {i}', ''))
            if val:
                lbl_low = lbl.lower()
                if lbl_low == 'length' and not record['LENGTH']:
                    record['LENGTH'] = val
                    record['LENGTH_UOM'] = uom
                elif lbl_low == 'width' and not record['WIDTH']:
                    record['WIDTH'] = val
                    record['WIDTH_UOM'] = uom
                elif lbl_low == 'height' and not record['HEIGHT']:
                    record['HEIGHT'] = val
                    record['HEIGHT_UOM'] = uom
                elif lbl_low in ['depth', 'thickness'] and not record['HEIGHT']:
                    record['HEIGHT'] = val
                    record['HEIGHT_UOM'] = uom

        record['Actual Image (Yes/No)'] = 'Yes' if mfg_part_num else 'No'
        if mfg_part_num:
            safe_part = re.sub(r'[^A-Za-z0-9\_]', '_', mfg_part_num)
            clean_bname = re.sub(r'[^A-Za-z0-9\_]', '_', brand_name.replace('®','').replace('™',''))
            record['Product Image'] = f"{clean_bname}_{safe_part}.jpg"
            
        output_rows.append(record)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=DELIVERY_HEADERS)
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Successfully generated 252-column delivery CSV at {output_path}")
    print(f"Total rows: {len(output_rows)}, Flagged low-confidence rows: {len(flagged_rows)}")
    
    return output_rows, flagged_rows

if __name__ == '__main__':
    run_pipeline()
