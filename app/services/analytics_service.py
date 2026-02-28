from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DataPoint


def get_channels(db: Session, experiment_id: int) -> list[dict]:
    """Возвращает список каналов с базовой статистикой по эксперименту."""
    stmt = (
        select(
            DataPoint.channel,
            func.count().label("count"),
            func.min(DataPoint.value).label("min"),
            func.max(DataPoint.value).label("max"),
            func.avg(DataPoint.value).label("avg"),
            func.min(DataPoint.timestamp).label("first_ts"),
            func.max(DataPoint.timestamp).label("last_ts"),
        )
        .where(DataPoint.experiment_id == experiment_id)
        .group_by(DataPoint.channel)
        .order_by(DataPoint.channel)
    )
    rows = db.execute(stmt).all()

    return [
        {
            "channel": row.channel,
            "count": row.count,
            "min": row.min,
            "max": row.max,
            "avg": round(row.avg, 6) if row.avg is not None else None,
            "first_ts": row.first_ts.isoformat() if row.first_ts else None,
            "last_ts": row.last_ts.isoformat() if row.last_ts else None,
        }
        for row in rows
    ]


def get_series(
    db: Session,
    experiment_id: int,
    channels: list[str],
    start: datetime | None,
    end: datetime | None,
) -> dict[str, list[dict]]:
    """Возвращает временные ряды по выбранным каналам для построения графиков."""
    if not channels:
        return {}

    stmt = (
        select(DataPoint.channel, DataPoint.timestamp, DataPoint.value)
        .where(DataPoint.experiment_id == experiment_id)
        .where(DataPoint.channel.in_(channels))
        .order_by(DataPoint.channel, DataPoint.timestamp)
    )
    if start:
        stmt = stmt.where(DataPoint.timestamp >= start)
    if end:
        stmt = stmt.where(DataPoint.timestamp <= end)

    rows = db.execute(stmt).all()

    result: dict[str, list[dict]] = {ch: [] for ch in channels}
    for row in rows:
        result[row.channel].append({"timestamp": row.timestamp.isoformat(), "value": row.value})
    return result


def get_summary(db: Session, experiment_id: int) -> dict:
    """Сводка по эксперименту: длительность, количество точек, каналы, качество."""
    stmt = select(
        func.count().label("total_points"),
        func.count(DataPoint.channel.distinct()).label("channels_count"),
        func.min(DataPoint.timestamp).label("first_ts"),
        func.max(DataPoint.timestamp).label("last_ts"),
    ).where(DataPoint.experiment_id == experiment_id)
    row = db.execute(stmt).one()

    duration_seconds = None
    if row.first_ts and row.last_ts:
        duration_seconds = (row.last_ts - row.first_ts).total_seconds()

    q_stmt = (
        select(DataPoint.quality, func.count().label("count"))
        .where(DataPoint.experiment_id == experiment_id)
        .where(DataPoint.quality.is_not(None))
        .group_by(DataPoint.quality)
        .order_by(DataPoint.quality)
    )
    q_rows = db.execute(q_stmt).all()
    points_by_quality = {r.quality: r.count for r in q_rows}

    return {
        "total_points": row.total_points,
        "channels_count": row.channels_count,
        "duration_seconds": duration_seconds,
        "first_ts": row.first_ts.isoformat() if row.first_ts else None,
        "last_ts": row.last_ts.isoformat() if row.last_ts else None,
        "points_by_quality": points_by_quality,
    }
