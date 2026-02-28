from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services import analytics_service, experiment_service

router = APIRouter(tags=["analytics"])


@router.get("/experiments/{experiment_id}/channels")
def get_channels(experiment_id: int, db: Session = Depends(get_db)):
    experiment_service.get_experiment_or_404(db, experiment_id)
    return analytics_service.get_channels(db, experiment_id)


@router.get("/experiments/{experiment_id}/series")
def get_series(
    experiment_id: int,
    channels: list[str] = Query(default=[]),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    experiment_service.get_experiment_or_404(db, experiment_id)
    return analytics_service.get_series(db, experiment_id, channels, start, end)


@router.get("/experiments/{experiment_id}/summary")
def get_summary(experiment_id: int, db: Session = Depends(get_db)):
    experiment_service.get_experiment_or_404(db, experiment_id)
    return analytics_service.get_summary(db, experiment_id)
