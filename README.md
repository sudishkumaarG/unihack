# UniHack 2026 Submission: AI-Powered Product Intelligence

**Challenge Track:** Unilog Challenge — AI-Powered Product Intelligence for Industrial Commerce  
**Target Schema:** Unilog Fixed 252-Column Commerce-Ready Delivery Format (`Unihack__Expected_Output_-_Delivery_Format.csv`)

---

## Executive Summary & Challenge Context

This submission transforms sparse, messy industrial product records into standardized, commerce-ready records matching Unilog's 252-column Delivery Format schema.

### Event Resource Scope & Methodological Disclosure
As confirmed via the official UniHack hackathon Resources page, external reference files—such as separate LOV datasets (`Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`), the 27k+ manufacturer master list (`UniCat_Manufacturer_and_Brand_List.xlsx`), content guidelines docx, and 200-item ground truth sheets—were **not separately downloadable for this event**.

Our only provided datasets were:
1. `Unihack__Sample_Dataset_-_Input.csv` (1,000 sparse input records)
2. `Unihack__Expected_Output_-_Delivery_Format.csv` (252-column target schema, containing 2 worked dishwasher template examples)

### Key Architectural & Evaluation Decisions
1. **Honest Metric Framing — Format Calibration (83.59%)**:
   The 83.59% similarity metric is presented strictly as a **Format Calibration Score** (validated against the 2 worked template dishwasher examples in the delivery schema), proving our pipeline correctly constructs all 252 delivery columns, description formats, feature bullet structures, and attribute triplet formats. It is **not** claimed as dataset-wide accuracy across unlabelled rows.
2. **Category Focus Deep-Dive (30-Row Verified Slice for Abrasives & Cut-Off Discs)**:
   To demonstrate deep product intelligence capability, we selected a prominent recurring category (**Abrasives & Cut-Off Discs** — Diablo, 3M Cubitron, Mirka, Milwaukee). We generated a 30-row deeply verified batch with **visible step-by-step extraction reasoning per field**, documented in [Deep_Verified_Abrasives_Batch.md](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/Deep_Verified_Abrasives_Batch.md).
3. **Attribute Extraction Audit & Honest Coverage Framing (74.7%)**:
   Attribute extraction was expanded from the initial abrasives slice across all recurring structured categories in the input dataset. **747 out of 1,000 rows (74.7%)** now have $\ge 1$ candidate attribute triplet extracted (total 1,609 attributes; avg 1.61 attributes/row). The remaining 253 rows (25.3%) represent ultra-sparse catalog codes or unlabelled commodity parts with no raw spec text; in strict compliance with hackathon anti-hallucination rules, these slots remain unpopulated.
4. **Deliberate Human-Review Flagging (10.3%)**:
   The hackathon rules strictly penalize ungrounded/invented data. For ultra-sparse 1-word input titles or unbranded commodity items, our pipeline deterministically flags records as `"needs human review"` (103 records, 10.3%) rather than making unsupported guesses.
5. **Intentionally Blank Schema Fields — Zero-Ungrounded-Data Compliance**:
   Specific delivery columns (`UPC`/`EAN`/`GTIN`, pricing/packaging agreements, `SDS`/`Manual`/`Drawing` links, `Discontinued`, `Country Of Origin`) are **intentionally blank — data source not available in the provided event materials**. Guessing values for these fields would violate UniHack zero-ungrounded-data rules.

---

## Submission Performance Summary

| Metric | Target / Benchmark | Pipeline Score | Status |
| :--- | :--- | :--- | :--- |
| **Delivery Schema Headers** | Fixed 252 Columns | **252 / 252 Columns** | ✅ Exact Match |
| **Format Calibration Score** | 2 Worked Template Examples | **83.59%** | ✅ FORMAT CALIBRATED |
| **Attribute Extraction Coverage** | Dataset-Wide $\ge 1$ Attr | **74.70%** (747/1000 Rows) | ✅ AUDITED |
| **Abrasives Deep-Verification Slice** | 30-Row Category Slice | **100.0% Verified** | ✅ DEEP VERIFIED |
| **Curated UOM & Space Compliance** | Standard UOM & Space Rule | **95.30%** | ✅ COMPLIANT |
| **Character-Limit Compliance Rate** | 100% Guideline Limits | **100.0%** | ✅ PASS |
| **Processed Input Records** | Full Input Dataset | **1,000 Records** | ✅ COMPLETE |
| **Flagged Low-Confidence Records** | Needs Human Review | **103 Records** (10.3%) | ⚠️ AUDITED |

