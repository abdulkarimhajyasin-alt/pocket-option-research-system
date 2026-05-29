"""Executive dashboard metrics for Phase 17 visualization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.dashboard.analytics import DashboardAnalyticsService
from app.dashboard.models import DashboardOverview
from app.dashboard.service import DashboardService


@dataclass(frozen=True)
class ExecutiveMetric:
    """One executive dashboard metric card."""

    key: str
    label: str
    value: str
    status: str

    def to_dict(self) -> dict[str, str]:
        """Return JSON-serializable metric data."""
        return {
            "key": self.key,
            "label": self.label,
            "value": self.value,
            "status": self.status,
        }


class DashboardMetricsService:
    """Compose dashboard service data into workbench metrics."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.service = DashboardService(self.project_root)
        self.analytics = DashboardAnalyticsService(
            self.project_root,
            self.service.config.reports_dir,
        )

    def workbench(self) -> dict[str, Any]:
        """Return the full overview workbench payload."""
        overview = self.service.overview()
        warning_count = sum(overview.warning_counts.values())
        health = self.health_status(overview)
        equity = self.analytics.equity_analytics()
        workflow = self.workflow(overview)
        activity = self.recent_activity(overview)
        insights = self.analytics.build_insights(
            overview.latest_robustness_score,
            overview.latest_dataset_quality_score,
            warning_count,
        )
        return {
            "overview": overview,
            "health": health,
            "metrics": [
                item.to_dict() for item in self.executive_metrics(overview, warning_count)
            ],
            "equity": equity,
            "workflow": workflow,
            "activity": activity,
            "insights": [item.to_dict() for item in insights],
        }

    def executive_metrics(
        self,
        overview: DashboardOverview,
        warning_count: int,
    ) -> list[ExecutiveMetric]:
        """Build executive metric cards."""
        last_report = overview.reports[0].modified_at if overview.reports else "n/a"
        return [
            ExecutiveMetric(
                "strategies",
                "عدد الاستراتيجيات",
                str(len(overview.strategies)),
                "healthy",
            ),
            ExecutiveMetric("datasets", "عدد البيانات", str(len(overview.datasets)), "healthy"),
            ExecutiveMetric(
                "validations",
                "تشغيلات التحقق",
                str(len(overview.validations)),
                "healthy",
            ),
            ExecutiveMetric("reports", "عدد التقارير", str(len(overview.reports)), "healthy"),
            ExecutiveMetric(
                "robustness",
                "آخر درجة متانة",
                self._score(overview.latest_robustness_score),
                self._score_status(overview.latest_robustness_score),
            ),
            ExecutiveMetric(
                "dataset_quality",
                "جودة البيانات",
                self._score(overview.latest_dataset_quality_score),
                self._score_status(overview.latest_dataset_quality_score),
            ),
            ExecutiveMetric(
                "warnings",
                "التحذيرات",
                str(warning_count),
                "healthy" if warning_count == 0 else "warning",
            ),
            ExecutiveMetric(
                "last_run",
                "آخر تشغيل بحثي",
                last_report,
                "healthy" if overview.reports else "warning",
            ),
        ]

    def health_status(self, overview: DashboardOverview) -> dict[str, str]:
        """Return coarse dashboard health status."""
        warning_count = sum(overview.warning_counts.values())
        robustness = overview.latest_robustness_score
        quality = overview.latest_dataset_quality_score
        if warning_count >= 3 or (robustness is not None and robustness < 40):
            status = "critical"
        elif warning_count > 0 or (quality is not None and quality < 90) or robustness is None:
            status = "warning"
        else:
            status = "healthy"
        labels = {"healthy": "سليم", "warning": "تحذير", "critical": "حرج"}
        return {"status": status, "label": labels[status]}

    def workflow(self, overview: DashboardOverview) -> list[dict[str, str]]:
        """Return visual research workflow progress."""
        steps = [
            ("dataset", "تحميل البيانات", bool(overview.datasets)),
            ("quality", "فحص الجودة", overview.latest_dataset_quality_score is not None),
            ("strategy", "تشغيل الاستراتيجية", bool(overview.strategies)),
            ("validation", "اكتمال التحقق", bool(overview.validations)),
            ("report", "توليد التقرير", bool(overview.reports)),
        ]
        return [
            {
                "key": key,
                "label": label,
                "status": "complete" if complete else "pending",
                "symbol": "✓" if complete else "…",
            }
            for key, label, complete in steps
        ]

    def recent_activity(self, overview: DashboardOverview) -> list[dict[str, str]]:
        """Return recent report activity timeline."""
        activity = []
        for report in overview.reports[:8]:
            activity.append(
                {
                    "label": self._activity_label(report.relative_path),
                    "path": report.relative_path,
                    "time": report.modified_at,
                    "report_id": report.report_id,
                }
            )
        return activity

    def _activity_label(self, relative_path: str) -> str:
        lowered = relative_path.lower()
        if "/validation/" in lowered:
            return "تشغيل تحقق"
        if "/datasets/" in lowered:
            return "فحص بيانات"
        if "/strategy_research/" in lowered:
            return "تشغيل استراتيجية"
        return "تقرير بحثي"

    def _score(self, value: float | None) -> str:
        return "n/a" if value is None else f"{value:.1f}"

    def _score_status(self, value: float | None) -> str:
        if value is None:
            return "warning"
        if value >= 70:
            return "healthy"
        if value >= 40:
            return "warning"
        return "critical"
