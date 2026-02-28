from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExperimentCreate(BaseModel):
    name: str
    stand: str | None = None
    operator: str | None = None
    notes: str | None = None


class ExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    stand: str | None
    operator: str | None
    notes: str | None
    created_at: datetime
