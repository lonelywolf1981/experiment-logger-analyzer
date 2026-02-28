# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run server
uvicorn app.main:app --reload

# Run all tests
python -m pytest -v

# Run a single test file
python -m pytest tests/test_import.py -v

# Run a single test
python -m pytest tests/test_import.py::test_import_csv_success -v

# Lint
python -m ruff check app
```

Use `python -m pytest` and `python -m ruff` (not bare commands) to avoid PATH issues on CI.

## Architecture

```
app/
  main.py            # FastAPI app + router registration + table creation
  db.py              # SQLAlchemy engine + SessionLocal (DATABASE_URL from env)
  models.py          # ORM models: Experiment, ImportRun, DataPoint
  dependencies.py    # get_db() dependency injection
  schemas.py         # Pydantic schemas for request/response (Experiment CRUD)
  routers/
    experiments.py   # CRUD /experiments (GET, POST, DELETE)
    import_data.py   # POST /experiments/{id}/import
    analytics.py     # GET /experiments/{id}/channels|series|summary
    export.py        # GET /experiments/{id}/export.csv
  services/
    experiment_service.py   # DB CRUD for Experiment
    import_service.py       # CSV/JSONL parsing, validation, DataPoint insertion
    analytics_service.py    # channels stats, series, summary (aggregate queries)
    export_service.py       # CSV export with filters
tests/
  conftest.py         # db_session, client, sample_csv, sample_jsonl, experiment_id fixtures
```

## Key Contracts

**DataPoint validation rules:**
- `timestamp`, `channel`, `value` required → empty values: `skipped`
- Invalid (non-parseable) `timestamp` → `errors`; invalid `value` → `errors`
- `quality` if present must be `OK|WARN|BAD` (case-insensitive) → else `skipped`
- `unit`, `tag` are always optional

**Import formats:**
- `.csv` — strict header: `timestamp,channel,value,unit,quality,tag`
- `.jsonl` — 1 JSON object per line; empty lines ignored; invalid JSON line → `errors`
- Max upload: `MAX_UPLOAD_BYTES = 10 MB`
- Filename is sanitized with `Path(filename).name` (path traversal protection)

**SQLAlchemy style:** Use SQLAlchemy 2.0 (`select`, `scalars`, `execute`, `Mapped[...]`).
Use `db.flush()` to get auto-generated IDs without committing; single `db.commit()` at end of import for atomicity.

**Cascade delete:** Deleting an Experiment cascades to DataPoints and ImportRuns via ORM `cascade="all, delete-orphan"`.

**Tests:** Use in-memory SQLite (`StaticPool`), override `get_db` dependency. All tests use shared fixtures from `conftest.py`.
