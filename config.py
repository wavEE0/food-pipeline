import os
from dotenv import load_dotenv

# load .env file if it exists - won't override real env vars
load_dotenv()

# database stuff
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ.get('DB_NAME', 'food_pipeline')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

# api settings
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://world.openfoodfacts.org/api/v2/search')
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 100))
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))

# slack webhook - optional, skip notifications if not set
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')
