from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services import experiment_service, import_service

router = APIRouter(tags=["import"])


@router.post("/experiments/{experiment_id}/import")
async def import_data(
    experiment_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    experiment_service.get_experiment_or_404(db, experiment_id)
    return await import_service.import_file(file, experiment_id, db)
