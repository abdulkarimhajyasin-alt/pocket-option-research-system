"""Request-level dashboard service context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from app.dashboard.analytics import DashboardAnalyticsService
from app.dashboard.metrics import DashboardMetricsService
from app.dashboard.service import DashboardService
from app.jobs.manager import JobManager
from app.reports.repository import ReportRepository


@dataclass
class DashboardContext:
    """Shared dashboard graph for one request."""

    repository: ReportRepository
    service: DashboardService
    analytics: DashboardAnalyticsService
    metrics: DashboardMetricsService
    jobs: JobManager
    started_at: float

    @classmethod
    def create(
        cls,
        project_root: Path,
        repository: ReportRepository,
        jobs: JobManager,
    ) -> "DashboardContext":
        """Create a request-scoped dashboard context from shared dependencies."""
        service = DashboardService(project_root, repository=repository)
        analytics = DashboardAnalyticsService(
            project_root,
            service.config.reports_dir,
            repository=repository,
        )
        metrics = DashboardMetricsService(
            project_root,
            service=service,
            analytics=analytics,
            jobs=jobs,
        )
        return cls(
            repository=repository,
            service=service,
            analytics=analytics,
            metrics=metrics,
            jobs=jobs,
            started_at=perf_counter(),
        )

    def diagnostics(self) -> dict[str, object]:
        """Return request and shared dashboard diagnostics."""
        reports = self.repository.list_reports()
        return {
            **self.repository.diagnostics(),
            **self.jobs.diagnostics(),
            "reports_indexed": len(reports),
            "dashboard_render_duration_ms": round((perf_counter() - self.started_at) * 1000, 3),
        }
