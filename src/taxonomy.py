import re
from src.preprocessor import clean_value

# Taxonomy classification rules
TAXONOMY_RULES = [
    # Dishwashers & Laundry Appliances
    {
        'pattern': r'dishwasher',
        'dept': 'Appliances',
        'class': 'Large Appliances',
        'fine': 'Dishwashers',
        'classpath': 'Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers',
        'product_name': 'Dishwasher'
    },
    {
        'pattern': r'dryer|washer|laundry center',
        'dept': 'Appliances',
        'class': 'Large Appliances',
        'fine': 'Laundry Appliances',
        'classpath': 'Appliances & Consumer Electronics>Laundry Appliances>Washers & Dryers',
        'product_name': 'Laundry Appliance'
    },
    # Faucets
    {
        'pattern': r'faucet|sink mixer|lavatory',
        'dept': 'Plumbing & Heating',
        'class': 'Plumbing Fixtures',
        'fine': 'Faucets',
        'classpath': 'Plumbing & Heating>Plumbing Fixtures>Faucets',
        'product_name': 'Faucet'
    },
    # Sanding Belts
    {
        'pattern': r'sanding belt|belt',
        'dept': 'Tools & Hardware',
        'class': 'Abrasives & Cutting Tools',
        'fine': 'Sanding Belts',
        'classpath': 'Tools & Hardware>Abrasives>Sanding Belts',
        'product_name': 'Sanding Belt'
    },
    # Abrasive Sheets & Strips
    {
        'pattern': r'abranet|sanding sheet|sanding strip|sanding sponge',
        'dept': 'Tools & Hardware',
        'class': 'Abrasives & Cutting Tools',
        'fine': 'Abrasive Sheets',
        'classpath': 'Tools & Hardware>Abrasives>Sanding Sheets',
        'product_name': 'Abrasive Sheet'
    },
    # Cut-off Discs & Grinding Wheels
    {
        'pattern': r'cut-off|cut off|cutoff|cut-off wheel|dko|grinding wheel|flap disc|wire wheel',
        'dept': 'Tools & Hardware',
        'class': 'Abrasives & Cutting Tools',
        'fine': 'Cut-Off Discs',
        'classpath': 'Tools & Hardware>Abrasives>Cut-Off Wheels',
        'product_name': 'Cut-Off Disc'
    },
    # Sanding Discs & Film Discs
    {
        'pattern': r'stikit|hiolit|film disc|sanding disc|disc',
        'dept': 'Tools & Hardware',
        'class': 'Abrasives & Cutting Tools',
        'fine': 'Abrasive Discs',
        'classpath': 'Tools & Hardware>Abrasives>Sanding Discs',
        'product_name': 'Abrasive Disc'
    },
    # Saw Blades & Accessories
    {
        'pattern': r'blade|saw|drill|bit|countersink|router bit',
        'dept': 'Tools & Hardware',
        'class': 'Power Tool Accessories',
        'fine': 'Blades & Bits',
        'classpath': 'Tools & Hardware>Power Tool Accessories>Blades & Bits',
        'product_name': 'Saw Blade'
    },
    # Power Tool Accessories / Socket Adapters & Sockets
    {
        'pattern': r'socket adapter|socket|drive bit',
        'dept': 'Tools & Hardware',
        'class': 'Power Tool Accessories',
        'fine': 'Adapters & Sockets',
        'classpath': 'Tools & Hardware>Power Tool Accessories>Sockets & Adapters',
        'product_name': 'Socket Adapter'
    },
    # Fittings (Word-boundary anchored to prevent 'steel' matching 'tee')
    {
        'pattern': r'\b(fitting|fittings|elbow|elbows|tee|tees|coupling|couplings|adapter|adapters|bushing|bushings|nipple|nipples)\b',
        'dept': 'Plumbing & Heating',
        'class': 'Pipe & Tube Fittings',
        'fine': 'Fittings',
        'classpath': 'Plumbing & Heating>Pipe Fittings>Fittings',
        'product_name': 'Pipe Fitting'
    },
    # Lighting & Bulbs
    {
        'pattern': r'\b(led strip light|wall light|bath light|downlight|lamp|bulb|recessed fixture|lighting)\b',
        'dept': 'Electrical & Lighting',
        'class': 'Lighting Fixtures & Lamps',
        'fine': 'Lamps & Bulbs',
        'classpath': 'Electrical & Lighting>Lighting>Lamps & Fixtures',
        'product_name': 'Lighting Fixture'
    },
    # Wiring Devices & Outlets
    {
        'pattern': r'outlet|receptacle|switch|plug|dimmer|decor plate',
        'dept': 'Electrical & Lighting',
        'class': 'Wiring Devices',
        'fine': 'Outlets & Switches',
        'classpath': 'Electrical & Lighting>Wiring Devices>Receptacles & Switches',
        'product_name': 'Electrical Receptacle'
    },
    # Tapes & Adhesives
    {
        'pattern': r'tape|emseal',
        'dept': 'Tools & Hardware',
        'class': 'Adhesives & Tapes',
        'fine': 'Industrial Tapes',
        'classpath': 'Tools & Hardware>Adhesives & Tapes>Industrial Tapes',
        'product_name': 'Industrial Tape'
    },
    # Decking & Building Materials
    {
        'pattern': r'deck|trex|timbertech|board|plank|lumber|azek|patio dr|gate sq',
        'dept': 'Building Materials',
        'class': 'Decking & Lumber',
        'fine': 'Composite Decking',
        'classpath': 'Building Materials>Decking>Composite Deck Boards',
        'product_name': 'Composite Deck Board'
    },
    # Mortar & Masonry Building Materials
    {
        'pattern': r'mortar|concrete|cement',
        'dept': 'Building Materials',
        'class': 'Masonry Supplies',
        'fine': 'Mortar & Mixes',
        'classpath': 'Building Materials>Masonry Supplies>Mortar',
        'product_name': 'Masonry Supply'
    },
    # PPE / Safety
    {
        'pattern': r'glove|eyewear|glasses|protective|kneeling pad',
        'dept': 'Safety & Security',
        'class': 'Personal Protective Equipment',
        'fine': 'PPE',
        'classpath': 'Safety & Security>PPE>Eye & Hand Protection',
        'product_name': 'Safety Equipment'
    }
]

def classify_product(part_desc, mfg_part_num=""):
    """
    Returns taxonomy tuple: (Dept, Class, Fine, Classpath, Product Name)
    """
    desc = clean_value(part_desc) + " " + clean_value(mfg_part_num)
    
    for rule in TAXONOMY_RULES:
        if re.search(rule['pattern'], desc, re.IGNORECASE):
            return (
                rule['dept'],
                rule['class'],
                rule['fine'],
                rule['classpath'],
                rule['product_name']
            )

    # General industrial hardware fallback
    return (
        'Tools & Hardware',
        'Industrial Supplies',
        'General Hardware',
        'Tools & Hardware>Industrial Supplies>General Hardware',
        'Industrial Supply'
    )
