# The Cake Shop official product catalog
# Single source of truth for flavors, sizes, and pricing rules

CAKE_CATALOG = {
    "Chocolate Truffle Cake": {
        "1kg": 500,
        "2kg": 900,
        "3kg": 1300
    },
    "Black Forest Cake": {
        "1kg": 550,
        "2kg": 1000,
        "3kg": 1450
    },
    "Red Velvet Cake": {
        "1kg": 650,
        "2kg": 1200,
        "3kg": 1700
    },
    "Vanilla Cream Cake": {
        "1kg": 450,
        "2kg": 850,
        "3kg": 1200
    },
    "Butterscotch Cake": {
        "1kg": 550,
        "2kg": 1000,
        "3kg": 1450
    },
    "Pineapple Cake": {
        "1kg": 500,
        "2kg": 900,
        "3kg": 1300
    },
    "Fruit Cake": {
        "1kg": 700,
        "2kg": 1350,
        "3kg": 1900
    }
}

def get_cake_catalog():
    """Returns the full list of products and pricing."""
    return CAKE_CATALOG

def get_cake_price(flavor: str, size: str) -> float:
    """
    Returns the exact price for a given flavor and size.
    Performs case-insensitive matching.
    """
    # Normalize flavor name
    matched_flavor = None
    for name in CAKE_CATALOG.keys():
        if flavor.lower() in name.lower() or name.lower() in flavor.lower():
            matched_flavor = name
            break
            
    if not matched_flavor:
        return 0.0
        
    size_key = size.strip().lower()
    # Normalize size key, e.g. "2 kg" -> "2kg"
    size_key = size_key.replace(" ", "")
    if not size_key.endswith("kg"):
        size_key += "kg"
        
    sizes = CAKE_CATALOG[matched_flavor]
    return sizes.get(size_key, sizes.get("1kg", 0.0))
