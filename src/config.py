import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV_PATH = os.path.join(BASE_DIR, "Unihack_ Sample Dataset - Input.csv")
DELIVERY_FORMAT_CSV_PATH = os.path.join(BASE_DIR, "Unihack_ Expected Output - Delivery Format.csv")
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, "Unihack_Submission_Output.csv")
EVALUATION_REPORT_PATH = os.path.join(BASE_DIR, "Evaluation_Report.md")

def load_delivery_headers():
    if os.path.exists(DELIVERY_FORMAT_CSV_PATH):
        with open(DELIVERY_FORMAT_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return next(reader)
    raise FileNotFoundError(f"Delivery format header CSV not found at {DELIVERY_FORMAT_CSV_PATH}")

DELIVERY_HEADERS = load_delivery_headers()

PLACEHOLDERS = {
    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
    "-",
    "n/a",
    "none",
    "null",
    "unknown",
    ""
}

# Curated UOM standard mapping table derived from input data types
CURATED_UOM_MAP = {
    "IN": "in",
    "INCH": "in",
    "INCHES": "in",
    '"': "in",
    "FT": "ft",
    "FEET": "ft",
    "'": "ft",
    "MM": "mm",
    "MILLIMETER": "mm",
    "MILLIMETERS": "mm",
    "CM": "cm",
    "CENTIMETER": "cm",
    "M": "m",
    "METER": "m",
    "V": "V",
    "VOLT": "V",
    "VOLTS": "V",
    "A": "A",
    "AMP": "A",
    "AMPS": "A",
    "AMPERE": "A",
    "W": "W",
    "WATT": "W",
    "WATTS": "W",
    "HZ": "Hz",
    "HERTZ": "Hz",
    "DBA": "dBA",
    "DB": "dBA",
    "DECIBEL": "dBA",
    "RPM": "rpm",
    "GPM": "gpm",
    "LBS": "lb",
    "LB": "lb",
    "POUND": "lb",
    "POUNDS": "lb",
    "OZ": "oz",
    "OUNCE": "oz",
    "KW-HR": "kW-hr",
    "KWH": "kW-hr",
    "DEGREE": "deg",
    "DEG": "deg",
    "GRIT": "Grit",
    "P": "Grit",
    "PC": "pc",
    "PIECE": "pc",
    "PIECES": "pc"
}

# Character Limits as specified in content guidelines
CHAR_LIMITS = {
    'INVOICE_DESC': 40,
    'MOBILE_DESC': 80,
    'SHORT_DESC': 150,
    'LONG_DESC1': 500,
    'RETAIL_DESC': 250,
    'Product Name': 100
}
for i in range(1, 21):
    CHAR_LIMITS[f'ITEM_FEATURES_{i}'] = 120