---

## Stage-by-Stage Scope & Attribute Extraction Audit

| Pipeline Stage | Target Scope | Actual Dataset Coverage | Stage Description |
| :--- | :--- | :--- | :--- |
| **Stage 1: Taxonomy Classification** | All 1,000 Rows | **100.0% (1,000/1,000)** | Full classification into `Dept`, `Class`, `Fine`, `Classpath`, and `Product Name`. |
| **Stage 2: Brand & Mfr Normalization** | All 1,000 Rows | **100.0% (1,000/1,000)** | Normalizes legal entity suffixes while preserving trade/brand names; 103 commodity rows flagged for human review. |
| **Stage 3: Description Building** | All 1,000 Rows | **100.0% (1,000/1,000)** | Populates `MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`, and `With`. |
| **Stage 4: Attribute & UOM Extraction** | Structured Categories | **74.70% (747/1,000)** | Extracts structured candidate triplets (Label, Value, UOM). 253 rows remain legitimately blank to avoid hallucinating ungrounded data. |

### Per-Category Attribute Extraction Breakdown

| Product Category | Total Rows | Rows with $\ge 1$ Attr | % Coverage | Avg Attrs / Row | Key Extracted Attributes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cut-Off Discs** | 39 | 39 | **100.0%** | 4.00 | Grit, Diameter, Thickness, Arbor Size, Material Application |
| **Abrasive Discs** | 12 | 12 | **100.0%** | 3.17 | Grit, Diameter, Arbor Size, Series, Material Application |
| **Abrasive Sheets** | 6 | 6 | **100.0%** | 3.00 | Grit, Dimensions, Series, Package Quantity |
| **Pipe Fittings** | 8 | 8 | **100.0%** | 2.50 | Connection Size, Material, Fitting Type |
| **Industrial Tapes** | 4 | 4 | **100.0%** | 2.25 | Tape Width, Roll Length, Material |
| **Composite Deck Boards** | 170 | 167 | **98.2%** | 3.35 | Thickness, Width, Length, Color, Material, Edge Profile |
| **Laundry Appliances** | 22 | 21 | **95.5%** | 1.55 | Fuel Type (Gas/Electric), Finish/Color (White/Black), App Type |
| **Electrical Receptacles** | 17 | 14 | **82.4%** | 1.24 | Voltage, Amperage, Color (Light Almond/White), Device Type |
| **Saw Blades & Bits** | 91 | 75 | **82.4%** | 1.01 | Blade/Bit Diameter, Tool Accessory Type, Material |
| **Dishwashers** | 10 | 8 | **80.0%** | 3.50 | Wash Cycles, Voltage, Sound Level, Material, Finish |
| **Masonry Supplies** | 9 | 7 | **77.8%** | 0.89 | Mortar Type (Type N), Color, Mix Type |
| **Industrial Supplies** | 564 | 361 | **64.0%** | 1.02 | Grinding Dimensions, Arbor, Grit, Voltage, Amps |
| **Safety Equipment / PPE** | 25 | 15 | **60.0%** | 0.76 | Apparel Size, Color/Lens, Product Type |
| **Sanding Belts** | 2 | 1 | **50.0%** | 1.50 | Grit, Belt Width, Belt Length |
| **Lighting Fixtures** | 21 | 9 | **42.9%** | 0.57 | Fixture Length, Light Source, Finish |

---

## Intentionally Blank Schema Fields (Scope & Zero-Ungrounded-Data Compliance)

Adhering strictly to the hackathon policy prohibiting invented or ungrounded data generation, the following column groups in the 252-column schema are **intentionally blank — data source not available in the provided event materials**:

1. **Barcodes & Universal Identifiers** (`UPC`, `EAN`, `GTIN`): Require external barcode master databases or GTIN registries not included in event materials.
2. **Commercial Pricing & Packaging Agreements** (`Price`, `Case Pack Pricing`, `MOQ`): Require commercial vendor pricing schedules.
3. **Hosted Manufacturer Media & Documentation** (`SDS`, `Manual`, `Engineering Drawing`, `Video Links`): Require hosted URL asset repositories.
4. **Lifecycle & Regulatory Sourcing Status** (`Discontinued`, `Country Of Origin`): Require active catalog lifecycle feeds and customs regulatory filings.

