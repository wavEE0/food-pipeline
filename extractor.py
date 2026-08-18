import requests
import config
from logger import logger

# the fields we actually want from the api - no point downloading everything
FIELDS = 'code,product_name,nutriments,categories_tags'

def fetch_products():
    """
    fetches products from open food facts api
    yields lists of raw product dicts (one list per page)

    NOTE: this is a basic version, only gets the first page
    will add pagination later
    """
    params = {
        'fields': FIELDS,
        'page_size': config.BATCH_SIZE,
        'page': 1,
        'json': 1,
    }

    logger.info(f"fetching page 1 from open food facts")
    response = requests.get(config.API_BASE_URL, params=params, timeout=30)

    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        logger.info(f"got {len(products)} products")
        yield products
    else:
        logger.error(f"api returned status {response.status_code}")
