import psycopg2
import db
from logger import logger

# upgraded to upsert - now safe to rerun without duplicate key errors
# ON CONFLICT updates the record if the barcode already exists

UPSERT_SQL = """
    INSERT INTO foods (barcode, product_name, calories, protein, carbs, fat, fibre, sodium, category)
    VALUES (%(barcode)s, %(product_name)s, %(calories)s, %(protein)s, %(carbs)s,
            %(fat)s, %(fibre)s, %(sodium)s, %(category)s)
    ON CONFLICT (barcode) DO UPDATE SET
        product_name = EXCLUDED.product_name,
        calories     = EXCLUDED.calories,
        protein      = EXCLUDED.protein,
        carbs        = EXCLUDED.carbs,
        fat          = EXCLUDED.fat,
        fibre        = EXCLUDED.fibre,
        sodium       = EXCLUDED.sodium,
        category     = EXCLUDED.category,
        updated_at   = NOW()
"""


def load_records(records):
    """
    upserts a list of clean records into the foods table
    insert new, update existing - safe to run multiple times
    returns number of records processed
    """
    if not records:
        return 0

    conn = db.get_connection()
    loaded = 0

    try:
        with conn.cursor() as cur:
            for record in records:
                cur.execute(UPSERT_SQL, record)
                loaded += 1
        conn.commit()
        logger.info(f"upserted {loaded} records")
    except Exception as e:
        conn.rollback()
        logger.error(f"upsert failed: {e}")
        raise
    finally:
        conn.close()

    return loaded
