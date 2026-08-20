import os
import openpyxl
import pandas as pd

from src.config import (
    BASE_DIR,
    GROUND_TRUTH_200_PATH,
    BRAND_LIST_PATH,
    UNICAT_LOV_PATH,
    FAUCETS_LOV_PATH,
    FITTINGS_LOV_PATH,
    GUIDELINES_DOCX_PATH,
    UOM_STANDARDS_PATH,
    DECIMAL_FRACTION_PATH
)

def check_reference_files_exist():
    """
    Returns a dict showing which reference files are present in BASE_DIR.
    """
    files = {
        'ground_truth_200': GROUND_TRUTH_200_PATH,
        'brand_list': BRAND_LIST_PATH,
        'unicat_lov': UNICAT_LOV_PATH,
        'faucets_lov': FAUCETS_LOV_PATH,
        'fittings_lov': FITTINGS_LOV_PATH,
        'guidelines_docx': GUIDELINES_DOCX_PATH,
        'uom_standards': UOM_STANDARDS_PATH,
        'decimal_fraction': DECIMAL_FRACTION_PATH
    }
    status = {k: os.path.exists(v) for k, v in files.items()}
    return status, files

def load_ground_truth_200(file_path=GROUND_TRUTH_200_PATH):
    """
    Loads 200-item Input vs Delivery Format sheets from Unilog-Sample_200_Items-Input-vs-Output.xlsx.
    Returns (df_input, df_expected_output).
    """
    if not os.path.exists(file_path):
        return None, None
        
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    
    input_sheet = [s for s in sheet_names if 'input' in s.lower()][0]
    output_sheet = [s for s in sheet_names if 'delivery' in s.lower() or 'output' in s.lower()][0]
    
    df_input = pd.read_excel(file_path, sheet_name=input_sheet)
    df_output = pd.read_excel(file_path, sheet_name=output_sheet)
    
    return df_input, df_output

def load_approved_brand_list(file_path=BRAND_LIST_PATH):
    """
    Loads UniCat_Manufacturer_and_Brand_List.xlsx (27k+ entries).
    Returns lookup dict mapping normalized key -> (Approved Manufacturer Name, Approved Brand Name, Trade Name).
    """
    if not os.path.exists(file_path):
        return {}
        
    df = pd.read_excel(file_path)
    brand_dict = {}
    
    for idx, row in df.iterrows():
        mfr = str(row.get('MANUFACTURER_NAME', '') or row.get('Manufacturer', '') or '').strip()
        brand = str(row.get('BRAND_NAME', '') or row.get('Brand', '') or '').strip()
        trade = str(row.get('TRADE_NAME', '') or row.get('Trade Name', '') or '').strip()
        
        if mfr and mfr.lower() != 'nan':
            key_mfr = mfr.lower()
            brand_dict[key_mfr] = (mfr, brand if brand else mfr, trade)
        if brand and brand.lower() != 'nan':
            key_brand = brand.lower()
            brand_dict[key_brand] = (mfr if mfr else brand, brand, trade)
            
    return brand_dict

def load_lov_allowed_values(lov_files=None):
    """
    Loads allowed LOV values from LOV excel files.
    Returns set of allowed values and dict mapping (classpath, label) -> set of allowed values.
    """
    if lov_files is None:
        lov_files = [UNICAT_LOV_PATH, FAUCETS_LOV_PATH, FITTINGS_LOV_PATH]
        
    allowed_values_set = set()
    classpath_label_values = {}
    
    for path in lov_files:
        if os.path.exists(path):
            try:
                df = pd.read_excel(path)
                for idx, row in df.iterrows():
                    val = str(row.get('Attribute Value', '') or row.get('ATTRIBUTE_VALUE', '') or row.get('Allowed Value', '') or '').strip()
                    lbl = str(row.get('Attribute Label', '') or row.get('ATTRIBUTE_LABEL', '') or '').strip()
                    cp = str(row.get('Classpath', '') or row.get('CLASSPATH', '') or '').strip()
                    
                    if val and val.lower() != 'nan':
                        allowed_values_set.add(val.lower())
                        if lbl:
                            key = (cp.lower(), lbl.lower())
                            if key not in classpath_label_values:
                                classpath_label_values[key] = set()
                            classpath_label_values[key].add(val.lower())
            except Exception as e:
                print(f"Warning loading LOV file {path}: {e}")
                
    return allowed_values_set, classpath_label_values

def load_decimal_fraction_table(file_path=DECIMAL_FRACTION_PATH):
    """
    Parses Decimal_Fraction.xlsx which contains 4 stacked Fraction|Decimal column blocks.
    Returns dict mapping fraction string -> decimal string.
    """
    if not os.path.exists(file_path):
        return {}
        
    df = pd.read_excel(file_path)
    frac_map = {}
    
    cols = df.columns
    for i in range(0, len(cols) - 1, 2):
        col_frac = cols[i]
        col_dec = cols[i + 1]
        for idx, row in df.iterrows():
            f_val = str(row[col_frac]).strip()
            d_val = str(row[col_dec]).strip()
            if f_val and d_val and f_val.lower() != 'nan' and d_val.lower() != 'nan':
                frac_map[f_val] = d_val
                
    return frac_map
