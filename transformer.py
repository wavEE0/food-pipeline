from logger import logger, error_logger

# max sensible calorie value per 100g - anything over this is probably an error
# pure fat is ~900 kcal/100g so 1000 gives a small buffer for weird edge cases
MAX_CALORIES = 1000


def _get_numeric(value):
    """
    safely converts a value to float
    returns None if it cant be converted (better than crashing on bad data)
    """
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _transform_one(product):
    """
    transforms a single raw product - now with proper validation
    returns None if the product fails validation
    """
    barcode = product.get('code', '').strip()
    name = product.get('product_name', '').strip()

    # cant store it without a barcode - its our unique key
    if not barcode:
        error_logger.warning(f"rejected: missing barcode - name={name!r}")
        return None

    # no name is also a dealbreaker
    if not name:
        error_logger.warning(f"rejected: missing product_name - barcode={barcode!r}")
        return None

    nutriments = product.get('nutriments', {})

    calories = _get_numeric(nutriments.get('energy-kcal_100g'))

    # calories way out of range probably means bad data in the api
    if calories is not None and (calories < 0 or calories > MAX_CALORIES):
        error_logger.warning(f"rejected: calories {calories} out of range - barcode={barcode}, name={name!r}")
        return None

    return {
        'barcode': barcode,
        'product_name': name,
        'calories': calories,
        'protein': _get_numeric(nutriments.get('proteins_100g')),
        'carbs': _get_numeric(nutriments.get('carbohydrates_100g')),
        'fat': _get_numeric(nutriments.get('fat_100g')),
        'fibre': _get_numeric(nutriments.get('fiber_100g')),
        'sodium': _get_numeric(nutriments.get('sodium_100g')),
        'category': None,
    }


def transform_batch(raw_products):
    """
    transforms and validates a batch of raw products
    returns (clean_records, rejected_count)
    """
    results = []
    rejected = 0

    for product in raw_products:
        result = _transform_one(product)
        if result:
            results.append(result)
        else:
            rejected += 1

    logger.debug(f"transform: {len(results)} ok, {rejected} rejected")
    return results, rejected
