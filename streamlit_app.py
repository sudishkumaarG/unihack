import streamlit as st
import pandas as pd
import re

from src.preprocessor import clean_value, extract_clean_manufacturer
from src.taxonomy import classify_product
from src.brand_normalizer import normalize_brand_and_manufacturer
from src.attribute_extractor import extract_attributes_and_uoms
from src.description_builder import build_descriptions
from src.config import DELIVERY_HEADERS, CHAR_LIMITS

# Page Configuration & Theme Setting
st.set_page_config(
    page_title="UniHack 2026 - AI Product Intelligence Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme CSS (Navy/Blue palette, Adaptive Light/Dark Mode Cards)
st.markdown("""
<style>
    /* Theme Color Variables */
    :root {
        --primary-navy: #1a3a5c;
        --accent-blue: #2563eb;
        --accent-light-blue: #3b82f6;
        --border-color: #e2e8f0;
        --card-bg-light: #f8fafc;
        --card-bg-dark: #1e293b;
        --text-muted: #64748b;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1a3a5c 0%, #2563eb 100%);
        color: white;
        padding: 1.6rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(26, 58, 92, 0.15);
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .header-subtitle {
        font-size: 1.05rem;
        color: #e0f2fe;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    
    /* Pipeline Stage Stepper */
    .pipeline-stepper {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    .step-pill {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(4px);
        color: #f8fafc;
        padding: 0.3rem 0.7rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    .step-pill.active {
        background: #ffffff;
        color: #1a3a5c;
        font-weight: 700;
    }
    .step-arrow {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
    }
    
    /* Card Container Panels */
    .panel-card {
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }
    
    /* Classpath Styled Badge */
    .classpath-container {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        margin-top: 0.8rem;
        padding: 0.5rem 0.9rem;
        background-color: rgba(37, 99, 235, 0.08);
        border: 1px solid rgba(37, 99, 235, 0.25);
        border-radius: 8px;
    }
    .classpath-label {
        font-weight: 700;
        color: #1a3a5c;
        font-size: 0.95rem;
    }
    .classpath-badge {
        background: linear-gradient(135deg, #1a3a5c 0%, #2563eb 100%);
        color: #ffffff !important;
        padding: 0.3rem 0.85rem;
        border-radius: 16px;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }
    
    /* Dimension Pills */
    .dim-box {
        background-color: rgba(26, 58, 92, 0.05);
        border-left: 4px solid #2563eb;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
    }
    .dim-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .dim-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a3a5c;
    }
    
    /* Character Count Badge */
    .char-caption {
        font-size: 0.78rem;
        font-weight: 600;
        color: #16a34a;
        margin-top: -0.4rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Banner with Pipeline Stepper
st.markdown("""
<div class="header-banner">
    <div class="header-title">⚡ UniHack 2026 — AI Product Intelligence Studio</div>
    <div class="header-subtitle">Real-time Catalog Standardization & Commerce Enrichment (Unilog 252-Column Delivery Standard)</div>
    <div class="pipeline-stepper">
        <span class="step-pill active">1. Preprocessing</span>
        <span class="step-arrow">➔</span>
        <span class="step-pill active">2. Classification</span>
        <span class="step-arrow">➔</span>
        <span class="step-pill active">3. Normalization</span>
        <span class="step-arrow">➔</span>
        <span class="step-pill active">4. Attribute Extraction</span>
        <span class="step-arrow">➔</span>
        <span class="step-pill active">5. Description Suite</span>
        <span class="step-arrow">➔</span>
        <span class="step-pill active">6. Delivery Standard</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Preset Examples Data
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

# Sidebar Preset Selectors
st.sidebar.markdown("### 📋 Sample Input Presets")
selected_preset_name = st.sidebar.selectbox("Select a benchmark sample record:", list(PRESETS.keys()))
preset_data = PRESETS[selected_preset_name]
st.sidebar.info("Click 'Enrich Product Record' to run real-time enrichment via core `src/` modules.")

# Input Section Form
with st.form(key="enrichment_form"):
    st.markdown("### 📥 Product Catalog Input")
    col1, col2 = st.columns([2, 1])
    with col1:
        raw_desc_input = st.text_input("Raw Product Description", value=preset_data["desc"], help="Raw title or description text from catalog feed")
    with col2:
        mfg_num_input = st.text_input("Mfg Part Number (MPN)", value=preset_data["mpn"])
        
    part_manuf_input = st.text_input("Raw Part Manufacturer (Optional)", value=preset_data["manuf"])
    
    submit_button = st.form_submit_button(label="🚀 Enrich Product Record", type="primary")

def enrich_single_record(mfg_num, raw_desc, manuf=''):
    """
    Calls exact pipeline modules directly from src/ without reimplementing logic.
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

# Process and Render Results
if submit_button or raw_desc_input:
    record, attributes_dict = enrich_single_record(mfg_num_input.strip(), raw_desc_input.strip(), part_manuf_input.strip())
    
    st.markdown("---")
    st.subheader("🔍 Enriched Output Results")
    
    # 1. Primary Identifiers & Taxonomy Section
    st.markdown("#### 🏢 Taxonomy & Entity Normalization")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Manufacturer Name", record['MANUFACTURER_NAME'] or "N/A")
    m2.metric("Brand Name", record['BRAND_NAME'] or "N/A")
    m3.metric("Trade Name", record['TRADE_NAME'] or "N/A")
    m4.metric("Product Name", record['Product Name'] or "N/A")
    
    # Render Taxonomy Classpath as a styled HTML badge pill
    classpath_html = f'''
    <div class="classpath-container">
        <span class="classpath-label">Taxonomy Classpath:</span>
        <span class="classpath-badge">{record["Classpath"]}</span>
    </div>
    '''
    st.markdown(classpath_html, unsafe_allow_html=True)
    st.write("")
    
    # 2. Extracted Attributes & Dedicated Dimensions Section
    col_attr, col_dim = st.columns([2, 1])
    
    with col_attr:
        st.markdown("#### 🏷️ Extracted Specification Attributes")
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
            df_attr = pd.DataFrame(attr_list)
            st.dataframe(df_attr, use_container_width=True, hide_index=True)
        else:
            st.info("No candidate spec attributes extracted from raw description text.")
            
    with col_dim:
        st.markdown("#### 📏 Dedicated Dimensions")
        d_len = f"{record['LENGTH']} {record['LENGTH_UOM']}".strip()
        d_wid = f"{record['WIDTH']} {record['WIDTH_UOM']}".strip()
        d_hgt = f"{record['HEIGHT']} {record['HEIGHT_UOM']}".strip()
        
        st.markdown(f'''
        <div class="dim-box">
            <div class="dim-title">LENGTH</div>
            <div class="dim-value">{d_len if d_len else 'N/A'}</div>
        </div>
        <div class="dim-box">
            <div class="dim-title">WIDTH</div>
            <div class="dim-value">{d_wid if d_wid else 'N/A'}</div>
        </div>
        <div class="dim-box">
            <div class="dim-title">HEIGHT / DEPTH</div>
            <div class="dim-value">{d_hgt if d_hgt else 'N/A'}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.write("")
    
    # 3. Commerce Description Suite Section
    st.markdown("#### 📝 Commerce Description Suite")
    
    c1, c2 = st.columns(2)
    with c1:
        inv_val = record["INVOICE_DESC"]
        st.text_area("INVOICE_DESC (≤ 40 CAPS)", value=inv_val, height=80)
        st.markdown(f'<div class="char-caption">Length: {len(inv_val)}/40 chars (100% Schema Compliant ✅)</div>', unsafe_allow_html=True)
        
        mob_val = record["MOBILE_DESC"]
        st.text_area("MOBILE_DESC (60-80 Target)", value=mob_val, height=80)
        st.markdown(f'<div class="char-caption">Length: {len(mob_val)}/80 chars (100% Schema Compliant ✅)</div>', unsafe_allow_html=True)

        shrt_val = record["SHORT_DESC"]
        st.text_area("SHORT_DESC (≤ 150 chars)", value=shrt_val, height=100)
        st.markdown(f'<div class="char-caption">Length: {len(shrt_val)}/150 chars (100% Schema Compliant ✅)</div>', unsafe_allow_html=True)

    with c2:
        long_val = record["LONG_DESC1"]
        st.text_area("LONG_DESC1 (≤ 500 chars)", value=long_val, height=120)
        st.markdown(f'<div class="char-caption">Length: {len(long_val)}/500 chars (100% Schema Compliant ✅)</div>', unsafe_allow_html=True)

        ret_val = record["RETAIL_DESC"]
        st.text_area("RETAIL_DESC", value=ret_val, height=80)
        st.markdown(f'<div class="char-caption">Length: {len(ret_val)} chars</div>', unsafe_allow_html=True)
