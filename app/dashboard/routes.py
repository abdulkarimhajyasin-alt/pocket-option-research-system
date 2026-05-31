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

    @app.get("/signals-intelligence", response_class=HTMLResponse)
    def signals_intelligence(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/signals_intelligence.html",
            context(
                request,
                dashboard,
                page="signals_intelligence",
                signals_intelligence=dashboard.analytics.signals_intelligence_analytics(),
            ),
        )

    @app.get("/signal-performance", response_class=HTMLResponse)
    def signal_performance(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/signal_performance.html",
            context(
                request,
                dashboard,
                page="signal_performance",
                signal_performance=dashboard.analytics.signal_performance_analytics(),
            ),
        )

    @app.get("/opportunities", response_class=HTMLResponse)
    def opportunities(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/opportunities.html",
            context(
                request,
                dashboard,
                page="opportunities",
                opportunities=dashboard.analytics.opportunities_analytics(),
            ),
        )

    @app.get("/multi-timeframe", response_class=HTMLResponse)
    def multi_timeframe(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/multi_timeframe.html",
            context(
                request,
                dashboard,
                page="multi_timeframe",
                multi_timeframe=dashboard.analytics.multi_timeframe_analytics(),
            ),
        )

    @app.get("/confluence", response_class=HTMLResponse)
    def confluence(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/confluence.html",
            context(
                request,
                dashboard,
                page="confluence",
                confluence=dashboard.analytics.confluence_analytics(),
            ),
        )

    @app.get("/trade-lifecycle", response_class=HTMLResponse)
    def trade_lifecycle(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/trade_lifecycle.html",
            context(
                request,
                dashboard,
                page="trade_lifecycle",
                trade_lifecycle=dashboard.analytics.trade_lifecycle_analytics(),
            ),
        )

    @app.get("/strategy-readiness", response_class=HTMLResponse)
    def strategy_readiness(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/strategy_readiness.html",
            context(
                request,
                dashboard,
                page="strategy_readiness",
                strategy_readiness=dashboard.analytics.strategy_readiness_analytics(),
            ),
        )

    @app.get("/strategy-benchmark", response_class=HTMLResponse)
    def strategy_benchmark(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/strategy_benchmark.html",
            context(
                request,
                dashboard,
                page="strategy_benchmark",
                strategy_benchmark=dashboard.analytics.strategy_benchmark_analytics(),
            ),
        )

    @app.get("/pattern-memory", response_class=HTMLResponse)
    def pattern_memory(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/pattern_memory.html",
            context(
                request,
                dashboard,
                page="pattern_memory",
                pattern_memory=dashboard.analytics.pattern_memory_analytics(),
            ),
        )

    @app.get("/market-regime", response_class=HTMLResponse)
    def market_regime(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/market_regime.html",
            context(
                request,
                dashboard,
                page="market_regime",
                market_regime=dashboard.analytics.market_regime_analytics(),
            ),
        )

    @app.get("/research-certification", response_class=HTMLResponse)
    def research_certification(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/research_certification.html",
            context(
                request,
                dashboard,
                page="research_certification",
                research_certification=dashboard.analytics.research_certification_analytics(),
            ),
        )

    @app.get("/broker-readiness", response_class=HTMLResponse)
    def broker_readiness(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/broker_readiness.html",
            context(
                request,
                dashboard,
                page="broker_readiness",
                broker_readiness=dashboard.analytics.broker_readiness_analytics(),
            ),
        )

    @app.get("/external-observation", response_class=HTMLResponse)
    def external_observation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/external_observation.html",
            context(
                request,
                dashboard,
                page="external_observation",
                external_observation=dashboard.analytics.external_observation_analytics(),
            ),
        )

    @app.get("/browser-observation", response_class=HTMLResponse)
    def browser_observation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/browser_observation.html",
            context(
                request,
                dashboard,
                page="browser_observation",
                browser_observation=dashboard.analytics.browser_observation_analytics(),
            ),
        )

    @app.get("/snapshot-import", response_class=HTMLResponse)
    def snapshot_import(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/snapshot_import.html",
            context(
                request,
                dashboard,
                page="snapshot_import",
                snapshot_import=dashboard.analytics.snapshot_import_analytics(),
                upload_message=None,
            ),
        )

    @app.post("/snapshot-import/upload", response_class=HTMLResponse)
    async def upload_snapshot(request: Request) -> HTMLResponse:
        from app.snapshot_import.importer import SnapshotImporter
        from app.snapshot_import.service import SnapshotImportService

        dashboard = dashboard_context()
        form = await request.form()
        upload = form.get("snapshot_file")
        message = "لم يتم اختيار ملف صالح"
        allowed_suffixes = {".html", ".json", ".txt"}
        if upload is not None and hasattr(upload, "filename"):
            filename = str(upload.filename or "")
            target = SnapshotImporter(root).safe_upload_path(filename)
            if target.suffix.lower() in allowed_suffixes:
                content = await upload.read()
                if len(content) <= 2_000_000:
                    target.write_bytes(content)
                    SnapshotImportService(root).run()
                    message = "تم حفظ اللقطة اليدوية وتحليلها"
                else:
                    message = "حجم الملف أكبر من الحد المسموح"
            else:
                message = "نوع الملف غير مدعوم"
        return templates.TemplateResponse(
            request,
            "dashboard/snapshot_import.html",
            context(
                request,
                dashboard,
                page="snapshot_import",
                snapshot_import=dashboard.analytics.snapshot_import_analytics(),
                upload_message=message,
            ),
        )

    @app.get("/observation-intelligence", response_class=HTMLResponse)
    def observation_intelligence(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/observation_intelligence.html",
            context(
                request,
                dashboard,
                page="observation_intelligence",
                observation_intelligence=dashboard.analytics.observation_intelligence_analytics(),
            ),
        )

    @app.get("/market-observation", response_class=HTMLResponse)
    def market_observation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/market_observation.html",
            context(
                request,
                dashboard,
                page="market_observation",
                market_observation=dashboard.analytics.market_observation_analytics(),
            ),
        )

    @app.get("/live-observation", response_class=HTMLResponse)
    def live_observation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/live_observation.html",
            context(
                request,
                dashboard,
                page="live_observation",
                live_observation=dashboard.analytics.live_observation_analytics(),
            ),
        )

    @app.get("/signal-stream", response_class=HTMLResponse)
    def signal_stream(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/signal_stream.html",
            context(
                request,
                dashboard,
                page="signal_stream",
                signal_stream=dashboard.analytics.signal_stream_analytics(),
            ),
        )

    @app.get("/execution-readiness", response_class=HTMLResponse)
    def execution_readiness(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/execution_readiness.html",
            context(
                request,
                dashboard,
                page="execution_readiness",
                execution_readiness=dashboard.analytics.execution_readiness_analytics(),
            ),
        )

    @app.get("/paper-execution", response_class=HTMLResponse)
    def paper_execution(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/paper_execution.html",
            context(
                request,
                dashboard,
                page="paper_execution",
                paper_execution=dashboard.analytics.paper_execution_analytics(),
            ),
        )

    @app.get("/paper-portfolio", response_class=HTMLResponse)
    def paper_portfolio(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/paper_portfolio.html",
            context(
                request,
                dashboard,
                page="paper_portfolio",
                paper_portfolio=dashboard.analytics.paper_portfolio_analytics(),
            ),
        )

    @app.get("/paper-control", response_class=HTMLResponse)
    def paper_control(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/paper_control.html",
            context(
                request,
                dashboard,
                page="paper_control",
                paper_control=dashboard.analytics.paper_control_analytics(),
            ),
        )

    @app.get("/paper-live-readiness", response_class=HTMLResponse)
    def paper_live_readiness(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/paper_live_readiness.html",
            context(
                request,
                dashboard,
                page="paper_live_readiness",
                paper_live_readiness=dashboard.analytics.paper_live_readiness_analytics(),
            ),
        )

    @app.get("/integration-safety", response_class=HTMLResponse)
    def integration_safety(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/integration_safety.html",
            context(
                request,
                dashboard,
                page="integration_safety",
                integration_safety=dashboard.analytics.integration_safety_analytics(),
            ),
        )

    @app.get("/research-operations", response_class=HTMLResponse)
    def research_operations(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/research_operations.html",
            context(
                request,
                dashboard,
                page="research_operations",
                research_ops=dashboard.analytics.research_operations_analytics(),
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

    @app.get("/api/signals-intelligence")
    def api_signals_intelligence() -> dict[str, object]:
        return dashboard_context().analytics.signals_intelligence_analytics()

    @app.get("/api/signal-performance")
    def api_signal_performance() -> dict[str, object]:
        return dashboard_context().analytics.signal_performance_analytics()

    @app.get("/api/opportunities")
    def api_opportunities() -> dict[str, object]:
        return dashboard_context().analytics.opportunities_analytics()

    @app.get("/api/multi-timeframe")
    def api_multi_timeframe() -> dict[str, object]:
        return dashboard_context().analytics.multi_timeframe_analytics()

    @app.get("/api/confluence")
    def api_confluence() -> dict[str, object]:
        return dashboard_context().analytics.confluence_analytics()

    @app.get("/api/trade-lifecycle")
    def api_trade_lifecycle() -> dict[str, object]:
        return dashboard_context().analytics.trade_lifecycle_analytics()

    @app.get("/api/strategy-readiness")
    def api_strategy_readiness() -> dict[str, object]:
        return dashboard_context().analytics.strategy_readiness_analytics()

    @app.get("/api/strategy-benchmark")
    def api_strategy_benchmark() -> dict[str, object]:
        return dashboard_context().analytics.strategy_benchmark_analytics()

    @app.get("/api/pattern-memory")
    def api_pattern_memory() -> dict[str, object]:
        return dashboard_context().analytics.pattern_memory_analytics()

    @app.get("/api/market-regime")
    def api_market_regime() -> dict[str, object]:
        return dashboard_context().analytics.market_regime_analytics()

    @app.get("/api/research-certification")
    def api_research_certification() -> dict[str, object]:
        return dashboard_context().analytics.research_certification_analytics()

    @app.get("/api/broker-readiness")
    def api_broker_readiness() -> dict[str, object]:
        return dashboard_context().analytics.broker_readiness_analytics()

    @app.get("/api/external-observation")
    def api_external_observation() -> dict[str, object]:
        return dashboard_context().analytics.external_observation_analytics()

    @app.get("/api/browser-observation")
    def api_browser_observation() -> dict[str, object]:
        return dashboard_context().analytics.browser_observation_analytics()

    @app.get("/api/snapshot-import")
    def api_snapshot_import() -> dict[str, object]:
        return dashboard_context().analytics.snapshot_import_analytics()

    @app.get("/api/observation-intelligence")
    def api_observation_intelligence() -> dict[str, object]:
        return dashboard_context().analytics.observation_intelligence_analytics()

    @app.get("/api/market-observation")
    def api_market_observation() -> dict[str, object]:
        return dashboard_context().analytics.market_observation_analytics()

    @app.get("/api/live-observation")
    def api_live_observation() -> dict[str, object]:
        return dashboard_context().analytics.live_observation_analytics()

    @app.get("/api/signal-stream")
    def api_signal_stream() -> dict[str, object]:
        return dashboard_context().analytics.signal_stream_analytics()

    @app.get("/api/execution-readiness")
    def api_execution_readiness() -> dict[str, object]:
        return dashboard_context().analytics.execution_readiness_analytics()

    @app.get("/api/paper-execution")
    def api_paper_execution() -> dict[str, object]:
        return dashboard_context().analytics.paper_execution_analytics()

    @app.get("/api/paper-portfolio")
    def api_paper_portfolio() -> dict[str, object]:
        return dashboard_context().analytics.paper_portfolio_analytics()

    @app.get("/api/paper-control")
    def api_paper_control() -> dict[str, object]:
        return dashboard_context().analytics.paper_control_analytics()

    @app.get("/api/paper-live-readiness")
    def api_paper_live_readiness() -> dict[str, object]:
        return dashboard_context().analytics.paper_live_readiness_analytics()

    @app.get("/api/integration-safety")
    def api_integration_safety() -> dict[str, object]:
        return dashboard_context().analytics.integration_safety_analytics()

    @app.get("/api/research-operations")
    def api_research_operations() -> dict[str, object]:
        return dashboard_context().analytics.research_operations_analytics()

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
