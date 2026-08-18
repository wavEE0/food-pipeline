import requests
import time
import config
from logger import logger

FIELDS = 'code,product_name,nutriments,categories_tags'

# dont want to hammer the api too hard - max pages to fetch per run
MAX_PAGES = 50


def _fetch_page_with_retry(page):
    """
    fetches a single page with retry logic
    exponential backoff on rate limit (429) or server errors (5xx)
    returns the response json or None if all retries fail
    """
    params = {
        'fields': FIELDS,
        'page_size': config.BATCH_SIZE,
        'page': page,
        'json': 1,
    }

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            logger.debug(f"page {page} attempt {attempt}")
            response = requests.get(config.API_BASE_URL, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()

            # rate limited - wait longer each time
            if response.status_code == 429:
                wait = 2 ** attempt
                logger.warning(f"rate limited on page {page}, waiting {wait}s before retry")
                time.sleep(wait)
                continue

            # server error - also worth retrying
            if response.status_code >= 500:
                wait = 2 ** attempt
                logger.warning(f"server error {response.status_code} on page {page}, waiting {wait}s")
                time.sleep(wait)
                continue

            # other errors (4xx) arent going to go away with retries
            logger.error(f"unrecoverable error {response.status_code} on page {page}")
            return None

        except requests.exceptions.Timeout:
            wait = 2 ** attempt
            logger.warning(f"timeout on page {page} attempt {attempt}, waiting {wait}s")
            time.sleep(wait)
        except requests.exceptions.RequestException as e:
            logger.error(f"request failed on page {page}: {e}")
            return None

    logger.error(f"all {config.MAX_RETRIES} retries failed for page {page}")
    return None


def fetch_products():
    """
    main generator - fetches all products page by page
    yields lists of raw product dicts
    """
    page = 1

    while page <= MAX_PAGES:
        data = _fetch_page_with_retry(page)

        if data is None:
            logger.error(f"giving up on page {page}")
            break

        products = data.get('products', [])
        logger.info(f"page {page}: fetched {len(products)} products")

        if not products:
            break

        yield products

        if len(products) < config.BATCH_SIZE:
            logger.info("reached last page")
            break

        page += 1

    if page > MAX_PAGES:
        logger.warning(f"hit max page limit ({MAX_PAGES}), stopping early")
