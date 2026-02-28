from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas import ExperimentCreate, ExperimentRead
from app.services import experiment_service

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentRead, status_code=201)
def create_experiment(body: ExperimentCreate, db: Session = Depends(get_db)):
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Experiment name must not be blank")
    return experiment_service.create_experiment(
        db,
        name=body.name,
        stand=body.stand,
        operator=body.operator,
        notes=body.notes,
    )


@router.get("", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)):
    return experiment_service.list_experiments(db)


@router.get("/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    return experiment_service.get_experiment_or_404(db, experiment_id)


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    deleted = experiment_service.delete_experiment(db, experiment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
