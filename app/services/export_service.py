from __future__ import annotations

import csv
import io
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DataPoint

MAX_EXPORT_ROWS = 5000


def export_csv(
    db: Session,
    experiment_id: int,
    channels: list[str] | None,
    start: datetime | None,
    end: datetime | None,
    quality: str | None,
) -> str:
    """Генерирует CSV-выгрузку DataPoints эксперимента с поддержкой фильтров."""
    stmt = (
        select(DataPoint)
        .where(DataPoint.experiment_id == experiment_id)
        .order_by(DataPoint.timestamp, DataPoint.channel)
        .limit(MAX_EXPORT_ROWS)
    )

    if channels:
        stmt = stmt.where(DataPoint.channel.in_(channels))
    if start:
        stmt = stmt.where(DataPoint.timestamp >= start)
    if end:
        stmt = stmt.where(DataPoint.timestamp <= end)
    if quality:
        stmt = stmt.where(DataPoint.quality == quality.upper())

    data_points = db.scalars(stmt).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "channel", "value", "unit", "quality", "tag"])
    for dp in data_points:
        writer.writerow([
            dp.timestamp.isoformat(),
            dp.channel,
            dp.value,
            dp.unit or "",
            dp.quality or "",
            dp.tag or "",
        ])
    return output.getvalue()
