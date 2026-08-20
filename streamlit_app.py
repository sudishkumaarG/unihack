import streamlit as st
import pandas as pd

from src.preprocessor import clean_value, extract_clean_manufacturer
from src.taxonomy import classify_product
from src.brand_normalizer import normalize_brand_and_manufacturer
from src.attribute_extractor import extract_attributes_and_uoms
from src.description_builder import build_descriptions
from src.config import DELIVERY_HEADERS

# Page Configuration & Styling
st.set_page_config(
    page_title="UniHack 2026 - AI Product Intelligence",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .badge {
        background-color: #3B82F6;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .desc-label {
        font-weight: 600;
        color: #334155;
        font-size: 0.9rem;
    }
    .desc-val {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        font-family: monospace;
        font-size: 0.95rem;
        color: #0F172A;
        margin-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ UniHack 2026 — AI Product Intelligence Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Live Product Enrichment Engine matching Unilog 252-Column Delivery Standard</div>', unsafe_allow_html=True)

# Preset Examples
PRESETS = {
    "DCB518ASTS06G (Diablo Sanding Belt)": {
        "mpn": "DCB518ASTS06G",
        "desc": "DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc",
        "manuf": "Freud / Diablo"
    },
    "9A-570-240 (Mirka Abranet Sheet)": {
        "mpn": "9A-570-240",
        "desc": "9A-570-240 Abranet 2.75x30",
        "manuf": "Mirka USA"
    },
    "ASH-40-40-04 (Emseal Legacy Tape)": {
        "mpn": "ASH-40-40-04",
        "desc": "1.5x1.5x13' Legacy Emseal Tape",
        "manuf": "Emseal Joint Systems Ltd"
    },
    "65-1224 (Satco Strip Light)": {
        "mpn": "65-1224",
        "desc": "65-1224 4' Led Strip Light",
        "manuf": "Satco Products"
    }
}

st.sidebar.header("📋 Sample Preset Selectors")
selected_preset_name = st.sidebar.selectbox("Choose a sample input record:", list(PRESETS.keys()))
preset_data = PRESETS[selected_preset_name]

# Input Form
with st.form(key="enrichment_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        raw_desc_input = st.text_input("Raw Product Description", value=preset_data["desc"], help="Raw title or description text from catalog feed")
    with col2:
        mfg_num_input = st.text_input("Mfg Part Number (MPN)", value=preset_data["mpn"])
        
    part_manuf_input = st.text_input("Raw Part Manufacturer (Optional)", value=preset_data["manuf"])
    
    submit_button = st.form_submit_button(label="🚀 Enrich Product Record", type="primary")

def enrich_single_record(mfg_num, raw_desc, manuf=''):
    """
    Calls exact pipeline modules from src/ to enrich a single record.
    """
    row_dict = {
        'Mfg_Part_Num': mfg_num,
        'Part_Desc': raw_desc,
        'Part_Manuf': manuf,
        'E1_Brand': '',
        'Unilog_Brand': '',
        'DIB_Brand': ''
    }
    dept, class_name, fine, classpath, product_name = classify_product(raw_desc, mfg_num)
    mfr_name, brand_name, trade_name, brand_conf, brand_flag = normalize_brand_and_manufacturer(row_dict)
    attributes_dict = extract_attributes_and_uoms(row_dict, product_name)
    descriptions_dict = build_descriptions(row_dict, mfr_name, brand_name, trade_name, product_name, attributes_dict)
    
    record = {h: '' for h in DELIVERY_HEADERS}
    record['Mfg_Part_Num'] = mfg_num
    record['Part_Desc'] = raw_desc
    record['MANUFACTURER_NAME'] = mfr_name
    record['BRAND_NAME'] = brand_name
    record['TRADE_NAME'] = trade_name
    record['Classpath'] = classpath
    record['Product Name'] = product_name
    record['Dept'] = dept
    record['Class'] = class_name
    record['Fine'] = fine
    
    for k in ['MOBILE_DESC', 'INVOICE_DESC', 'SHORT_DESC', 'LONG_DESC1', 'RETAIL_DESC', 'MARKETING_DESCRIPTION', 'With']:
        record[k] = descriptions_dict.get(k, '')
        
    for f_idx in range(1, 21):
        key = f'ITEM_FEATURES_{f_idx}'
        record[key] = descriptions_dict.get(key, '')
        
    for attr_key, attr_val in attributes_dict.items():
        record[attr_key] = attr_val
        
    for i in range(1, 51):
        lbl = clean_value(attributes_dict.get(f'ATTRIBUTE_LABEL {i}', ''))
        val = clean_value(attributes_dict.get(f'ATTRIBUTE_VALUE {i}', ''))
        uom = clean_value(attributes_dict.get(f'ATTRIBUTE_UOM {i}', ''))
        if val:
            lbl_low = lbl.lower()
            if lbl_low == 'length' and not record['LENGTH']:
                record['LENGTH'] = val; record['LENGTH_UOM'] = uom
            elif lbl_low == 'width' and not record['WIDTH']:
                record['WIDTH'] = val; record['WIDTH_UOM'] = uom
            elif lbl_low in ['height', 'depth', 'thickness'] and not record['HEIGHT']:
                record['HEIGHT'] = val; record['HEIGHT_UOM'] = uom

    return record, attributes_dict

if submit_button or raw_desc_input:
    record, attributes_dict = enrich_single_record(mfg_num_input.strip(), raw_desc_input.strip(), part_manuf_input.strip())
    
    st.subheader("🔍 Enriched Output Results")
    
    # 1. Primary Identifiers & Taxonomy
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Manufacturer", record['MANUFACTURER_NAME'] or "N/A")
    m2.metric("Brand Name", record['BRAND_NAME'] or "N/A")
    m3.metric("Trade Name", record['TRADE_NAME'] or "N/A")
    m4.metric("Product Name", record['Product Name'] or "N/A")
    
    st.markdown(f"**Taxonomy Classpath:** `<span class='badge'>{record['Classpath']}</span>`", unsafe_allow_html=True)
    st.write("")
    
    # 2. Extracted Attributes & Dedicated Dimensions
    col_attr, col_dim = st.columns([2, 1])
    
    with col_attr:
        st.markdown("### 🏷️ Extracted Specification Attributes")
        attr_list = []
        for i in range(1, 51):
            lbl = record.get(f'ATTRIBUTE_LABEL {i}')
            val = record.get(f'ATTRIBUTE_VALUE {i}')
            uom = record.get(f'ATTRIBUTE_UOM {i}')
            if pd.notna(lbl) and str(lbl).strip() != '':
                attr_list.append({
                    "Attribute Label": lbl,
                    "Attribute Value": val,
                    "Attribute UOM": uom if pd.notna(uom) else ""
                })
        if attr_list:
            st.dataframe(pd.DataFrame(attr_list), use_container_width=True)
        else:
            st.info("No candidate spec attributes extracted from raw description text.")
            
    with col_dim:
        st.markdown("### 📏 Dedicated Dimensions")
        d_len = f"{record['LENGTH']} {record['LENGTH_UOM']}".strip()
        d_wid = f"{record['WIDTH']} {record['WIDTH_UOM']}".strip()
        d_hgt = f"{record['HEIGHT']} {record['HEIGHT_UOM']}".strip()
        
        st.write(f"**LENGTH:** `{d_len if d_len else 'N/A'}`")
        st.write(f"**WIDTH:** `{d_wid if d_wid else 'N/A'}`")
        st.write(f"**HEIGHT / DEPTH:** `{d_hgt if d_hgt else 'N/A'}`")

    st.write("")
    
    # 3. Commerce Descriptions
    st.markdown("### 📝 Commerce Description Suite")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="desc-label">INVOICE_DESC (≤ 40 CAPS)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-val">{record["INVOICE_DESC"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="desc-label">MOBILE_DESC (60-80 chars)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-val">{record["MOBILE_DESC"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="desc-label">SHORT_DESC (≤ 150 chars)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-val">{record["SHORT_DESC"]}</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="desc-label">LONG_DESC1 (≤ 500 chars)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-val">{record["LONG_DESC1"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="desc-label">RETAIL_DESC</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-val">{record["RETAIL_DESC"]}</div>', unsafe_allow_html=True)
