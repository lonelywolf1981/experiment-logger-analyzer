from __future__ import annotations

from fastapi import FastAPI

from app.db import engine
from app.models import Base
from app.routers import analytics, experiments, export, import_data, web

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Experiment Logger & Analyzer",
    description="Импорт и анализ экспериментальных данных: каналы, графики, сводка, экспорт.",
    version="0.1.0",
)

app.include_router(experiments.router)
app.include_router(import_data.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(web.router)
