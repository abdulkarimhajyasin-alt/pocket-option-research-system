"""Dashboard analytics aggregation and insight generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.dashboard.charts import bar_chart, line_chart
from app.dashboard.report_loader import DashboardReportLoader
from app.reports.repository import ReportRepository


@dataclass(frozen=True)
class Insight:
    """Small deterministic research insight."""

    severity: str
    title: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable insight."""
        return {"severity": self.severity, "title": self.title, "detail": self.detail}


class DashboardAnalyticsService:
    """Build visual analytics from local research reports."""

    def __init__(
        self,
        project_root: Path | str = ".",
        reports_dir: Path | str = "reports",
        repository: ReportRepository | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.loader = repository or DashboardReportLoader(self.project_root, reports_dir)

    def equity_analytics(self) -> dict[str, Any]:
        """Return equity, balance, performance, and drawdown chart data."""
        rows = self._latest_json_list("analytics", "equity")
        labels = [self._short_time(row.get("timestamp")) for row in rows]
        equity = [self._float(row.get("equity")) for row in rows]
        performance = [self._float(row.get("cumulative_pnl")) for row in rows]
        drawdown = [self._float(row.get("drawdown")) for row in rows]
        balance = self._balance_curve(equity)
        max_drawdown = max(drawdown) if drawdown else 0.0
        current_drawdown = drawdown[-1] if drawdown else 0.0
        worst_index = drawdown.index(max_drawdown) if drawdown else -1
        return {
            "equity": line_chart("منحنى رأس المال", labels, equity, label="Equity").to_dict(),
            "balance": line_chart("منحنى الرصيد", labels, balance, label="Balance").to_dict(),
            "performance": line_chart(
                "الأداء التراكمي",
                labels,
                performance,
                label="Cumulative PnL",
                color="blue",
            ).to_dict(),
            "drawdown": line_chart(
                "منحنى التراجع",
                labels,
                drawdown,
                label="Drawdown",
                color="warning",
            ).to_dict(),
            "summary": {
                "max_drawdown": max_drawdown,
                "current_drawdown": current_drawdown,
                "worst_period": labels[worst_index] if worst_index >= 0 else None,
                "recovery_periods": self._count_recoveries(drawdown),
            },
        }

    def signal_analytics(self) -> dict[str, Any]:
        """Return signal distribution and confidence/session charts."""
        summary = self._latest_json_dict("strategy_research", "summary")
        generated = int(summary.get("generated_signals") or summary.get("total_signals") or 0)
        bullish = int(summary.get("bullish_signals") or summary.get("long_signals") or 0)
        bearish = int(summary.get("bearish_signals") or summary.get("short_signals") or 0)
        rejected = int(summary.get("decision_distribution", {}).get("rejected") or 0)
        confidence_by_evidence = summary.get("average_confidence_by_evidence", {})
        session_quality = summary.get("session_quality", {})
        session_labels = []
        session_values = []
        if isinstance(session_quality, dict):
            for name, payload in session_quality.items():
                if isinstance(payload, dict):
                    session_labels.append(str(name))
                    session_values.append(self._float(payload.get("signals")))
        confidence_labels, confidence_values = self._dict_chart_values(confidence_by_evidence)
        return {
            "total_signals": generated,
            "long_signals": bullish,
            "short_signals": bearish,
            "rejected_decisions": rejected,
            "distribution": bar_chart(
                "توزيع الإشارات",
                ["صاعدة", "هابطة", "مرفوضة"],
                [bullish, bearish, rejected],
                label="Signals",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                confidence_labels,
                confidence_values,
                label="Confidence",
                color="blue",
            ).to_dict(),
            "sessions": bar_chart(
                "توزيع الجلسات",
                session_labels,
                session_values,
                label="Signals",
                color="green",
            ).to_dict(),
        }

    def validation_analytics(self) -> dict[str, Any]:
        """Return validation charts from validation reports."""
        reports = [
            item
            for item in self.loader.list_reports()
            if item.report_type == "json" and "/validation/" in item.relative_path
        ]
        scores = []
        labels = []
        walk_forward_windows = []
        sweep_counts = []
        out_of_sample = []
        for report in reversed(reports):
            content = self.loader.get_report(report.report_id)
            payload = content.json_data if content else {}
            if not isinstance(payload, dict):
                continue
            labels.append(self._short_time(report.modified_at))
            robustness = payload.get("robustness", {})
            results = payload.get("validation_results", {})
            score = robustness.get("score") if isinstance(robustness, dict) else None
            scores.append(self._float(score))
            walk_forward = results.get("walk_forward", {}) if isinstance(results, dict) else {}
            parameter_sweep = (
                results.get("parameter_sweep", {}) if isinstance(results, dict) else {}
            )
            out_sample = results.get("out_of_sample", {}) if isinstance(results, dict) else {}
            walk_forward_windows.append(float(len(walk_forward.get("windows", []))))
            sweep_counts.append(float(len(parameter_sweep.get("results", []))))
            out_of_sample.append(self._float(out_sample.get("stability_score")))
        latest = self._latest_json_dict("validation", "report")
        components = latest.get("robustness", {}).get("components", {}) if latest else {}
        component_labels, component_values = self._dict_chart_values(components)
        return {
            "history": line_chart(
                "اتجاه التحقق",
                labels,
                scores,
                label="Robustness",
            ).to_dict(),
            "windows": bar_chart(
                "نوافذ Walk-forward",
                labels,
                walk_forward_windows,
                label="Windows",
            ).to_dict(),
            "parameter_sweep": bar_chart(
                "توزيع فحص المعاملات",
                labels,
                sweep_counts,
                label="Runs",
                color="blue",
            ).to_dict(),
            "out_of_sample": line_chart(
                "نتائج خارج العينة",
                labels,
                out_of_sample,
                label="Stability",
                color="green",
            ).to_dict(),
            "components": bar_chart(
                "مكونات المتانة",
                component_labels,
                component_values,
                label="Score",
                color="warning",
            ).to_dict(),
        }

    def dataset_analytics(self) -> dict[str, Any]:
        """Return dataset coverage and quality visualization data."""
        latest = self._latest_json_dict("datasets")
        quality = latest.get("quality", {}) if latest else {}
        metadata = latest.get("metadata", {}) if latest else {}
        statistics = latest.get("statistics", {}) if latest else {}
        components = quality.get("components", {}) if isinstance(quality, dict) else {}
        component_labels, component_values = self._dict_chart_values(components)
        gaps = quality.get("gaps", []) if isinstance(quality, dict) else []
        return {
            "quality": bar_chart(
                "مكونات جودة البيانات",
                component_labels,
                component_values,
                label="Quality",
                color="green",
            ).to_dict(),
            "gaps": bar_chart(
                "توزيع الفجوات",
                [
                    "الفجوات",
                    "التكرارات",
                    "الشموع",
                ],
                [
                    float(len(gaps)),
                    self._float(statistics.get("duplicate_count")),
                    self._float(metadata.get("row_count") or statistics.get("row_count")),
                ],
                label="Dataset",
                color="warning",
            ).to_dict(),
            "summary": {
                "start_time": metadata.get("start_time") or statistics.get("start_time"),
                "end_time": metadata.get("end_time") or statistics.get("end_time"),
                "row_count": metadata.get("row_count") or statistics.get("row_count") or 0,
                "quality_score": quality.get("quality_score") or statistics.get("quality_score"),
                "gap_count": len(gaps),
                "integrity_passed": (
                    bool(latest.get("integrity", {}).get("passed")) if latest else False
                ),
            },
        }

    def report_visualization(self, payload: Any) -> dict[str, Any]:
        """Build generic cards and charts for a JSON report."""
        if not isinstance(payload, dict):
            return {"cards": [], "charts": []}
        cards = []
        charts = []
        for key, value in payload.items():
            if isinstance(value, (int, float, str, bool)) or value is None:
                cards.append({"label": key, "value": value})
            elif isinstance(value, dict):
                labels, values = self._dict_chart_values(value)
                if values:
                    charts.append(
                        bar_chart(str(key), labels, values, label=str(key)).to_dict()
                    )
        return {"cards": cards[:8], "charts": charts[:4]}

    def build_insights(
        self,
        robustness_score: float | None,
        dataset_quality_score: float | None,
        warning_count: int,
    ) -> list[Insight]:
        """Generate deterministic research insights without external AI."""
        insights = []
        if robustness_score is None:
            insights.append(
                Insight("warning", "المتانة غير متاحة", "لم يتم العثور على تقرير تحقق.")
            )
        elif robustness_score >= 70:
            insights.append(
                Insight("healthy", "المتانة قوية", f"آخر درجة متانة {robustness_score:.1f}.")
            )
        else:
            insights.append(
                Insight(
                    "warning",
                    "المتانة تحتاج مراجعة",
                    f"آخر درجة متانة {robustness_score:.1f}.",
                )
            )
        if dataset_quality_score is not None and dataset_quality_score >= 95:
            insights.append(
                Insight("healthy", "جودة البيانات مستقرة", "درجة الجودة الحالية مرتفعة.")
            )
        elif dataset_quality_score is not None:
            insights.append(
                Insight("warning", "جودة البيانات منخفضة", "راجع الفجوات والتكرارات.")
            )
        if warning_count > 0:
            insights.append(
                Insight("warning", "توجد تحذيرات", f"عدد التحذيرات الحالي {warning_count}.")
            )
        if not insights:
            insights.append(
                Insight("healthy", "البحث مستقر", "لا توجد إشارات خطر في التقارير الحالية.")
            )
        return insights

    def _latest_json_dict(self, *parts: str) -> dict[str, Any]:
        reports = self.loader.list_reports()
        return self.loader.latest_json(reports, *parts)

    def _latest_json_list(self, *parts: str) -> list[dict[str, Any]]:
        reports = self.loader.list_reports()
        report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            *parts,
        )
        if report is None:
            return []
        content = self.loader.get_report(report.report_id)
        if not content or not isinstance(content.json_data, list):
            return []
        return [item for item in content.json_data if isinstance(item, dict)]

    def _dict_chart_values(self, payload: Any) -> tuple[list[str], list[float]]:
        if not isinstance(payload, dict):
            return [], []
        labels = []
        values = []
        for key, value in payload.items():
            if isinstance(value, (int, float)):
                labels.append(str(key))
                values.append(float(value))
        return labels, values

    def _balance_curve(self, equity: list[float]) -> list[float]:
        balance = []
        peak = 0.0
        for value in equity:
            peak = max(peak, value)
            balance.append(peak)
        return balance

    def _count_recoveries(self, drawdown: list[float]) -> int:
        recoveries = 0
        in_drawdown = False
        for value in drawdown:
            if value > 0:
                in_drawdown = True
            elif in_drawdown:
                recoveries += 1
                in_drawdown = False
        return recoveries

    def _short_time(self, value: Any) -> str:
        text = str(value or "")
        if "T" in text:
            return text.split("T", 1)[1][:5] or text[:10]
        return text[:10]

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
