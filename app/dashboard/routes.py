"""FastAPI routes for the local research dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.dashboard.context import DashboardContext
from app.dashboard.decision import (
    dataset_decision,
    strategy_decision,
    validation_decision,
)
from app.dashboard.formatting import (
    format_duration,
    format_datetime,
    format_metric,
    format_number,
    format_percent,
    format_relative_time,
)
from app.dashboard.service import DashboardService, load_dashboard_config
from app.jobs.manager import JobManager
from app.reports.repository import ReportRepository
from app.i18n import DEFAULT_LANGUAGE, get_translations


SAFETY_NOTE = (
    "This is a local research dashboard. It does not execute live trades, connect to "
    "real-money accounts, or automate broker actions."
)


def create_dashboard_app(project_root: Path | str = ".") -> FastAPI:
    """Create the local dashboard FastAPI application."""
    root = Path(project_root).resolve()
    repository = ReportRepository(root, load_dashboard_config(root).reports_dir)
    service = DashboardService(root, repository=repository)
    jobs = JobManager(service.actions.job_registry())
    translations = get_translations(DEFAULT_LANGUAGE)
    templates = Jinja2Templates(directory=str(root / "app" / "templates"))
    templates.env.filters["datetime_ar"] = format_datetime
    templates.env.filters["metric_ar"] = format_metric
    templates.env.filters["number_ar"] = format_number
    templates.env.filters["percent_ar"] = format_percent
    templates.env.filters["relative_ar"] = format_relative_time
    templates.env.globals["duration_ar"] = format_duration
    templates.env.globals["dataset_decision"] = dataset_decision
    templates.env.globals["strategy_decision"] = strategy_decision
    templates.env.globals["validation_decision"] = validation_decision
    app = FastAPI(
        title="Pocket Option Research Dashboard",
        description="Local-only research dashboard. No live trading.",
        version="0.1.0",
    )
    static_dir = root / "app" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def dashboard_context() -> DashboardContext:
        return DashboardContext.create(root, repository, jobs)

    def context(
        request: Request,
        dashboard: DashboardContext,
        **values: object,
    ) -> dict[str, object]:
        return {
            "request": request,
            "safety_note": translations["app"]["safety"],
            "t": translations,
            "language": DEFAULT_LANGUAGE,
            "config": dashboard.service.config,
            **values,
        }

    @app.get("/", response_class=HTMLResponse)
    def overview(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        workbench = dashboard.metrics.workbench()
        return templates.TemplateResponse(
            request,
            "dashboard/overview.html",
            context(
                request,
                dashboard,
                page="overview",
                overview=workbench["overview"],
                workbench=workbench,
            ),
        )

    @app.get("/strategies", response_class=HTMLResponse)
    def strategies(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/strategies.html",
            context(
                request,
                dashboard,
                page="strategies",
                strategies=dashboard.service.strategy_summaries(),
            ),
        )

    @app.get("/datasets", response_class=HTMLResponse)
    def datasets(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/datasets.html",
            context(
                request,
                dashboard,
                page="datasets",
                datasets=dashboard.service.dataset_summaries(),
                dataset_analytics=dashboard.analytics.dataset_analytics(),
            ),
        )

    @app.get("/datasets/{dataset_id}", response_class=HTMLResponse)
    def dataset_detail(request: Request, dataset_id: str) -> HTMLResponse:
        dashboard = dashboard_context()
        dataset = next(
            (
                item
                for item in dashboard.service.dataset_summaries()
                if item.dataset_id == dataset_id
            ),
            None,
        )
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return templates.TemplateResponse(
            request,
            "dashboard/dataset_detail.html",
            context(
                request,
                dashboard,
                page="datasets",
                dataset=dataset,
                dataset_analytics=dashboard.analytics.dataset_analytics(),
            ),
        )

    @app.get("/validation", response_class=HTMLResponse)
    def validation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/validation.html",
            context(
                request,
                dashboard,
                page="validation",
                validations=dashboard.service.validation_summaries(),
                validation_analytics=dashboard.analytics.validation_analytics(),
            ),
        )

    @app.get("/validation/{report_id}", response_class=HTMLResponse)
    def validation_detail(request: Request, report_id: str) -> HTMLResponse:
        dashboard = dashboard_context()
        validation_item = next(
            (
                item
                for item in dashboard.service.validation_summaries()
                if item.report_id == report_id
            ),
            None,
        )
        if validation_item is None:
            raise HTTPException(status_code=404, detail="Validation report not found")
        return templates.TemplateResponse(
            request,
            "dashboard/validation_detail.html",
            context(
                request,
                dashboard,
                page="validation",
                validation=validation_item,
                validation_analytics=dashboard.analytics.validation_analytics(),
            ),
        )

    @app.get("/signals", response_class=HTMLResponse)
    def signals(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/signals.html",
            context(
                request,
                dashboard,
                page="signals",
                signal_analytics=dashboard.analytics.signal_analytics(),
            ),
        )

    @app.get("/reports", response_class=HTMLResponse)
    def reports(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/reports.html",
            context(
                request,
                dashboard,
                page="reports",
                reports=dashboard.repository.list_reports(),
            ),
        )

    @app.get("/reports/{report_id}", response_class=HTMLResponse)
    def report_detail(request: Request, report_id: str) -> HTMLResponse:
        dashboard = dashboard_context()
        report = dashboard.repository.get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return templates.TemplateResponse(
            request,
            "dashboard/report_detail.html",
            context(
                request,
                dashboard,
                page="reports",
                report=report,
                visualization=dashboard.analytics.report_visualization(report.json_data),
            ),
        )

    @app.get("/execution", response_class=HTMLResponse)
    def execution(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/execution.html",
            context(
                request,
                dashboard,
                page="execution",
                execution=dashboard.analytics.execution_analytics(),
            ),
        )

    @app.get("/observation", response_class=HTMLResponse)
    def observation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/observation.html",
            context(
                request,
                dashboard,
                page="observation",
                observation=dashboard.analytics.observation_analytics(),
            ),
        )

    @app.get("/live-feed", response_class=HTMLResponse)
    def live_feed(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/live_feed.html",
            context(
                request,
                dashboard,
                page="live_feed",
                live_feed=dashboard.analytics.live_feed_analytics(),
            ),
        )

    @app.get("/market-data", response_class=HTMLResponse)
    def market_data(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/market_data.html",
            context(
                request,
                dashboard,
                page="market_data",
                market_data=dashboard.analytics.market_data_analytics(),
            ),
        )

    @app.get("/api/dashboard")
    def api_dashboard() -> dict[str, object]:
        dashboard = dashboard_context()
        return jsonable_encoder(dashboard.metrics.workbench())

    @app.get("/api/metrics")
    def api_metrics() -> dict[str, object]:
        dashboard = dashboard_context()
        workbench = dashboard.metrics.workbench()
        return {"health": workbench["health"], "metrics": workbench["metrics"]}

    @app.get("/api/validation")
    def api_validation() -> dict[str, object]:
        return dashboard_context().analytics.validation_analytics()

    @app.get("/api/datasets")
    def api_datasets() -> dict[str, object]:
        return dashboard_context().analytics.dataset_analytics()

    @app.get("/api/signals")
    def api_signals() -> dict[str, object]:
        return dashboard_context().analytics.signal_analytics()

    @app.get("/api/execution")
    def api_execution() -> dict[str, object]:
        return dashboard_context().analytics.execution_analytics()

    @app.get("/api/observation")
    def api_observation() -> dict[str, object]:
        return dashboard_context().analytics.observation_analytics()

    @app.get("/api/live-feed")
    def api_live_feed() -> dict[str, object]:
        return dashboard_context().analytics.live_feed_analytics()

    @app.get("/api/market-data")
    def api_market_data() -> dict[str, object]:
        return dashboard_context().analytics.market_data_analytics()

    @app.get("/actions", response_class=HTMLResponse)
    def actions(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/actions.html",
            context(
                request,
                dashboard,
                page="actions",
                actions=dashboard.service.actions.list_actions(),
                result=None,
            ),
        )

    @app.post("/actions/run/{action_name}", response_class=HTMLResponse)
    def run_action(request: Request, action_name: str) -> HTMLResponse:
        dashboard = dashboard_context()
        if not dashboard.service.config.allow_actions:
            raise HTTPException(status_code=403, detail="Dashboard actions are disabled")
        try:
            job = jobs.enqueue(action_name)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return RedirectResponse(url=f"/jobs?run_id={job.run_id}", status_code=303)

    @app.get("/jobs", response_class=HTMLResponse)
    def job_monitor(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/jobs.html",
            context(
                request,
                dashboard,
                page="jobs",
                jobs=dashboard.jobs.list_jobs(),
            ),
        )

    @app.get("/api/jobs")
    def api_jobs() -> dict[str, object]:
        return {"jobs": [job.to_dict() for job in jobs.list_jobs()]}

    @app.get("/diagnostics", response_class=HTMLResponse)
    def diagnostics(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/diagnostics.html",
            context(
                request,
                dashboard,
                page="diagnostics",
                diagnostics=dashboard.diagnostics(),
            ),
        )

    @app.get("/api/diagnostics")
    def api_diagnostics() -> dict[str, object]:
        return dashboard_context().diagnostics()

    @app.get("/health")
    def health() -> dict[str, object]:
        config = load_dashboard_config(root)
        return {
            "status": "ok",
            "local_only": True,
            "actions_enabled": config.allow_actions,
            "reports": len(repository.list_reports()),
            "language": DEFAULT_LANGUAGE,
            "active_jobs": jobs.active_count(),
        }

    @app.get("/favicon.ico")
    def favicon() -> RedirectResponse:
        return RedirectResponse(url="/static/dashboard/favicon.svg")

    logger.bind(component="dashboard").info(
        "Dashboard app created for local project root {}",
        root,
    )
    return app
