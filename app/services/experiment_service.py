from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Experiment


def create_experiment(
    db: Session,
    name: str,
    stand: str | None,
    operator: str | None,
    notes: str | None,
) -> Experiment:
    experiment = Experiment(
        name=name.strip(),
        stand=stand.strip() if stand else None,
        operator=operator.strip() if operator else None,
        notes=notes.strip() if notes else None,
        created_at=datetime.now().astimezone(),
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def list_experiments(db: Session) -> list[Experiment]:
    stmt = select(Experiment).order_by(Experiment.created_at.desc(), Experiment.id.desc())
    return list(db.scalars(stmt).all())


def get_experiment(db: Session, experiment_id: int) -> Experiment | None:
    return db.get(Experiment, experiment_id)


def get_experiment_or_404(db: Session, experiment_id: int) -> Experiment:
    experiment = db.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
    return experiment


def delete_experiment(db: Session, experiment_id: int) -> bool:
    experiment = db.get(Experiment, experiment_id)
    if experiment is None:
        return False
    db.delete(experiment)
    db.commit()
    return True
