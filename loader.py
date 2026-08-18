import psycopg2
from datetime import datetime
import db
from logger import logger

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

START_RUN_SQL = """
    INSERT INTO pipeline_runs (started_at, status)
    VALUES (%s, 'running')
    RETURNING id
"""

END_RUN_SQL = """
    UPDATE pipeline_runs
    SET completed_at     = %s,
        records_fetched  = %s,
        records_loaded   = %s,
        records_rejected = %s,
        status           = %s,
        error_message    = %s
    WHERE id = %s
"""


def start_run():
    """
    creates a new pipeline_runs row and returns the run id
    call this at the very start of a pipeline run
    """
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(START_RUN_SQL, (datetime.utcnow(),))
            run_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"started run id={run_id}")
        return run_id
    finally:
        conn.close()


def end_run(run_id, fetched, loaded, rejected, status, error=None):
    """
    updates the pipeline_runs row when the run finishes
    status should be 'success' or 'failed'
    """
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(END_RUN_SQL, (
                datetime.utcnow(), fetched, loaded, rejected, status, error, run_id
            ))
        conn.commit()
        logger.info(f"run id={run_id} finished: status={status} fetched={fetched} loaded={loaded} rejected={rejected}")
    finally:
        conn.close()


def load_records(records):
    """
    upserts a list of clean records into the foods table
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
