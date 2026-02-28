from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services import experiment_service, export_service

router = APIRouter(tags=["export"])


@router.get("/experiments/{experiment_id}/export.csv")
def export_csv(
    experiment_id: int,
    channels: list[str] = Query(default=[]),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    quality: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    experiment_service.get_experiment_or_404(db, experiment_id)
    csv_content = export_service.export_csv(
        db,
        experiment_id=experiment_id,
        channels=channels or None,
        start=start,
        end=end,
        quality=quality,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}.csv"},
    )
