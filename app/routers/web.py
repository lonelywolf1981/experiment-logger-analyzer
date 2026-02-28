from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services import analytics_service, experiment_service, import_service
from app.services.experiment_service import create_experiment

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/ui", tags=["ui"])


@router.get("/experiments", response_class=HTMLResponse)
def experiments_list(request: Request, db: Session = Depends(get_db)):
    experiments = experiment_service.list_experiments(db)
    return templates.TemplateResponse(
        "experiments.html",
        {"request": request, "experiments": experiments},
    )


@router.post("/experiments", response_class=HTMLResponse)
def create_experiment_htmx(
    request: Request,
    name: str = Form(...),
    stand: str = Form(default=""),
    operator: str = Form(default=""),
    notes: str = Form(default=""),
    db: Session = Depends(get_db),
):
    if not name.strip():
        return HTMLResponse('<tr><td colspan="5" class="text-danger p-2">Название не может быть пустым</td></tr>', status_code=422)

    experiment = create_experiment(
        db,
        name=name,
        stand=stand or None,
        operator=operator or None,
        notes=notes or None,
    )
    return templates.TemplateResponse(
        "partials/experiment_row.html",
        {"request": request, "experiment": experiment},
    )


@router.delete("/experiments/{experiment_id}", response_class=HTMLResponse)
def delete_experiment_htmx(experiment_id: int, db: Session = Depends(get_db)):
    experiment_service.delete_experiment(db, experiment_id)
    return HTMLResponse("")


@router.get("/experiments/{experiment_id}", response_class=HTMLResponse)
def experiment_detail(request: Request, experiment_id: int, db: Session = Depends(get_db)):
    experiment = experiment_service.get_experiment(db, experiment_id)
    if experiment is None:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )

    channels = analytics_service.get_channels(db, experiment_id)
    summary = analytics_service.get_summary(db, experiment_id)
    import_history = import_service.list_import_runs_for_experiment(db, experiment_id)

    return templates.TemplateResponse(
        "experiment.html",
        {
            "request": request,
            "experiment": experiment,
            "channels": channels,
            "summary": summary,
            "import_history": import_history,
        },
    )


@router.post("/experiments/{experiment_id}/import", response_class=HTMLResponse)
async def import_data_htmx(
    request: Request,
    experiment_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    experiment = experiment_service.get_experiment(db, experiment_id)
    if experiment is None:
        return HTMLResponse('<div class="alert alert-danger">Эксперимент не найден</div>')

    result = None
    error = None
    try:
        result = await import_service.import_file(file, experiment_id, db)
    except HTTPException as exc:
        error = exc.detail

    channels = analytics_service.get_channels(db, experiment_id)
    summary = analytics_service.get_summary(db, experiment_id)
    import_history = import_service.list_import_runs_for_experiment(db, experiment_id)

    return templates.TemplateResponse(
        "partials/import_response.html",
        {
            "request": request,
            "result": result,
            "error": error,
            "channels": channels,
            "summary": summary,
            "import_history": import_history,
        },
    )


# Redirect root UI to experiments list
@router.get("", response_class=RedirectResponse)
@router.get("/", response_class=RedirectResponse)
def ui_root():
    return RedirectResponse(url="/ui/experiments")
