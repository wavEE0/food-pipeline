"""
main entry point - orchestrates the full ETL run
extract -> transform -> load -> notify
"""
import sys
import requests
import config
from extractor import fetch_products
from transformer import transform_batch
from loader import load_records, start_run, end_run
from logger import logger


def notify_slack(message):
    """
    sends a message to slack via webhook
    silently skips if no webhook url is configured
    """
    if not config.SLACK_WEBHOOK_URL:
        return

    try:
        resp = requests.post(config.SLACK_WEBHOOK_URL, json={'text': message}, timeout=10)
        if resp.status_code != 200:
            logger.warning(f"slack notification failed: {resp.status_code}")
    except Exception as e:
        # notifications are best-effort, dont let this crash the pipeline
        logger.warning(f"could not send slack notification: {e}")


def run():
    """runs the full ETL pipeline"""
    logger.info("=== food-pipeline starting ===")

    run_id = start_run()
    total_fetched = 0
    total_loaded = 0
    total_rejected = 0

    try:
        for page_products in fetch_products():
            total_fetched += len(page_products)

            clean_records, rejected_count = transform_batch(page_products)
            total_rejected += rejected_count

            if clean_records:
                total_loaded += load_records(clean_records)

        end_run(run_id, total_fetched, total_loaded, total_rejected, 'success')
        msg = f"food-pipeline run complete ✓ | fetched={total_fetched} loaded={total_loaded} rejected={total_rejected}"
        logger.info(msg)
        notify_slack(msg)

    except Exception as e:
        logger.error(f"pipeline failed: {e}", exc_info=True)
        end_run(run_id, total_fetched, total_loaded, total_rejected, 'failed', str(e))
        notify_slack(f"food-pipeline FAILED ✗ | error: {e}")
        sys.exit(1)

    logger.info("=== food-pipeline done ===")


if __name__ == '__main__':
    run()
