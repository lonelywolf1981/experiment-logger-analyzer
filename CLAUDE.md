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
    import_data.py   # POST /experiments/{id}/import, GET /experiments/{id}/imports
    analytics.py     # GET /experiments/{id}/channels|series|summary
    export.py        # GET /experiments/{id}/export.csv
    web.py           # UI HTML pages: GET/POST /ui/experiments, GET/POST /ui/experiments/{id}
  services/
    experiment_service.py   # DB CRUD for Experiment
    import_service.py       # CSV/JSONL parsing, validation, DataPoint insertion + list_import_runs_for_experiment
    analytics_service.py    # channels stats, series, summary (aggregate queries)
    export_service.py       # CSV export with filters
  templates/
    base.html               # Bootstrap 5.3 + HTMX + dark/light theme toggle
    experiments.html        # experiment list + HTMX create form
    experiment.html         # detail page: summary cards, channels+chart, import form
    partials/               # HTMX targets: experiment_row, channels_table, summary_cards,
                            #               import_history, import_response (with OOB swaps)
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

**Web UI (v0.2):**
- Bootstrap 5.3 dark/light theme via `data-bs-theme` on `<html>`, saved in `localStorage`
- HTMX patterns: create experiment → prepend `<tr>` to table; delete → `hx-swap="outerHTML"` empty response; import → HTMX OOB swaps update `#channels-table-wrapper`, `#summary-section`, `#import-history` simultaneously
- Chart.js: `GET /experiments/{id}/series?channels=A&channels=B` → `{channel: [{timestamp,value}]}` → Chart.js `type: 'time'` datasets
- Import errors caught in web router (`except HTTPException`), returned as HTTP 200 with error alert so HTMX always processes the response

**Tests:** Use in-memory SQLite (`StaticPool`), override `get_db` dependency. All tests use shared fixtures from `conftest.py`.
