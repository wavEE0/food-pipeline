# food-pipeline

An ETL pipeline that fetches nutritional data from the [Open Food Facts API](https://world.openfoodfacts.org/),
validates and transforms it, and loads it into a PostgreSQL database. Runs daily via GitHub Actions.

Built as a portfolio project to demonstrate ETL design patterns — incremental pagination, retry logic,
data validation, upsert handling, and run tracking.

---

## What It Does

1. **Extract** — fetches product data from the Open Food Facts API in paginated batches.
   Retries automatically on rate limits (429) and server errors (5xx) with exponential backoff.

2. **Transform** — validates and cleans each record: rejects missing barcodes/names, filters
   out-of-range calorie values, converts non-numeric nutriments to NULL, deduplicates within
   each batch, and normalises category strings.

3. **Load** — upserts clean records into PostgreSQL using `ON CONFLICT DO UPDATE`, so reruns
   update stale data rather than failing on duplicates. Each run is tracked in a `pipeline_runs`
   table with counts and status.

4. **Notify** — sends a Slack webhook message on completion (or failure), if configured.

---

## Project Structure

```
food-pipeline/
├── pipeline.py          # main entry point - runs the full ETL
├── extractor.py         # fetches data from open food facts api
├── transformer.py       # validates and cleans raw records
├── loader.py            # upserts into postgres, tracks run metadata
├── db.py                # database connection helper
├── config.py            # reads env vars / .env file
├── logger.py            # two loggers: pipeline.log + errors.log
├── schema.sql           # run once to create tables
├── requirements.txt
├── .env.example         # copy to .env and fill in your values
├── logs/                # created at runtime
│   ├── pipeline.log     # all events
│   └── errors.log       # rejected records only
├── tests/
│   ├── test_transformer.py
│   ├── test_extractor.py
│   └── test_loader.py
└── .github/
    └── workflows/
        └── pipeline.yml  # runs daily at 06:00 UTC
```

---

## Setup

**Requirements:** Python 3.9+, PostgreSQL 14+

```bash
# clone and install dependencies
git clone https://github.com/wavEE0/food-pipeline.git
cd food-pipeline
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# configure environment
cp .env.example .env
# edit .env with your database credentials

# create tables
psql -U postgres -d food_pipeline -f schema.sql

# run the pipeline
python pipeline.py
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Database Schema

### `foods`

| Column | Type | Notes |
|---|---|---|
| id | SERIAL | primary key |
| barcode | VARCHAR(50) | unique, used for upsert |
| product_name | VARCHAR(500) | |
| calories | NUMERIC(8,2) | per 100g |
| protein | NUMERIC(8,2) | per 100g |
| carbs | NUMERIC(8,2) | per 100g |
| fat | NUMERIC(8,2) | per 100g |
| fibre | NUMERIC(8,2) | per 100g |
| sodium | NUMERIC(8,2) | per 100g |
| category | VARCHAR(200) | normalised from API tags |
| loaded_at | TIMESTAMP | first inserted |
| updated_at | TIMESTAMP | last updated |

### `pipeline_runs`

| Column | Type | Notes |
|---|---|---|
| id | SERIAL | primary key |
| started_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |
| records_fetched | INTEGER | raw count from API |
| records_loaded | INTEGER | successfully upserted |
| records_rejected | INTEGER | failed validation |
| status | VARCHAR(20) | `running` / `success` / `failed` |
| error_message | TEXT | set on failure |

---

## Scheduling

The pipeline runs automatically every day at **06:00 UTC** via GitHub Actions
(`.github/workflows/pipeline.yml`). It can also be triggered manually from the
Actions tab in the GitHub UI.

Add a `SLACK_WEBHOOK_URL` secret in your repository settings to enable
Slack notifications on completion and failure.

---

## Example Log Output

```
10:42:01 [INFO] started run id=1
10:42:01 [INFO] fetching page 1
10:42:03 [INFO] page 1: fetched 100 products
10:42:03 [INFO] upserted 94 records
10:42:04 [INFO] page 2: fetched 100 products
10:42:04 [INFO] upserted 97 records
...
10:43:15 [INFO] run id=1 finished: status=success fetched=500 loaded=472 rejected=28
10:43:15 [INFO] food-pipeline run complete ✓ | fetched=500 loaded=472 rejected=28
```
