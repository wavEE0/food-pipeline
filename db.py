import psycopg2
import config
from logger import logger

# just a thin wrapper around psycopg2 - nothing fancy
# returns a connection, caller is responsible for closing it

def get_connection():
    """
    opens a connection to postgres using the config values
    raises an exception if it cant connect - better to fail loud than silently
    """
    logger.debug(f"connecting to {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        logger.debug("db connection ok")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"could not connect to database: {e}")
        raise
