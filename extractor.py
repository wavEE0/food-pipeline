import requests
import config
from logger import logger

FIELDS = 'code,product_name,nutriments,categories_tags'

def fetch_products():
    """
    fetches products from open food facts api
    yields one page of results at a time so we dont load everything into memory

    stops when we get fewer results than the page size (means we hit the end)
    """
    page = 1

    while True:
        params = {
            'fields': FIELDS,
            'page_size': config.BATCH_SIZE,
            'page': page,
            'json': 1,
        }

        logger.info(f"fetching page {page}")
        response = requests.get(config.API_BASE_URL, params=params, timeout=30)

        if response.status_code != 200:
            logger.error(f"api returned status {response.status_code} on page {page}, stopping")
            break

        products = response.json().get('products', [])
        logger.info(f"page {page}: got {len(products)} products")

        if not products:
            logger.info("empty page, done fetching")
            break

        yield products

        # if we got fewer than a full page, this was the last one
        if len(products) < config.BATCH_SIZE:
            logger.info("partial page, reached end of results")
            break

        page += 1
