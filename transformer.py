from logger import logger, error_logger

MAX_CALORIES = 1000


def _get_numeric(value):
    """safely converts a value to float, returns None if it cant"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _clean_category(raw_tags):
    """
    open food facts categories look like: ['en:beverages', 'en:soft-drinks']
    we want: 'beverages' (first tag, strip prefix, readable)
    """
    if not raw_tags:
        return None

    first = raw_tags[0] if isinstance(raw_tags, list) else raw_tags

    # strip language prefix (en:, fr:, etc.)
    if ':' in first:
        first = first.split(':', 1)[1]

    # dashes to spaces, lowercase
    return first.replace('-', ' ').lower()


def _transform_one(product, seen_barcodes):
    """
    transforms and validates a single product
    seen_barcodes is a set we use to catch duplicates within the same batch
    returns None if rejected
    """
    barcode = product.get('code', '').strip()
    name = product.get('product_name', '').strip()

    if not barcode:
        error_logger.warning(f"rejected: missing barcode - name={name!r}")
        return None

    if not name:
        error_logger.warning(f"rejected: missing product_name - barcode={barcode!r}")
        return None

    # skip duplicates within this batch - loader handles cross-run dedup
    if barcode in seen_barcodes:
        error_logger.warning(f"rejected: duplicate barcode in batch - barcode={barcode}")
        return None

    seen_barcodes.add(barcode)

    nutriments = product.get('nutriments', {})
    calories = _get_numeric(nutriments.get('energy-kcal_100g'))

    if calories is not None and (calories < 0 or calories > MAX_CALORIES):
        error_logger.warning(f"rejected: calories {calories} out of range - barcode={barcode}")
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
        'category': _clean_category(product.get('categories_tags')),
    }


def transform_batch(raw_products):
    """
    transforms, validates, and deduplicates a batch of raw products
    returns (clean_records, rejected_count)
    """
    seen_barcodes = set()
    results = []
    rejected = 0

    for product in raw_products:
        result = _transform_one(product, seen_barcodes)
        if result:
            results.append(result)
        else:
            rejected += 1

    logger.debug(f"transform: {len(results)} ok, {rejected} rejected")
    return results, rejected
