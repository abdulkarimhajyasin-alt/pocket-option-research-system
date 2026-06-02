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
from app.research_api.service import UnifiedResearchAPIService
from app.research_archive.service import ResearchArchiveService
from app.platform_certification.service import PlatformCertificationService
from app.release_packaging.service import ReleasePackagingService
from app.post_research_architecture.service import PostResearchArchitectureService
from app.trading_architecture_program.service import TradingArchitectureProgramService
from app.trading_requirements.service import TradingRequirementsService
from app.production_system_design.service import ProductionSystemDesignService
from app.operational_governance.service import OperationalGovernanceService
from app.governance_traceability.service import GovernanceTraceabilityService
from app.control_assurance.service import ControlAssuranceService
from app.review_board_simulation.service import ReviewBoardSimulationService
from app.repository_hygiene.service import RepositoryHygieneService

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

    @app.get("/architecture-audit", response_class=HTMLResponse)
    def architecture_audit(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/architecture_audit.html",
            context(
                request,
                dashboard,
                page="architecture_audit",
                architecture_audit=dashboard.analytics.architecture_audit_analytics(),
            ),
        )

    @app.get("/knowledge-graph", response_class=HTMLResponse)
    def knowledge_graph(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/knowledge_graph.html",
            context(
                request,
                dashboard,
                page="knowledge_graph",
                knowledge_graph=dashboard.analytics.knowledge_graph_analytics(),
            ),
        )

    @app.get("/research-api", response_class=HTMLResponse)
    def research_api(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/research_api.html",
            context(
                request,
                dashboard,
                page="research_api",
                research_api=dashboard.analytics.research_api_analytics(),
            ),
        )

    @app.get("/research-archive", response_class=HTMLResponse)
    def research_archive(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/research_archive.html",
            context(
                request,
                dashboard,
                page="research_archive",
                research_archive=dashboard.analytics.research_archive_analytics(),
            ),
        )

    @app.get("/platform-certification", response_class=HTMLResponse)
    def platform_certification(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/platform_certification.html",
            context(
                request,
                dashboard,
                page="platform_certification",
                platform_certification=dashboard.analytics.platform_certification_analytics(),
            ),
        )

    @app.get("/release-packaging", response_class=HTMLResponse)
    def release_packaging(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/release_packaging.html",
            context(
                request,
                dashboard,
                page="release_packaging",
                release_packaging=dashboard.analytics.release_packaging_analytics(),
            ),
        )

    @app.get("/post-research-architecture", response_class=HTMLResponse)
    def post_research_architecture(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/post_research_architecture.html",
            context(
                request,
                dashboard,
                page="post_research_architecture",
                post_research_architecture=(
                    dashboard.analytics.post_research_architecture_analytics()
                ),
            ),
        )

    @app.get("/trading-architecture-program", response_class=HTMLResponse)
    def trading_architecture_program(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/trading_architecture_program.html",
            context(
                request,
                dashboard,
                page="trading_architecture_program",
                trading_architecture_program=(
                    dashboard.analytics.trading_architecture_program_analytics()
                ),
            ),
        )

    @app.get("/trading-requirements", response_class=HTMLResponse)
    def trading_requirements(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/trading_requirements.html",
            context(
                request,
                dashboard,
                page="trading_requirements",
                trading_requirements=dashboard.analytics.trading_requirements_analytics(),
            ),
        )

    @app.get("/production-system-design", response_class=HTMLResponse)
    def production_system_design(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/production_system_design.html",
            context(
                request,
                dashboard,
                page="production_system_design",
                production_system_design=dashboard.analytics.production_system_design_analytics(),
            ),
        )

    @app.get("/operational-governance", response_class=HTMLResponse)
    def operational_governance(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/operational_governance.html",
            context(
                request,
                dashboard,
                page="operational_governance",
                operational_governance=dashboard.analytics.operational_governance_analytics(),
            ),
        )

    @app.get("/governance-traceability", response_class=HTMLResponse)
    def governance_traceability(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/governance_traceability.html",
            context(
                request,
                dashboard,
                page="governance_traceability",
                governance_traceability=dashboard.analytics.governance_traceability_analytics(),
            ),
        )

    @app.get("/control-assurance", response_class=HTMLResponse)
    def control_assurance(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/control_assurance.html",
            context(
                request,
                dashboard,
                page="control_assurance",
                control_assurance=dashboard.analytics.control_assurance_analytics(),
            ),
        )

    @app.get("/review-board-simulation", response_class=HTMLResponse)
    def review_board_simulation(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/review_board_simulation.html",
            context(
                request,
                dashboard,
                page="review_board_simulation",
                review_board_simulation=dashboard.analytics.review_board_simulation_analytics(),
            ),
        )

    @app.get("/repository-hygiene", response_class=HTMLResponse)
    def repository_hygiene(request: Request) -> HTMLResponse:
        dashboard = dashboard_context()
        return templates.TemplateResponse(
            request,
            "dashboard/repository_hygiene.html",
            context(
                request,
                dashboard,
                page="repository_hygiene",
                repository_hygiene=dashboard.analytics.repository_hygiene_analytics(),
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

    @app.get("/api/architecture-audit")
    def api_architecture_audit() -> dict[str, object]:
        return dashboard_context().analytics.architecture_audit_analytics()

    @app.get("/api/knowledge-graph")
    def api_knowledge_graph() -> dict[str, object]:
        return dashboard_context().analytics.knowledge_graph_analytics()

    @app.get("/api/research")
    def api_research() -> dict[str, object]:
        return UnifiedResearchAPIService(root).snapshot().to_dict()

    @app.get("/api/research/signals")
    def api_research_signals() -> dict[str, object]:
        return UnifiedResearchAPIService(root).signals()

    @app.get("/api/research/opportunities")
    def api_research_opportunities() -> dict[str, object]:
        return UnifiedResearchAPIService(root).opportunities()

    @app.get("/api/research/paper")
    def api_research_paper() -> dict[str, object]:
        return UnifiedResearchAPIService(root).paper()

    @app.get("/api/research/readiness")
    def api_research_readiness() -> dict[str, object]:
        return UnifiedResearchAPIService(root).readiness()

    @app.get("/api/research/knowledge-graph")
    def api_research_knowledge_graph() -> dict[str, object]:
        return UnifiedResearchAPIService(root).knowledge_graph()

    @app.get("/api/research/diagnostics")
    def api_research_diagnostics() -> dict[str, object]:
        return UnifiedResearchAPIService(root).diagnostics_view()

    @app.get("/api/research-archive")
    def api_research_archive() -> dict[str, object]:
        return dashboard_context().analytics.research_archive_analytics()

    @app.get("/api/research-archive/latest")
    def api_research_archive_latest() -> dict[str, object]:
        return ResearchArchiveService(root).get_latest_version()

    @app.get("/api/research-archive/history")
    def api_research_archive_history() -> list[dict[str, object]]:
        return ResearchArchiveService(root).get_version_history()

    @app.get("/api/research-archive/diff")
    def api_research_archive_diff() -> dict[str, object]:
        return ResearchArchiveService(root).compare_latest_with_previous()

    @app.get("/api/research-archive/evolution")
    def api_research_archive_evolution() -> dict[str, object]:
        return ResearchArchiveService(root).generate_evolution_report()

    @app.get("/api/research-archive/diagnostics")
    def api_research_archive_diagnostics() -> dict[str, object]:
        service = ResearchArchiveService(root)
        latest = service.get_latest_version()
        snapshot = (
            service.storage.load_snapshot(str(latest.get("version_label", "")))
            if latest
            else service.build_current_snapshot().to_dict()
        )
        return {
            "diagnostics": service._diagnostics_from_current(snapshot),
            "research_only": True,
            "local_only": True,
        }

    @app.get("/api/platform-certification")
    def api_platform_certification() -> dict[str, object]:
        return PlatformCertificationService(root).certify().to_dict()

    @app.get("/api/platform-certification/summary")
    def api_platform_certification_summary() -> dict[str, object]:
        return PlatformCertificationService(root).summary()

    @app.get("/api/platform-certification/domains")
    def api_platform_certification_domains() -> list[dict[str, object]]:
        return PlatformCertificationService(root).domains()

    @app.get("/api/platform-certification/diagnostics")
    def api_platform_certification_diagnostics() -> list[dict[str, object]]:
        return PlatformCertificationService(root).diagnostics_view()

    @app.get("/api/platform-certification/recommendations")
    def api_platform_certification_recommendations() -> list[str]:
        return PlatformCertificationService(root).recommendations_view()

    @app.get("/api/release-packaging")
    def api_release_packaging() -> dict[str, object]:
        return dashboard_context().analytics.release_packaging_analytics()

    @app.get("/api/release-packaging/manifest")
    def api_release_packaging_manifest() -> dict[str, object]:
        return ReleasePackagingService(root).get_release_manifest()

    @app.get("/api/release-packaging/status")
    def api_release_packaging_status() -> dict[str, object]:
        return ReleasePackagingService(root).get_project_status()

    @app.get("/api/release-packaging/notes")
    def api_release_packaging_notes() -> dict[str, object]:
        return ReleasePackagingService(root).get_release_notes()

    @app.get("/api/release-packaging/diagnostics")
    def api_release_packaging_diagnostics() -> list[dict[str, object]]:
        return ReleasePackagingService(root).generate_diagnostics()

    @app.get("/api/release-packaging/recommendations")
    def api_release_packaging_recommendations() -> list[str]:
        return ReleasePackagingService(root).generate_recommendations()

    @app.get("/api/post-research-architecture")
    def api_post_research_architecture() -> dict[str, object]:
        return dashboard_context().analytics.post_research_architecture_analytics()

    @app.get("/api/post-research-architecture/roadmap")
    def api_post_research_architecture_roadmap() -> dict[str, object]:
        return PostResearchArchitectureService(root).roadmap()

    @app.get("/api/post-research-architecture/gaps")
    def api_post_research_architecture_gaps() -> dict[str, object]:
        return PostResearchArchitectureService(root).gaps()

    @app.get("/api/post-research-architecture/blueprints")
    def api_post_research_architecture_blueprints() -> dict[str, object]:
        return PostResearchArchitectureService(root).blueprints()

    @app.get("/api/post-research-architecture/transition")
    def api_post_research_architecture_transition() -> dict[str, object]:
        return PostResearchArchitectureService(root).transition()

    @app.get("/api/post-research-architecture/diagnostics")
    def api_post_research_architecture_diagnostics() -> list[dict[str, object]]:
        return PostResearchArchitectureService(root).generate_diagnostics()

    @app.get("/api/post-research-architecture/recommendations")
    def api_post_research_architecture_recommendations() -> list[str]:
        return PostResearchArchitectureService(root).generate_recommendations()

    @app.get("/api/trading-architecture-program")
    def api_trading_architecture_program() -> dict[str, object]:
        return dashboard_context().analytics.trading_architecture_program_analytics()

    @app.get("/api/trading-architecture-program/gates")
    def api_trading_architecture_program_gates() -> list[dict[str, object]]:
        return TradingArchitectureProgramService(root).gates()

    @app.get("/api/trading-architecture-program/workstreams")
    def api_trading_architecture_program_workstreams() -> list[dict[str, object]]:
        return TradingArchitectureProgramService(root).workstreams()

    @app.get("/api/trading-architecture-program/domains")
    def api_trading_architecture_program_domains() -> list[dict[str, object]]:
        return TradingArchitectureProgramService(root).domains()

    @app.get("/api/trading-architecture-program/diagnostics")
    def api_trading_architecture_program_diagnostics() -> list[dict[str, object]]:
        return TradingArchitectureProgramService(root).generate_diagnostics()

    @app.get("/api/trading-requirements")
    def api_trading_requirements() -> dict[str, object]:
        return dashboard_context().analytics.trading_requirements_analytics()

    @app.get("/api/trading-requirements/functional")
    def api_trading_requirements_functional() -> dict[str, object]:
        return TradingRequirementsService(root).build_functional_requirements()

    @app.get("/api/trading-requirements/non-functional")
    def api_trading_requirements_non_functional() -> dict[str, object]:
        return TradingRequirementsService(root).build_non_functional_requirements()

    @app.get("/api/trading-requirements/safety")
    def api_trading_requirements_safety() -> dict[str, object]:
        return TradingRequirementsService(root).build_safety_requirements()

    @app.get("/api/trading-requirements/risk")
    def api_trading_requirements_risk() -> dict[str, object]:
        return TradingRequirementsService(root).build_risk_requirements()

    @app.get("/api/trading-requirements/compliance")
    def api_trading_requirements_compliance() -> dict[str, object]:
        return TradingRequirementsService(root).build_compliance_constraints()

    @app.get("/api/trading-requirements/broker")
    def api_trading_requirements_broker() -> dict[str, object]:
        return TradingRequirementsService(root).build_broker_constraints()

    @app.get("/api/trading-requirements/execution")
    def api_trading_requirements_execution() -> dict[str, object]:
        return TradingRequirementsService(root).build_execution_constraints()

    @app.get("/api/trading-requirements/monitoring")
    def api_trading_requirements_monitoring() -> dict[str, object]:
        return TradingRequirementsService(root).build_monitoring_constraints()

    @app.get("/api/trading-requirements/data")
    def api_trading_requirements_data() -> dict[str, object]:
        return TradingRequirementsService(root).build_data_constraints()

    @app.get("/api/trading-requirements/go-no-go")
    def api_trading_requirements_go_no_go() -> dict[str, object]:
        return TradingRequirementsService(root).build_go_no_go_criteria()

    @app.get("/api/trading-requirements/diagnostics")
    def api_trading_requirements_diagnostics() -> list[dict[str, object]]:
        return TradingRequirementsService(root).generate_diagnostics()

    @app.get("/api/trading-requirements/recommendations")
    def api_trading_requirements_recommendations() -> list[str]:
        return TradingRequirementsService(root).generate_recommendations()

    @app.get("/api/production-system-design")
    def api_production_system_design() -> dict[str, object]:
        return dashboard_context().analytics.production_system_design_analytics()

    @app.get("/api/production-system-design/topology")
    def api_production_system_design_topology() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_topology()

    @app.get("/api/production-system-design/service-boundaries")
    def api_production_system_design_service_boundaries() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_service_boundaries()

    @app.get("/api/production-system-design/runtime")
    def api_production_system_design_runtime() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_runtime_architecture()

    @app.get("/api/production-system-design/environments")
    def api_production_system_design_environments() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_environment_strategy()

    @app.get("/api/production-system-design/configuration")
    def api_production_system_design_configuration() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_configuration_strategy()

    @app.get("/api/production-system-design/secrets")
    def api_production_system_design_secrets() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_secrets_strategy()

    @app.get("/api/production-system-design/database")
    def api_production_system_design_database() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_database_strategy()

    @app.get("/api/production-system-design/events")
    def api_production_system_design_events() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_event_queue_strategy()

    @app.get("/api/production-system-design/logging")
    def api_production_system_design_logging() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_logging_strategy()

    @app.get("/api/production-system-design/monitoring")
    def api_production_system_design_monitoring() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_monitoring_strategy()

    @app.get("/api/production-system-design/alerting")
    def api_production_system_design_alerting() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_alerting_strategy()

    @app.get("/api/production-system-design/incidents")
    def api_production_system_design_incidents() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_incident_response()

    @app.get("/api/production-system-design/backup-recovery")
    def api_production_system_design_backup_recovery() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_backup_recovery()

    @app.get("/api/production-system-design/release-rollback")
    def api_production_system_design_release_rollback() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_release_rollback()

    @app.get("/api/production-system-design/readiness-gates")
    def api_production_system_design_readiness_gates() -> dict[str, object]:
        return ProductionSystemDesignService(root).build_readiness_gates()

    @app.get("/api/production-system-design/diagnostics")
    def api_production_system_design_diagnostics() -> list[dict[str, object]]:
        return ProductionSystemDesignService(root).generate_diagnostics()

    @app.get("/api/production-system-design/recommendations")
    def api_production_system_design_recommendations() -> list[str]:
        return ProductionSystemDesignService(root).generate_recommendations()

    @app.get("/api/operational-governance")
    def api_operational_governance() -> dict[str, object]:
        return dashboard_context().analytics.operational_governance_analytics()

    @app.get("/api/operational-governance/authority")
    def api_operational_governance_authority() -> dict[str, object]:
        return OperationalGovernanceService(root).build_authority_model()

    @app.get("/api/operational-governance/approval-workflows")
    def api_operational_governance_approval_workflows() -> dict[str, object]:
        return OperationalGovernanceService(root).build_approval_workflows()

    @app.get("/api/operational-governance/change-management")
    def api_operational_governance_change_management() -> dict[str, object]:
        return OperationalGovernanceService(root).build_change_management()

    @app.get("/api/operational-governance/release-governance")
    def api_operational_governance_release_governance() -> dict[str, object]:
        return OperationalGovernanceService(root).build_release_governance()

    @app.get("/api/operational-governance/incidents")
    def api_operational_governance_incidents() -> dict[str, object]:
        return OperationalGovernanceService(root).build_incident_escalation()

    @app.get("/api/operational-governance/kill-switch")
    def api_operational_governance_kill_switch() -> dict[str, object]:
        return OperationalGovernanceService(root).build_kill_switch_governance()

    @app.get("/api/operational-governance/audit-controls")
    def api_operational_governance_audit_controls() -> dict[str, object]:
        return OperationalGovernanceService(root).build_audit_controls()

    @app.get("/api/operational-governance/operators")
    def api_operational_governance_operators() -> dict[str, object]:
        return OperationalGovernanceService(root).build_operator_responsibility()

    @app.get("/api/operational-governance/review-boards")
    def api_operational_governance_review_boards() -> dict[str, object]:
        return OperationalGovernanceService(root).build_review_boards()

    @app.get("/api/operational-governance/decision-matrix")
    def api_operational_governance_decision_matrix() -> dict[str, object]:
        return OperationalGovernanceService(root).build_decision_matrix()

    @app.get("/api/operational-governance/control-evidence")
    def api_operational_governance_control_evidence() -> dict[str, object]:
        return OperationalGovernanceService(root).build_control_evidence()

    @app.get("/api/operational-governance/policies")
    def api_operational_governance_policies() -> dict[str, object]:
        return OperationalGovernanceService(root).build_policy_registry()

    @app.get("/api/operational-governance/readiness-gates")
    def api_operational_governance_readiness_gates() -> dict[str, object]:
        return OperationalGovernanceService(root).build_readiness_gates()

    @app.get("/api/operational-governance/diagnostics")
    def api_operational_governance_diagnostics() -> list[dict[str, object]]:
        return OperationalGovernanceService(root).generate_diagnostics()

    @app.get("/api/operational-governance/recommendations")
    def api_operational_governance_recommendations() -> list[str]:
        return OperationalGovernanceService(root).generate_recommendations()

    @app.get("/api/governance-traceability")
    def api_governance_traceability() -> dict[str, object]:
        return dashboard_context().analytics.governance_traceability_analytics()

    @app.get("/api/governance-traceability/mappings")
    def api_governance_traceability_mappings() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_control_mappings()

    @app.get("/api/governance-traceability/control-matrix")
    def api_governance_traceability_control_matrix() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_control_matrix()

    @app.get("/api/governance-traceability/evidence-matrix")
    def api_governance_traceability_evidence_matrix() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_evidence_matrix()

    @app.get("/api/governance-traceability/readiness")
    def api_governance_traceability_readiness() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_readiness_mapping()

    @app.get("/api/governance-traceability/risks")
    def api_governance_traceability_risks() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_risk_mapping()

    @app.get("/api/governance-traceability/incidents")
    def api_governance_traceability_incidents() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_incident_mapping()

    @app.get("/api/governance-traceability/releases")
    def api_governance_traceability_releases() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_release_mapping()

    @app.get("/api/governance-traceability/monitoring")
    def api_governance_traceability_monitoring() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_monitoring_mapping()

    @app.get("/api/governance-traceability/policies")
    def api_governance_traceability_policies() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_policy_mapping()

    @app.get("/api/governance-traceability/coverage")
    def api_governance_traceability_coverage() -> dict[str, object]:
        return GovernanceTraceabilityService(root).build_coverage_summary()

    @app.get("/api/governance-traceability/diagnostics")
    def api_governance_traceability_diagnostics() -> list[dict[str, object]]:
        return GovernanceTraceabilityService(root).generate_diagnostics()

    @app.get("/api/governance-traceability/recommendations")
    def api_governance_traceability_recommendations() -> list[str]:
        return GovernanceTraceabilityService(root).generate_recommendations()

    @app.get("/api/control-assurance")
    def api_control_assurance() -> dict[str, object]:
        return dashboard_context().analytics.control_assurance_analytics()

    @app.get("/api/control-assurance/control-quality")
    def api_control_assurance_control_quality() -> dict[str, object]:
        return ControlAssuranceService(root).assess_control_quality()

    @app.get("/api/control-assurance/evidence")
    def api_control_assurance_evidence() -> dict[str, object]:
        return ControlAssuranceService(root).assess_evidence_sufficiency()

    @app.get("/api/control-assurance/owners")
    def api_control_assurance_owners() -> dict[str, object]:
        return ControlAssuranceService(root).assess_owner_clarity()

    @app.get("/api/control-assurance/policies")
    def api_control_assurance_policies() -> dict[str, object]:
        return ControlAssuranceService(root).assess_policy_completeness()

    @app.get("/api/control-assurance/gates")
    def api_control_assurance_gates() -> dict[str, object]:
        return ControlAssuranceService(root).assess_gate_maturity()

    @app.get("/api/control-assurance/weaknesses")
    def api_control_assurance_weaknesses() -> dict[str, object]:
        return ControlAssuranceService(root).assess_weaknesses()

    @app.get("/api/control-assurance/audit-readiness")
    def api_control_assurance_audit_readiness() -> dict[str, object]:
        return ControlAssuranceService(root).assess_audit_readiness()

    @app.get("/api/control-assurance/review-readiness")
    def api_control_assurance_review_readiness() -> dict[str, object]:
        return ControlAssuranceService(root).assess_governance_review_readiness()

    @app.get("/api/control-assurance/scorecard")
    def api_control_assurance_scorecard() -> dict[str, object]:
        return ControlAssuranceService(root).build_scorecard()

    @app.get("/api/control-assurance/diagnostics")
    def api_control_assurance_diagnostics() -> list[dict[str, object]]:
        return ControlAssuranceService(root).generate_diagnostics()

    @app.get("/api/control-assurance/recommendations")
    def api_control_assurance_recommendations() -> list[str]:
        return ControlAssuranceService(root).generate_recommendations()

    @app.get("/api/review-board-simulation")
    def api_review_board_simulation() -> dict[str, object]:
        return dashboard_context().analytics.review_board_simulation_analytics()

    @app.get("/api/review-board-simulation/boards")
    def api_review_board_simulation_boards() -> dict[str, object]:
        return ReviewBoardSimulationService(root).build_board_registry()

    @app.get("/api/review-board-simulation/decisions")
    def api_review_board_simulation_decisions() -> dict[str, object]:
        boards = ReviewBoardSimulationService(root).simulate_board_reviews()
        return {
            "items": [
                decision
                for board in boards.get("items", [])
                for decision in board.get("simulated_decisions", [])
            ],
            "simulation_only": True,
            "review_only": True,
            "dry_run_only": True,
            "local_only": True,
        }

    @app.get("/api/review-board-simulation/gates")
    def api_review_board_simulation_gates() -> dict[str, object]:
        return ReviewBoardSimulationService(root).run_gate_dry_run()

    @app.get("/api/review-board-simulation/evidence")
    def api_review_board_simulation_evidence() -> dict[str, object]:
        return ReviewBoardSimulationService(root).review_evidence()

    @app.get("/api/review-board-simulation/blockers")
    def api_review_board_simulation_blockers() -> dict[str, object]:
        return ReviewBoardSimulationService(root).analyze_blockers()

    @app.get("/api/review-board-simulation/scores")
    def api_review_board_simulation_scores() -> dict[str, object]:
        return ReviewBoardSimulationService(root).build_decision_scores()

    @app.get("/api/review-board-simulation/findings")
    def api_review_board_simulation_findings() -> dict[str, object]:
        return ReviewBoardSimulationService(root).build_findings()

    @app.get("/api/review-board-simulation/readiness")
    def api_review_board_simulation_readiness() -> dict[str, object]:
        return ReviewBoardSimulationService(root).build_readiness_summary()

    @app.get("/api/review-board-simulation/diagnostics")
    def api_review_board_simulation_diagnostics() -> list[dict[str, object]]:
        return ReviewBoardSimulationService(root).generate_diagnostics()

    @app.get("/api/review-board-simulation/recommendations")
    def api_review_board_simulation_recommendations() -> list[str]:
        return ReviewBoardSimulationService(root).generate_recommendations()

    @app.get("/api/repository-hygiene")
    def api_repository_hygiene() -> dict[str, object]:
        return dashboard_context().analytics.repository_hygiene_analytics()

    @app.get("/api/repository-hygiene/git-status")
    def api_repository_hygiene_git_status() -> dict[str, object]:
        return RepositoryHygieneService(root).parse_git_status()

    @app.get("/api/repository-hygiene/artifacts")
    def api_repository_hygiene_artifacts() -> dict[str, object]:
        return RepositoryHygieneService(root).build_artifact_inventory()

    @app.get("/api/repository-hygiene/retention-policy")
    def api_repository_hygiene_retention_policy() -> dict[str, object]:
        return RepositoryHygieneService(root).build_retention_policy()

    @app.get("/api/repository-hygiene/cleanup-plan")
    def api_repository_hygiene_cleanup_plan() -> dict[str, object]:
        return RepositoryHygieneService(root).build_cleanup_plan()

    @app.get("/api/repository-hygiene/ignore-recommendations")
    def api_repository_hygiene_ignore_recommendations() -> dict[str, object]:
        return RepositoryHygieneService(root).build_ignore_recommendations()

    @app.get("/api/repository-hygiene/duplicates")
    def api_repository_hygiene_duplicates() -> dict[str, object]:
        return RepositoryHygieneService(root).detect_duplicates()

    @app.get("/api/repository-hygiene/stale")
    def api_repository_hygiene_stale() -> dict[str, object]:
        return RepositoryHygieneService(root).detect_stale_artifacts()

    @app.get("/api/repository-hygiene/archive-policy")
    def api_repository_hygiene_archive_policy() -> dict[str, object]:
        return RepositoryHygieneService(root).build_archive_policy()

    @app.get("/api/repository-hygiene/scorecard")
    def api_repository_hygiene_scorecard() -> dict[str, object]:
        return RepositoryHygieneService(root).build_scorecard()

    @app.get("/api/repository-hygiene/diagnostics")
    def api_repository_hygiene_diagnostics() -> list[dict[str, object]]:
        return RepositoryHygieneService(root).generate_diagnostics()

    @app.get("/api/repository-hygiene/recommendations")
    def api_repository_hygiene_recommendations() -> list[str]:
        return RepositoryHygieneService(root).generate_recommendations()

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
