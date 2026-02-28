from __future__ import annotations

import csv
import io
import json
import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.models import DataPoint, ImportRun

logger = logging.getLogger(__name__)

CSV_HEADER = ["timestamp", "channel", "value", "unit", "quality", "tag"]
ALLOWED_QUALITY = {"OK", "WARN", "BAD"}

# 10 MB — достаточно для CSV/JSONL с десятками тысяч строк
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def _parse_ts(raw: str) -> datetime:
    """Парсит ISO 8601 timestamp; поднимает ValueError при ошибке."""
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"Cannot parse timestamp: {raw!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Парсеры форматов файлов
# ---------------------------------------------------------------------------

def _parse_csv(text: str) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    actual_header = list(reader.fieldnames or [])
    if actual_header != CSV_HEADER:
        raise HTTPException(
            status_code=400,
            detail="CSV header must be exactly: " + ",".join(CSV_HEADER),
        )
    return reader


def _parse_jsonl(text: str) -> list[dict[str, Any]]:
    """Парсит JSONL: 1 JSON-объект на строку, пустые строки игнорируются.
    Возвращает список словарей; строки с ошибкой разбора помечены флагом _parse_error.
    """
    rows: list[dict[str, Any]] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            rows.append({"_parse_error": True, "_line": line_num})
            continue
        if not isinstance(obj, dict):
            rows.append({"_parse_error": True, "_line": line_num})
            continue
        rows.append(obj)
    return rows


# ---------------------------------------------------------------------------
# Общая обработка строк
# ---------------------------------------------------------------------------

def _process_datapoint_rows(
    rows: Iterable[Any],
    safe_filename: str,
    experiment_id: int,
    run_id: int,
    db: Session,
) -> tuple[int, int, int]:
    inserted = skipped = errors = 0

    for line_num, row in enumerate(rows, start=2):
        try:
            if not isinstance(row, dict):
                logger.warning("Import %s, row %d: expected dict, got %s", safe_filename, line_num, type(row).__name__)
                errors += 1
                continue

            # Parse error marker from JSONL parser
            if row.get("_parse_error"):
                logger.warning("Import %s, line %s: invalid JSON", safe_filename, row.get("_line", line_num))
                errors += 1
                continue

            # Required fields: timestamp, channel, value
            raw_ts = str(row.get("timestamp") or "").strip()
            channel = str(row.get("channel") or "").strip()
            raw_value = row.get("value")

            if not raw_ts or not channel:
                skipped += 1
                continue

            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                skipped += 1
                continue

            timestamp = _parse_ts(raw_ts)

            # Parse value
            if isinstance(raw_value, (int, float)):
                value = float(raw_value)
            else:
                value = float(str(raw_value).strip())

            # Optional fields
            raw_unit = row.get("unit")
            unit = str(raw_unit).strip() or None if raw_unit not in (None, "") else None

            raw_quality = row.get("quality")
            if raw_quality not in (None, ""):
                quality_upper = str(raw_quality).strip().upper()
                if quality_upper not in ALLOWED_QUALITY:
                    skipped += 1
                    continue
                quality = quality_upper
            else:
                quality = None

            raw_tag = row.get("tag")
            tag = str(raw_tag).strip() or None if raw_tag not in (None, "") else None

            db.add(
                DataPoint(
                    experiment_id=experiment_id,
                    import_run_id=run_id,
                    timestamp=timestamp,
                    channel=channel,
                    value=value,
                    unit=unit,
                    quality=quality,
                    tag=tag,
                )
            )
            inserted += 1

        except ValueError as exc:
            logger.warning("Import %s, row %d: parse error: %s", safe_filename, line_num, exc)
            errors += 1

    return inserted, skipped, errors


# ---------------------------------------------------------------------------
# Публичный интерфейс
# ---------------------------------------------------------------------------

async def import_file(file: UploadFile, experiment_id: int, db: Session) -> dict[str, object]:
    """Принимает .csv или .jsonl, валидирует и записывает DataPoints в БД."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    safe_filename = Path(file.filename).name
    lower = safe_filename.lower()

    if not (lower.endswith(".csv") or lower.endswith(".jsonl")):
        raise HTTPException(status_code=400, detail="Only .csv and .jsonl files are supported")

    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )

    text = content.decode("utf-8", errors="replace")

    rows: Iterable[Any] = _parse_csv(text) if lower.endswith(".csv") else _parse_jsonl(text)

    run = ImportRun(
        experiment_id=experiment_id,
        started_at=datetime.now().astimezone(),
        filename=safe_filename,
        inserted=0,
        skipped=0,
        errors=0,
    )
    db.add(run)
    db.flush()

    inserted, skipped, errors = _process_datapoint_rows(rows, safe_filename, experiment_id, run.id, db)

    run.inserted = inserted
    run.skipped = skipped
    run.errors = errors

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Database error during import of '%s'", safe_filename)
        raise HTTPException(status_code=500, detail="Database error during import")

    logger.info(
        "Import '%s' into experiment %d: inserted=%d skipped=%d errors=%d",
        safe_filename, experiment_id, inserted, skipped, errors,
    )

    return {
        "import_run_id": run.id,
        "filename": run.filename,
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
    }


def list_import_runs_for_experiment(
    db: Session,
    experiment_id: int,
    *,
    limit: int = 20,
) -> list[dict[str, object]]:
    """Возвращает историю импортов для конкретного эксперимента (новые первыми)."""
    stmt = (
        select(ImportRun)
        .where(ImportRun.experiment_id == experiment_id)
        .order_by(ImportRun.started_at.desc())
        .limit(limit)
    )
    rows = db.scalars(stmt).all()
    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "filename": run.filename,
            "inserted": run.inserted,
            "skipped": run.skipped,
            "errors": run.errors,
        }
        for run in rows
    ]
