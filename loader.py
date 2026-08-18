import psycopg2
import db
from logger import logger

# basic loader - just inserts records
# NOTE: will break if we try to load a barcode that already exists
# need to fix that for reruns - but at least it works for a first run

INSERT_SQL = """
    INSERT INTO foods (barcode, product_name, calories, protein, carbs, fat, fibre, sodium, category)
    VALUES (%(barcode)s, %(product_name)s, %(calories)s, %(protein)s, %(carbs)s,
            %(fat)s, %(fibre)s, %(sodium)s, %(category)s)
"""


def load_records(records):
    """
    loads a list of clean records into the foods table
    returns the number of records successfully inserted
    """
    if not records:
        return 0

    conn = db.get_connection()
    loaded = 0

    try:
        with conn.cursor() as cur:
            for record in records:
                cur.execute(INSERT_SQL, record)
                loaded += 1
        conn.commit()
        logger.info(f"inserted {loaded} records")
    except Exception as e:
        conn.rollback()
        logger.error(f"insert failed: {e}")
        raise
    finally:
        conn.close()

    return loaded
