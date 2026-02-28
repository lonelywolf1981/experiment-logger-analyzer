from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.db import engine
from app.models import Base
from app.routers import analytics, experiments, export, import_data, web

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Experiment Logger & Analyzer",
    description="Импорт и анализ экспериментальных данных: каналы, графики, сводка, экспорт.",
    version="0.1.0",
)

_app_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(_app_dir / "static")), name="static")

app.include_router(experiments.router)
app.include_router(import_data.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(web.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/experiments")
