from logger import logger

# basic transformer - pulls out the fields we want from the raw api response
# no validation yet, just getting it working first

def _transform_one(product):
    """
    transforms a single raw product dict into something we can store
    returns None if the product is unusable (missing barcode or name)
    """
    barcode = product.get('code', '').strip()
    name = product.get('product_name', '').strip()

    # cant do much without these two
    if not barcode or not name:
        return None

    nutriments = product.get('nutriments', {})

    # open food facts stores per-100g values with _100g suffix
    return {
        'barcode': barcode,
        'product_name': name,
        'calories': nutriments.get('energy-kcal_100g'),
        'protein': nutriments.get('proteins_100g'),
        'carbs': nutriments.get('carbohydrates_100g'),
        'fat': nutriments.get('fat_100g'),
        'fibre': nutriments.get('fiber_100g'),
        'sodium': nutriments.get('sodium_100g'),
        'category': None,  # handle categories later
    }


def transform_batch(raw_products):
    """
    transforms a list of raw products
    returns (clean_records, rejected_count)
    """
    results = []
    for product in raw_products:
        result = _transform_one(product)
        if result:
            results.append(result)

    # no rejection tracking yet, will add that in the next version
    return results, 0
