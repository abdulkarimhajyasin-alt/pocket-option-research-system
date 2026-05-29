"""FastAPI routes for the local research dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.dashboard.service import DashboardService, load_dashboard_config


SAFETY_NOTE = (
    "This is a local research dashboard. It does not execute live trades, connect to "
    "real-money accounts, or automate broker actions."
)


def create_dashboard_app(project_root: Path | str = ".") -> FastAPI:
    """Create the local dashboard FastAPI application."""
    root = Path(project_root).resolve()
    service = DashboardService(root)
    templates = Jinja2Templates(directory=str(root / "app" / "templates"))
    app = FastAPI(
        title="Pocket Option Research Dashboard",
        description="Local-only research dashboard. No live trading.",
        version="0.1.0",
    )
    static_dir = root / "app" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def context(request: Request, **values: object) -> dict[str, object]:
        return {
            "request": request,
            "safety_note": SAFETY_NOTE,
            "config": service.config,
            **values,
        }

    @app.get("/", response_class=HTMLResponse)
    def overview(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/overview.html",
            context(request, page="overview", overview=service.overview()),
        )

    @app.get("/strategies", response_class=HTMLResponse)
    def strategies(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/strategies.html",
            context(request, page="strategies", strategies=service.strategy_summaries()),
        )

    @app.get("/datasets", response_class=HTMLResponse)
    def datasets(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/datasets.html",
            context(request, page="datasets", datasets=service.dataset_summaries()),
        )

    @app.get("/datasets/{dataset_id}", response_class=HTMLResponse)
    def dataset_detail(request: Request, dataset_id: str) -> HTMLResponse:
        dataset = next(
            (item for item in service.dataset_summaries() if item.dataset_id == dataset_id),
            None,
        )
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return templates.TemplateResponse(
            request,
            "dashboard/dataset_detail.html",
            context(request, page="datasets", dataset=dataset),
        )

    @app.get("/validation", response_class=HTMLResponse)
    def validation(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/validation.html",
            context(request, page="validation", validations=service.validation_summaries()),
        )

    @app.get("/validation/{report_id}", response_class=HTMLResponse)
    def validation_detail(request: Request, report_id: str) -> HTMLResponse:
        validation_item = next(
            (item for item in service.validation_summaries() if item.report_id == report_id),
            None,
        )
        if validation_item is None:
            raise HTTPException(status_code=404, detail="Validation report not found")
        return templates.TemplateResponse(
            request,
            "dashboard/validation_detail.html",
            context(request, page="validation", validation=validation_item),
        )

    @app.get("/reports", response_class=HTMLResponse)
    def reports(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/reports.html",
            context(request, page="reports", reports=service.report_loader.list_reports()),
        )

    @app.get("/reports/{report_id}", response_class=HTMLResponse)
    def report_detail(request: Request, report_id: str) -> HTMLResponse:
        report = service.report_loader.get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return templates.TemplateResponse(
            request,
            "dashboard/report_detail.html",
            context(request, page="reports", report=report),
        )

    @app.get("/actions", response_class=HTMLResponse)
    def actions(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard/actions.html",
            context(
                request,
                page="actions",
                actions=service.actions.list_actions(),
                result=None,
            ),
        )

    @app.post("/actions/run/{action_name}", response_class=HTMLResponse)
    def run_action(request: Request, action_name: str) -> HTMLResponse:
        if not service.config.allow_actions:
            raise HTTPException(status_code=403, detail="Dashboard actions are disabled")
        try:
            result = service.actions.run(action_name)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return templates.TemplateResponse(
            request,
            "dashboard/actions.html",
            context(
                request,
                page="actions",
                actions=service.actions.list_actions(),
                result=result,
            ),
        )

    @app.get("/health")
    def health() -> dict[str, object]:
        config = load_dashboard_config(root)
        return {
            "status": "ok",
            "local_only": True,
            "actions_enabled": config.allow_actions,
            "reports": len(service.report_loader.list_reports()),
        }

    @app.get("/favicon.ico")
    def favicon() -> RedirectResponse:
        return RedirectResponse(url="/static/dashboard/favicon.svg")

    logger.bind(component="dashboard").info(
        "Dashboard app created for local project root {}",
        root,
    )
    return app