Dedicated dimension columns (`LENGTH`/`LENGTH_UOM`, `WIDTH`/`WIDTH_UOM`, `HEIGHT`/`HEIGHT_UOM`) are populated automatically wherever candidate attributes (`Length`, `Width`, `Height`, `Depth`, `Thickness`) are extracted and grounded in `Part_Desc`.

---

## Deliverable File Manifest

- **[Unihack_Submission_Output.csv](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/Unihack_Submission_Output.csv)**: Complete 1,000-row delivery dataset matching all 252 expected headers.
- **[Deep_Verified_Abrasives_Batch.csv](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/Deep_Verified_Abrasives_Batch.csv)**: 30-row deep-dive verified slice for Abrasives & Cut-Off Discs.
- **[Deep_Verified_Abrasives_Batch.md](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/Deep_Verified_Abrasives_Batch.md)**: Field-by-field extraction trace and derivation reasoning for every record in the 30-row deep slice.
- **[Evaluation_Report.md](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/Evaluation_Report.md)**: Comprehensive evaluation report with transparency disclosures and audit log.
- **[streamlit_app.py](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/streamlit_app.py)**: Interactive single-page Streamlit web app wrapping core `src/` modules for live product enrichment demos.
- **[requirements.txt](file:///c:/Users/sudis/OneDrive/Desktop/Unihack/requirements.txt)**: Python package dependencies (`streamlit`, `pandas`, `openpyxl`).
- **`src/` Pipeline Modules**:
  - `config.py`: Target headers, curated UOM standard map, character limit rules, and placeholder sets.
  - `preprocessor.py`: String cleaning, placeholder stripping (`-- Unbranded --`, etc.), parenthetical vendor code removal, and algorithmic fraction/decimal conversion (`convert_decimal_to_fraction`).
  - `brand_normalizer.py`: Best-effort manufacturer and brand normalizer stripping legal suffixes (`Inc`, `LLC`, `Corp`) while preserving trademark symbols (`®`, `™`).
  - `taxonomy.py`: Taxonomy classifier mapping products to `Classpath`, `Dept`, `Class`, `Fine`, and `Product Name`.
  - `attribute_extractor.py`: Candidate attribute & UOM triplet parser enforcing standard UOM abbreviations and space separators (e.g. `24 in`, `120 V`, `47 dBA`, `80 Grit`).
  - `description_builder.py`: Description generator enforcing hard character limits (`INVOICE_DESC` ≤ 40 CAPS, `MOBILE_DESC` 60–80 chars, `SHORT_DESC` ≤ 150, `LONG_DESC1` ≤ 500).
  - `deep_verified_batch.py`: Generator for the 30-row Abrasives deep verification slice and reasoning trace.
  - `pipeline.py`: End-to-end execution pipeline runner.
  - `evaluate.py`: Metrics evaluation engine.

---

## How to Execute the Pipeline & Web App Demo

To run the pipeline and generate all submission outputs from scratch:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run full 1,000-row pipeline execution
python -m src.pipeline

# 3. Generate the 30-row deeply verified Abrasives slice with field reasoning
python -m src.deep_verified_batch

# 4. Run evaluation scoring and update Evaluation_Report.md
python -c "from src.pipeline import run_pipeline; from src.evaluate import evaluate_pipeline_output; rows, flags = run_pipeline(); evaluate_pipeline_output(flagged_rows=flags)"

# 5. Launch the live Streamlit Web App demo
streamlit run streamlit_app.py
```

---

## Automation Summary

**What Was Automated, What Wasn't, and Why:**
We automated the end-to-end classification, brand/manufacturer normalization, attribute & UOM extraction, description generation, and 252-column schema assembly using a modular python pipeline. Preprocessing automatically stripped placeholder values (`-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`), manufacturer normalization stripped legal entity suffixes while preserving trademark symbols (`®`, `™`), and UOM formatting enforced standard abbreviations with single space separators (e.g. `24 in`). Description building enforced strict character limits (`INVOICE_DESC` ≤ 40 CAPS, `MOBILE_DESC` 60–80 chars, `SHORT_DESC` ≤ 150). What was *not* fully automated was guessing missing domain attributes for ultra-sparse product codes. Adhering strictly to the hackathon rule against ungrounded data creation, 103 low-confidence or commodity records (10.3%) were deterministically flagged as `"needs human review"` for expert audit.
