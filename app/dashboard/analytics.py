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

    def execution_analytics(self) -> dict[str, Any]:
        """Return latest execution simulation analytics."""
        analytics = self._latest_json_dict("execution", "analytics")
        summary = self._latest_json_dict("execution", "summary")
        if not analytics:
            analytics = {
                "total_trades": 0,
                "executed_trades": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "blocked_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "profit_loss": 0.0,
                "expectancy": 0.0,
                "average_return": 0.0,
                "average_confidence": 0.0,
                "blocked_by_rule": {},
                "confidence_distribution": {},
            }
        blocked_labels, blocked_values = self._dict_chart_values(
            analytics.get("blocked_by_rule", {})
        )
        confidence_labels, confidence_values = self._dict_chart_values(
            analytics.get("confidence_distribution", {})
        )
        return {
            "summary": {**summary, **analytics},
            "outcomes": bar_chart(
                "نتائج التنفيذ",
                ["رابحة", "خاسرة", "تعادل"],
                [
                    self._float(analytics.get("wins")),
                    self._float(analytics.get("losses")),
                    self._float(analytics.get("draws")),
                ],
                label="Outcomes",
                color="green",
            ).to_dict(),
            "blocked": bar_chart(
                "الصفقات الممنوعة",
                blocked_labels,
                blocked_values,
                label="Blocked",
                color="warning",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                confidence_labels,
                confidence_values,
                label="Confidence",
                color="blue",
            ).to_dict(),
        }

    def observation_analytics(self) -> dict[str, Any]:
        """Return latest broker observation analytics."""
        summary = self._latest_json_dict("observation", "summary")
        asset_activity = self._latest_json_dict("observation", "asset_activity")
        payout_distribution = self._latest_json_dict(
            "observation",
            "payout_distribution",
        )
        session_activity = self._latest_json_dict("observation", "session_activity")
        if not summary:
            summary = {
                "timestamp": None,
                "source": None,
                "active_assets": 0,
                "average_payout": 0.0,
                "market_activity_score": 0.0,
                "observation_count": 0,
                "assessment": {
                    "activity": "نشاط منخفض",
                    "readiness": "بيانات غير كافية",
                    "severity": "warning",
                },
            }
        if not isinstance(summary.get("assessment"), dict):
            summary["assessment"] = {
                "activity": "نشاط غير متاح",
                "readiness": "بيانات غير كافية",
                "severity": "warning",
            }
        if not asset_activity:
            asset_activity = summary.get("asset_activity", {})
        if not payout_distribution:
            payout_distribution = summary.get("payout_distribution", {})
        if not session_activity:
            session_activity = summary.get("session_activity", {})
        active_sessions = (
            sum(1 for value in session_activity.values() if self._float(value) >= 60)
            if isinstance(session_activity, dict)
            else 0
        )
        summary = {**summary, "active_sessions": active_sessions}
        asset_labels, asset_values = self._dict_chart_values(asset_activity)
        payout_labels, payout_values = self._dict_chart_values(payout_distribution)
        session_labels, session_values = self._dict_chart_values(session_activity)
        return {
            "summary": summary,
            "asset_activity": bar_chart(
                "مراقبة الأصول",
                asset_labels,
                asset_values,
                label="الأصول",
                color="green",
            ).to_dict(),
            "payout_distribution": bar_chart(
                "توزيع العوائد",
                payout_labels,
                payout_values,
                label="العوائد",
                color="blue",
            ).to_dict(),
            "session_activity": bar_chart(
                "نشاط الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="warning",
            ).to_dict(),
        }

    def live_feed_analytics(self) -> dict[str, Any]:
        """Return latest live-feed analytics."""
        summary = self._latest_json_dict("live_feed", "summary")
        health = self._latest_json_dict("live_feed", "health")
        activity_payload = self._latest_json_dict("live_feed", "activity")
        latency_rows = self._latest_json_list("live_feed", "latency")
        if not summary:
            summary = {
                "timestamp": None,
                "update_count": 0,
                "update_frequency": 0.0,
                "average_latency_ms": 0.0,
                "active_assets": 0,
                "stream_uptime_seconds": 0.0,
                "missing_updates": 0,
                "health_score": 0.0,
                "health_label": "ضعيف",
                "readiness": "غير مستقر",
            }
        severity = "healthy" if self._float(summary.get("health_score")) >= 75 else "warning"
        summary = {**summary, "severity": severity}
        activity = activity_payload.get("activity", {}) if activity_payload else {}
        frequency = activity_payload.get("frequency", {}) if activity_payload else {}
        session_activity = activity_payload.get("session_activity", {}) if activity_payload else {}
        health_timeline = activity_payload.get("health_timeline", {}) if activity_payload else {}
        latency_labels = [self._short_time(row.get("timestamp")) for row in latency_rows]
        latency_values = [self._float(row.get("latency_ms")) for row in latency_rows]
        activity_labels, activity_values = self._dict_chart_values(activity)
        frequency_labels, frequency_values = self._dict_chart_values(frequency)
        session_labels, session_values = self._dict_chart_values(session_activity)
        health_labels, health_values = self._dict_chart_values(health_timeline)
        return {
            "summary": {**health, **summary},
            "frequency": bar_chart(
                "معدل التحديث",
                frequency_labels,
                frequency_values,
                label="التحديثات",
                color="green",
            ).to_dict(),
            "latency": line_chart(
                "زمن الاستجابة",
                latency_labels,
                latency_values,
                label="التأخير",
                color="blue",
            ).to_dict(),
            "activity": bar_chart(
                "الأصول النشطة",
                activity_labels,
                activity_values,
                label="الأصول",
                color="accent",
            ).to_dict(),
            "health_timeline": line_chart(
                "صحة البث",
                health_labels,
                health_values,
                label="الصحة",
                color="warning",
            ).to_dict(),
            "session_activity": bar_chart(
                "نشاط الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="green",
            ).to_dict(),
        }

    def market_data_analytics(self) -> dict[str, Any]:
        """Return latest market data integration analytics."""
        summary = self._latest_json_dict("market_data", "summary")
        quality_payload = self._latest_json_dict("market_data", "quality")
        assets_rows = self._latest_json_list("market_data", "assets")
        sessions_rows = self._latest_json_list("market_data", "sessions")
        if not summary:
            summary = {
                "timestamp": None,
                "provider": None,
                "asset_count": 0,
                "active_assets": 0,
                "market_status": "غير متاح",
                "feed_quality_score": 0.0,
                "provider_health": "ضعيف",
                "average_latency_ms": 0.0,
                "update_frequency": 0.0,
                "readiness_score": 0.0,
                "readiness_label": "غير جاهز",
            }
        severity = "healthy" if self._float(summary.get("readiness_score")) >= 70 else "warning"
        summary = {**summary, "severity": severity}
        asset_quality = quality_payload.get("asset_quality", {}) if quality_payload else {}
        feed_quality = quality_payload.get("feed_quality", {}) if quality_payload else {}
        market_status = quality_payload.get("market_status", {}) if quality_payload else {}
        session_activity = quality_payload.get("session_activity", {}) if quality_payload else {}
        time_activity = quality_payload.get("time_activity", {}) if quality_payload else {}
        if not asset_quality:
            asset_quality = {
                row.get("asset", ""): self._float(row.get("quality_score")) for row in assets_rows
            }
        if not session_activity:
            session_activity = {
                row.get("name", ""): self._float(row.get("activity_score")) for row in sessions_rows
            }
        asset_labels, asset_values = self._dict_chart_values(asset_quality)
        session_labels, session_values = self._dict_chart_values(session_activity)
        quality_labels, quality_values = self._dict_chart_values(feed_quality)
        status_labels, status_values = self._dict_chart_values(market_status)
        time_labels, time_values = self._dict_chart_values(time_activity)
        return {
            "summary": summary,
            "assets": bar_chart(
                "توزيع الأصول",
                asset_labels,
                asset_values,
                label="الأصول",
                color="green",
            ).to_dict(),
            "sessions": bar_chart(
                "نشاط الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="warning",
            ).to_dict(),
            "quality": bar_chart(
                "جودة البيانات",
                quality_labels,
                quality_values,
                label="الجودة",
                color="blue",
            ).to_dict(),
            "status": bar_chart(
                "صحة السوق",
                status_labels,
                status_values,
                label="الحالة",
                color="accent",
            ).to_dict(),
            "time_activity": line_chart(
                "النشاط الزمني",
                time_labels,
                time_values,
                label="النشاط",
                color="green",
            ).to_dict(),
        }

    def signals_intelligence_analytics(self) -> dict[str, Any]:
        """Return latest signal intelligence analytics."""
        summary = self._latest_json_dict("signals", "summary")
        distribution = self._latest_json_dict("signals", "distribution")
        confidence = self._latest_json_dict("signals", "confidence")
        structure = self._latest_json_dict("signals", "structure")
        fvg = self._latest_json_dict("signals", "fvg")
        cisd = self._latest_json_dict("signals", "cisd")
        liquidity = self._latest_json_dict("signals", "liquidity")
        quality = self._latest_json_dict("signals", "quality")
        if not summary:
            summary = {
                "signal_count": 0,
                "average_confidence": 0.0,
                "highest_confidence": 0.0,
                "signal_quality": "غير متاح",
            }
        latest = self._latest_json_list("signals", "latest")
        best = self._best_signal(latest) or summary.get("best_signal", {})
        distribution_labels, distribution_values = self._dict_chart_values(distribution)
        structure_labels, structure_values = self._dict_chart_values(structure)
        cisd_labels, cisd_values = self._dict_chart_values(cisd)
        fvg_labels, fvg_values = self._dict_chart_values(fvg)
        liquidity_labels, liquidity_values = self._dict_chart_values(liquidity)
        sessions = quality.get("session_performance", {}) if quality else {}
        session_labels, session_values = self._dict_chart_values(sessions)
        confidence_labels, confidence_values = self._dict_chart_values(confidence)
        return {
            "summary": summary,
            "best": best,
            "distribution": bar_chart(
                "توزيع الإشارات",
                distribution_labels,
                distribution_values,
                label="الإشارات",
                color="green",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                confidence_labels,
                confidence_values,
                label="الثقة",
                color="blue",
            ).to_dict(),
            "structure": bar_chart(
                "توزيع الهيكل السعري",
                structure_labels,
                structure_values,
                label="الهيكل",
                color="warning",
            ).to_dict(),
            "cisd": bar_chart(
                "توزيع CISD",
                cisd_labels,
                cisd_values,
                label="CISD",
                color="accent",
            ).to_dict(),
            "fvg": bar_chart(
                "توزيع FVG",
                fvg_labels,
                fvg_values,
                label="FVG",
                color="green",
            ).to_dict(),
            "liquidity": bar_chart(
                "توزيع السيولة",
                liquidity_labels,
                liquidity_values,
                label="السيولة",
                color="blue",
            ).to_dict(),
            "sessions": bar_chart(
                "جودة الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="warning",
            ).to_dict(),
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
                    charts.append(bar_chart(str(key), labels, values, label=str(key)).to_dict())
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
            insights.append(Insight("warning", "جودة البيانات منخفضة", "راجع الفجوات والتكرارات."))
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

    def _trend_score(self, value: Any) -> float:
        mapping = {
            "يتحسن": 100.0,
            "مستقر": 60.0,
            "يتراجع": 20.0,
            "غير كاف للتقييم": 0.0,
        }
        return mapping.get(str(value), 0.0)

    def _status_score(self, value: Any) -> float:
        mapping = {"PASS": 100.0, "WARNING": 60.0, "FAIL": 0.0}
        return mapping.get(str(value), self._float(value))

    def _best_signal(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {}
        return max(rows, key=lambda row: self._float(row.get("confidence", {}).get("score")))

    def signal_performance_analytics(self) -> dict[str, Any]:
        """Return latest signal performance analytics."""
        summary = self._latest_json_dict("signal_performance", "summary")
        outcomes = self._latest_json_dict("signal_performance", "win_rate")
        assets = self._latest_json_dict("signal_performance", "assets")
        sessions = self._latest_json_dict("signal_performance", "sessions")
        confidence_payload = self._latest_json_dict("signal_performance", "confidence")
        structure = self._latest_json_dict("signal_performance", "structure")
        quality = self._latest_json_dict("signal_performance", "quality")
        timeline = self._latest_json_dict("signal_performance", "stability")
        if not summary:
            summary = {
                "total_signals": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "unresolved": 0,
                "win_rate": 0.0,
                "average_confidence": 0.0,
                "best_asset": "غير متاح",
                "worst_asset": "غير متاح",
                "best_session": "غير متاح",
                "worst_session": "غير متاح",
                "validation_readiness_score": 0.0,
                "readiness_label": "غير متاح",
            }
        summary = {**summary, **quality}
        confidence = confidence_payload.get("buckets", {}) if confidence_payload else {}
        confidence_rates = {
            key: self._float(value.get("win_rate")) if isinstance(value, dict) else 0.0
            for key, value in confidence.items()
        }
        outcome_labels, outcome_values = self._dict_chart_values(outcomes)
        asset_labels, asset_values = self._dict_chart_values(assets)
        session_labels, session_values = self._dict_chart_values(sessions)
        confidence_labels, confidence_values = self._dict_chart_values(confidence_rates)
        structure_labels, structure_values = self._dict_chart_values(structure)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "outcomes": bar_chart(
                "توزيع النتائج",
                outcome_labels,
                outcome_values,
                label="النتائج",
                color="green",
            ).to_dict(),
            "win_rate": bar_chart(
                "نسبة النجاح",
                ["نسبة النجاح", "نسبة الخسارة"],
                [
                    self._float(summary.get("win_rate")) * 100,
                    self._float(summary.get("loss_rate")) * 100,
                ],
                label="النسبة",
                color="blue",
            ).to_dict(),
            "assets": bar_chart(
                "أداء الأصول",
                asset_labels,
                asset_values,
                label="الأصول",
                color="accent",
            ).to_dict(),
            "sessions": bar_chart(
                "أداء الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="warning",
            ).to_dict(),
            "confidence": bar_chart(
                "أداء مستويات الثقة",
                confidence_labels,
                confidence_values,
                label="الثقة",
                color="green",
            ).to_dict(),
            "structure": bar_chart(
                "أداء الهيكل السعري",
                structure_labels,
                structure_values,
                label="الهيكل",
                color="blue",
            ).to_dict(),
            "timeline": line_chart(
                "تطور الأداء الزمني",
                timeline_labels,
                timeline_values,
                label="التقييمات",
                color="warning",
            ).to_dict(),
        }

    def opportunities_analytics(self) -> dict[str, Any]:
        """Return latest opportunity qualification analytics."""
        summary = self._latest_json_dict("opportunities", "summary")
        rankings = self._latest_json_list("opportunities", "rankings")
        qualification = self._latest_json_dict("opportunities", "qualification")
        assets = self._latest_json_dict("opportunities", "assets")
        sessions = self._latest_json_dict("opportunities", "sessions")
        structures = self._latest_json_dict("opportunities", "structures")
        rejections = self._latest_json_dict("opportunities", "rejections")
        ranked_opportunities = [
            row.get("opportunity", {})
            for row in rankings
            if isinstance(row.get("opportunity"), dict)
        ]
        if not summary:
            summary = {
                "opportunity_count": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "average_confidence": 0.0,
                "highly_qualified_count": 0,
                "rejected_count": 0,
            }
        best = rankings[0] if rankings else {"opportunity": {}}
        fvg = self._fvg_from_opportunities(ranked_opportunities)
        timeline = self._timeline_from_opportunities(ranked_opportunities)
        qualification_labels, qualification_values = self._dict_chart_values(qualification)
        asset_labels, asset_values = self._dict_chart_values(assets)
        session_labels, session_values = self._dict_chart_values(sessions)
        structure_labels, structure_values = self._dict_chart_values(structures)
        fvg_labels, fvg_values = self._dict_chart_values(fvg)
        rejection_labels, rejection_values = self._dict_chart_values(rejections)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "best": best,
            "qualification": bar_chart(
                "توزيع حالات التأهيل",
                qualification_labels,
                qualification_values,
                label="الحالات",
                color="green",
            ).to_dict(),
            "assets": bar_chart(
                "أفضل الأصول",
                asset_labels,
                asset_values,
                label="الأصول",
                color="blue",
            ).to_dict(),
            "sessions": bar_chart(
                "أفضل الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="warning",
            ).to_dict(),
            "structures": bar_chart(
                "أفضل الهياكل",
                structure_labels,
                structure_values,
                label="الهياكل",
                color="accent",
            ).to_dict(),
            "fvg": bar_chart(
                "أفضل أنواع FVG",
                fvg_labels,
                fvg_values,
                label="FVG",
                color="green",
            ).to_dict(),
            "rejections": bar_chart(
                "أسباب الرفض",
                rejection_labels,
                rejection_values,
                label="الأسباب",
                color="warning",
            ).to_dict(),
            "timeline": line_chart(
                "جودة الفرص بمرور الوقت",
                timeline_labels,
                timeline_values,
                label="الجودة",
                color="blue",
            ).to_dict(),
        }

    def multi_timeframe_analytics(self) -> dict[str, Any]:
        """Return latest multi-timeframe confirmation analytics."""
        alignment_payload = self._latest_json_dict("multi_timeframe", "alignment")
        if "summary" not in alignment_payload:
            alignment_payload = self._latest_json_dict(
                "multi_timeframe",
                "alignment_summary",
            )
        summary = alignment_payload.get("summary", {}) if alignment_payload else {}
        alignment = alignment_payload.get("distribution", {}) if alignment_payload else {}
        confirmation = self._latest_json_dict("multi_timeframe", "confirmation")
        if isinstance(confirmation.get("distribution"), dict):
            confirmation = confirmation["distribution"]
        conflicts = self._latest_json_dict("multi_timeframe", "conflicts")
        assets = self._latest_json_dict("multi_timeframe", "assets")
        sessions = self._latest_json_dict("multi_timeframe", "sessions")
        timeframes = self._latest_json_dict("multi_timeframe", "timeframes")
        latest = alignment_payload.get("latest", []) if alignment_payload else []
        if not isinstance(latest, list):
            latest = self._latest_json_list("multi_timeframe", "confirmation_results")
        if not summary:
            summary = {
                "confirmed_count": 0,
                "conflicting_count": 0,
                "average_alignment": 0.0,
                "highest_alignment": 0.0,
                "lowest_alignment": 0.0,
            }
        best = alignment_payload.get("best_confirmation", {}) if alignment_payload else {}
        if not best:
            best = self._best_confirmation(latest)
        states = self._state_map(best)
        timeline = alignment_payload.get("timeline", {}) if alignment_payload else {}
        if not timeline:
            timeline = self._timeline_from_confirmations(latest)
        alignment_labels, alignment_values = self._dict_chart_values(alignment)
        confirmation_labels, confirmation_values = self._dict_chart_values(confirmation)
        conflict_labels, conflict_values = self._dict_chart_values(conflicts)
        asset_labels, asset_values = self._dict_chart_values(assets)
        session_labels, session_values = self._dict_chart_values(sessions)
        timeframe_labels, timeframe_values = self._dict_chart_values(timeframes)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "best": best,
            "states": states,
            "alignment": bar_chart(
                "توزيع التوافق",
                alignment_labels,
                alignment_values,
                label="التوافق",
                color="green",
            ).to_dict(),
            "confirmation": bar_chart(
                "توزيع التأكيد",
                confirmation_labels,
                confirmation_values,
                label="التأكيد",
                color="blue",
            ).to_dict(),
            "conflicts": bar_chart(
                "حالات التعارض",
                conflict_labels,
                conflict_values,
                label="التعارض",
                color="warning",
            ).to_dict(),
            "assets": bar_chart(
                "أفضل الأصول توافقا",
                asset_labels,
                asset_values,
                label="الأصول",
                color="accent",
            ).to_dict(),
            "sessions": bar_chart(
                "توافق الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="green",
            ).to_dict(),
            "timeframes": bar_chart(
                "توافق الأطر الزمنية",
                timeframe_labels,
                timeframe_values,
                label="الأطر",
                color="blue",
            ).to_dict(),
            "timeline": line_chart(
                "تطور التوافق الزمني",
                timeline_labels,
                timeline_values,
                label="التوافق",
                color="warning",
            ).to_dict(),
        }

    def confluence_analytics(self) -> dict[str, Any]:
        """Return latest confluence research analytics."""
        summary_payload = self._latest_json_dict("confluence", "summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        distribution = summary_payload.get("distribution", {}) if summary_payload else {}
        quality = summary_payload.get("quality", {}) if summary_payload else {}
        timeline = summary_payload.get("timeline", {}) if summary_payload else {}
        best = summary_payload.get("best_decision", {}) if summary_payload else {}
        factors = self._latest_json_dict("confluence", "factor")
        assets = self._latest_json_dict("confluence", "asset")
        sessions = self._latest_json_dict("confluence", "session")
        timeframes = self._latest_json_dict("confluence", "timeframe")
        rejections = self._latest_json_dict("confluence", "rejection")
        if not summary:
            summary = {
                "confluent_count": 0,
                "average_confluence": 0.0,
                "highest_confluence": 0.0,
                "lowest_confluence": 0.0,
                "strong_count": 0,
                "rejected_count": 0,
            }
        factor_labels, factor_values = self._dict_chart_values(factors)
        quality_labels, quality_values = self._dict_chart_values(quality)
        distribution_labels, distribution_values = self._dict_chart_values(distribution)
        asset_labels, asset_values = self._dict_chart_values(assets)
        session_labels, session_values = self._dict_chart_values(sessions)
        timeframe_labels, timeframe_values = self._dict_chart_values(timeframes)
        rejection_labels, rejection_values = self._dict_chart_values(rejections)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "best": best,
            "distribution": bar_chart(
                "توزيع درجات التوافق",
                distribution_labels,
                distribution_values,
                label="التوافق",
                color="green",
            ).to_dict(),
            "factors": bar_chart(
                "عوامل التوافق",
                factor_labels,
                factor_values,
                label="العوامل",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "أداء التوافق",
                quality_labels,
                quality_values,
                label="الجودة",
                color="accent",
            ).to_dict(),
            "states": bar_chart(
                "توزيع الحالات",
                distribution_labels,
                distribution_values,
                label="الحالات",
                color="warning",
            ).to_dict(),
            "assets": bar_chart(
                "التوافق حسب الأصل",
                asset_labels,
                asset_values,
                label="الأصول",
                color="green",
            ).to_dict(),
            "sessions": bar_chart(
                "التوافق حسب الجلسة",
                session_labels,
                session_values,
                label="الجلسات",
                color="blue",
            ).to_dict(),
            "timeframes": bar_chart(
                "التوافق حسب الإطار الزمني",
                timeframe_labels,
                timeframe_values,
                label="الأطر",
                color="accent",
            ).to_dict(),
            "rejections": bar_chart(
                "أسباب الرفض",
                rejection_labels,
                rejection_values,
                label="الأسباب",
                color="warning",
            ).to_dict(),
            "timeline": line_chart(
                "تطور التوافق بمرور الوقت",
                timeline_labels,
                timeline_values,
                label="التوافق",
                color="green",
            ).to_dict(),
        }

    def trade_lifecycle_analytics(self) -> dict[str, Any]:
        """Return latest trade lifecycle research analytics."""
        summary_payload = self._latest_json_dict("trade_lifecycle", "summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        states = summary_payload.get("state_distribution", {}) if summary_payload else {}
        timeline = summary_payload.get("timeline", {}) if summary_payload else {}
        best = summary_payload.get("best_lifecycle", {}) if summary_payload else {}
        outcomes = self._latest_json_dict("trade_lifecycle", "outcome")
        quality = self._latest_json_dict("trade_lifecycle", "quality")
        success = self._latest_json_dict("trade_lifecycle", "success")
        failure = self._latest_json_dict("trade_lifecycle", "failure")
        assets = self._latest_json_dict("trade_lifecycle", "asset")
        sessions = self._latest_json_dict("trade_lifecycle", "session")
        confluence = self._latest_json_dict("trade_lifecycle", "confluence")
        confidence = self._latest_json_dict("trade_lifecycle", "confidence")
        if not confidence:
            confidence = quality
        if not summary:
            summary = {
                "total_lifecycles": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "average_quality": 0.0,
                "best_asset": "غير متاح",
                "best_session": "غير متاح",
            }
        outcome_labels, outcome_values = self._dict_chart_values(outcomes)
        state_labels, state_values = self._dict_chart_values(states)
        entry = self._entry_quality(best)
        expiry = self._expiry_quality(best)
        entry_labels, entry_values = self._dict_chart_values(entry)
        expiry_labels, expiry_values = self._dict_chart_values(expiry)
        asset_labels, asset_values = self._dict_chart_values(assets)
        session_labels, session_values = self._dict_chart_values(sessions)
        confluence_labels, confluence_values = self._dict_chart_values(confluence)
        confidence_labels, confidence_values = self._dict_chart_values(confidence)
        failure_labels, failure_values = self._dict_chart_values(failure)
        success_labels, success_values = self._dict_chart_values(success)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "best": best,
            "outcomes": bar_chart(
                "توزيع النتائج",
                outcome_labels,
                outcome_values,
                label="النتائج",
                color="green",
            ).to_dict(),
            "states": bar_chart(
                "توزيع الحالات",
                state_labels,
                state_values,
                label="الحالات",
                color="blue",
            ).to_dict(),
            "entry": bar_chart(
                "جودة الدخول",
                entry_labels,
                entry_values,
                label="الدخول",
                color="accent",
            ).to_dict(),
            "expiry": bar_chart(
                "جودة الانتهاء",
                expiry_labels,
                expiry_values,
                label="الانتهاء",
                color="warning",
            ).to_dict(),
            "assets": bar_chart(
                "أداء الأصول",
                asset_labels,
                asset_values,
                label="الأصول",
                color="green",
            ).to_dict(),
            "sessions": bar_chart(
                "أداء الجلسات",
                session_labels,
                session_values,
                label="الجلسات",
                color="blue",
            ).to_dict(),
            "confluence": bar_chart(
                "أداء التوافق",
                confluence_labels,
                confluence_values,
                label="التوافق",
                color="accent",
            ).to_dict(),
            "confidence": bar_chart(
                "أداء الثقة",
                confidence_labels,
                confidence_values,
                label="الثقة",
                color="green",
            ).to_dict(),
            "failure": bar_chart(
                "أسباب الفشل",
                failure_labels,
                failure_values,
                label="الفشل",
                color="warning",
            ).to_dict(),
            "success": bar_chart(
                "أسباب النجاح",
                success_labels,
                success_values,
                label="النجاح",
                color="blue",
            ).to_dict(),
            "timeline": line_chart(
                "تطور الجودة بمرور الوقت",
                timeline_labels,
                timeline_values,
                label="الجودة",
                color="green",
            ).to_dict(),
        }

    def _entry_quality(self, row: dict[str, Any]) -> dict[str, float]:
        entry = row.get("entry", {}) if isinstance(row, dict) else {}
        return {
            "توقيت الدخول": self._float(entry.get("timing_quality")),
            "جودة التأكيد": self._float(entry.get("confirmation_quality")),
            "توافق الدخول": self._float(entry.get("entry_alignment")),
            "جاهزية الدخول": self._float(entry.get("readiness_score")),
        }

    def _expiry_quality(self, row: dict[str, Any]) -> dict[str, float]:
        expiry = row.get("expiry", {}) if isinstance(row, dict) else {}
        return {
            "ملاءمة الانتهاء": self._float(expiry.get("suitability")),
            "حساسية النتيجة": self._float(expiry.get("outcome_sensitivity")),
            "جودة الانتهاء": self._float(expiry.get("expiry_quality")),
        }

    def strategy_readiness_analytics(self) -> dict[str, Any]:
        """Return latest strategy readiness analytics."""
        summary_payload = self._latest_json_dict("strategy_readiness", "summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        readiness = summary_payload.get("readiness_distribution", {}) if summary_payload else {}
        strengths = summary_payload.get("strengths", {}) if summary_payload else {}
        weaknesses = summary_payload.get("weaknesses", {}) if summary_payload else {}
        timeline = summary_payload.get("timeline", {}) if summary_payload else {}
        latest = summary_payload.get("latest", {}) if summary_payload else {}
        gates = self._latest_json_dict("strategy_readiness", "gate")
        diagnostics = self._latest_json_dict("strategy_readiness", "diagnostics")
        recommendations = self._latest_json_dict(
            "strategy_readiness",
            "recommendations",
        )
        stability = self._latest_json_dict("strategy_readiness", "stability")
        failures = self._latest_json_dict("strategy_readiness", "failure")
        if not summary:
            summary = {
                "readiness_score": 0.0,
                "readiness_state": "غير متاح",
                "passed_gates": 0,
                "warnings": 0,
                "failures": 0,
                "stability_score": 0.0,
                "recommendation_count": 0,
            }
        gate_labels, gate_values = self._dict_chart_values(gates)
        readiness_labels, readiness_values = self._dict_chart_values(readiness)
        stability_labels, stability_values = self._dict_chart_values(stability)
        strength_labels, strength_values = self._dict_chart_values(strengths)
        weakness_labels, weakness_values = self._dict_chart_values(weaknesses)
        failure_labels, failure_values = self._dict_chart_values(failures)
        recommendation_labels, recommendation_values = self._dict_chart_values(recommendations)
        diagnostic_labels, diagnostic_values = self._dict_chart_values(diagnostics)
        timeline_labels, timeline_values = self._dict_chart_values(timeline)
        return {
            "summary": summary,
            "latest": latest,
            "gates": bar_chart(
                "توزيع البوابات",
                gate_labels,
                gate_values,
                label="البوابات",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "توزيع الجاهزية",
                readiness_labels,
                readiness_values,
                label="الجاهزية",
                color="blue",
            ).to_dict(),
            "stability": bar_chart(
                "توزيع الاستقرار",
                stability_labels,
                stability_values,
                label="الاستقرار",
                color="accent",
            ).to_dict(),
            "strengths": bar_chart(
                "نقاط القوة",
                strength_labels,
                strength_values,
                label="القوة",
                color="green",
            ).to_dict(),
            "weaknesses": bar_chart(
                "نقاط الضعف",
                weakness_labels,
                weakness_values,
                label="الضعف",
                color="warning",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الفشل",
                failure_labels,
                failure_values,
                label="الفشل",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                recommendation_labels,
                recommendation_values,
                label="التوصيات",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التشخيص",
                diagnostic_labels,
                diagnostic_values,
                label="التشخيص",
                color="accent",
            ).to_dict(),
            "timeline": line_chart(
                "تطور الجاهزية بمرور الوقت",
                timeline_labels,
                timeline_values,
                label="الجاهزية",
                color="green",
            ).to_dict(),
        }

    def strategy_benchmark_analytics(self) -> dict[str, Any]:
        """Return latest strategy benchmark analytics."""
        summary_payload = self._latest_json_dict("strategy_benchmark", "summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        best = summary_payload.get("best_profile", {}) if summary_payload else {}
        benchmark = summary_payload.get("benchmark_distribution", {}) if summary_payload else {}
        readiness = summary_payload.get("readiness_distribution", {}) if summary_payload else {}
        stability = summary_payload.get("stability_distribution", {}) if summary_payload else {}
        quality = summary_payload.get("quality_distribution", {}) if summary_payload else {}
        timeline = summary_payload.get("timeline", {}) if summary_payload else {}
        strengths = summary_payload.get("strengths", {}) if summary_payload else {}
        weaknesses = summary_payload.get("weaknesses", {}) if summary_payload else {}
        rankings = self._latest_json_dict("strategy_benchmark", "profile_rankings")
        improvements = self._latest_json_dict("strategy_benchmark", "improvement")
        robustness = self._latest_json_dict("strategy_benchmark", "robustness")
        recommendations = self._latest_json_dict(
            "strategy_benchmark",
            "recommendations",
        )
        degradations = (
            {key: value for key, value in improvements.items() if self._float(value) < 0}
            if isinstance(improvements, dict)
            else {}
        )
        if not summary:
            summary = {
                "profile_count": 0,
                "best_profile": "غير متاح",
                "highest_score": 0.0,
                "average_performance": 0.0,
                "highest_stability": 0.0,
                "highest_readiness": 0.0,
                "certification_state": "غير متاح",
            }
        return {
            "summary": summary,
            "best": best,
            "ranking": bar_chart(
                "ترتيب الملفات",
                *self._dict_chart_values(rankings or benchmark),
                label="الدرجة",
                color="green",
            ).to_dict(),
            "scores": bar_chart(
                "توزيع الدرجات",
                *self._dict_chart_values(benchmark),
                label="الدرجة",
                color="blue",
            ).to_dict(),
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="accent",
            ).to_dict(),
            "stability": bar_chart(
                "توزيع الاستقرار",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="warning",
            ).to_dict(),
            "quality": bar_chart(
                "توزيع الجودة",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "timeline": line_chart(
                "المقارنة الزمنية",
                *self._dict_chart_values(timeline),
                label="الأداء",
                color="blue",
            ).to_dict(),
            "improvements": bar_chart(
                "التحسينات",
                *self._dict_chart_values(improvements),
                label="الفارق",
                color="green",
            ).to_dict(),
            "degradations": bar_chart(
                "التراجعات",
                *self._dict_chart_values(degradations),
                label="الفارق",
                color="warning",
            ).to_dict(),
            "strengths": bar_chart(
                "نقاط القوة",
                *self._dict_chart_values(strengths),
                label="القوة",
                color="green",
            ).to_dict(),
            "weaknesses": bar_chart(
                "نقاط الضعف",
                *self._dict_chart_values(weaknesses),
                label="الضعف",
                color="warning",
            ).to_dict(),
            "robustness": robustness,
            "recommendations": recommendations,
        }

    def pattern_memory_analytics(self) -> dict[str, Any]:
        """Return latest adaptive pattern memory analytics."""
        summary_payload = self._latest_json_dict("pattern_memory", "summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        best = summary_payload.get("best_pattern", {}) if summary_payload else {}
        pattern_rankings = summary_payload.get("pattern_rankings", {}) if summary_payload else {}
        session_rankings = summary_payload.get("session_rankings", {}) if summary_payload else {}
        asset_rankings = summary_payload.get("asset_rankings", {}) if summary_payload else {}
        structure_rankings = (
            summary_payload.get("structure_rankings", {}) if summary_payload else {}
        )
        fvg_rankings = summary_payload.get("fvg_rankings", {}) if summary_payload else {}
        cisd_rankings = summary_payload.get("cisd_rankings", {}) if summary_payload else {}
        reliability_timeline = (
            summary_payload.get("reliability_timeline", {}) if summary_payload else {}
        )
        similarity = self._latest_json_dict("pattern_memory", "similarity")
        learning = self._latest_json_dict("pattern_memory", "learning")
        quality = self._latest_json_dict("pattern_memory", "quality")
        reliability = self._latest_json_dict("pattern_memory", "reliability")
        if not summary:
            summary = {
                "pattern_count": 0,
                "successful_patterns": 0,
                "failed_patterns": 0,
                "reliability_score": 0.0,
                "stability_score": 0.0,
                "learning_score": 0.0,
                "adaptation_score": 0.0,
                "best_pattern": "غير متاح",
            }
        return {
            "summary": summary,
            "best": best,
            "pattern_rankings": bar_chart(
                "ترتيب الأنماط",
                *self._dict_chart_values(pattern_rankings),
                label="الدرجة",
                color="green",
            ).to_dict(),
            "session_rankings": bar_chart(
                "ترتيب الجلسات",
                *self._dict_chart_values(session_rankings),
                label="الجودة",
                color="blue",
            ).to_dict(),
            "asset_rankings": bar_chart(
                "ترتيب الأصول",
                *self._dict_chart_values(asset_rankings),
                label="الجودة",
                color="accent",
            ).to_dict(),
            "structure_rankings": bar_chart(
                "ترتيب الهياكل",
                *self._dict_chart_values(structure_rankings),
                label="الجودة",
                color="warning",
            ).to_dict(),
            "fvg_rankings": bar_chart(
                "ترتيب FVG",
                *self._dict_chart_values(fvg_rankings),
                label="الجودة",
                color="green",
            ).to_dict(),
            "cisd_rankings": bar_chart(
                "ترتيب CISD",
                *self._dict_chart_values(cisd_rankings),
                label="الجودة",
                color="blue",
            ).to_dict(),
            "similarity": bar_chart(
                "توزيع التشابه",
                *self._dict_chart_values(similarity),
                label="التشابه",
                color="accent",
            ).to_dict(),
            "learning": bar_chart(
                "تقدم التعلم",
                *self._dict_chart_values(learning),
                label="التعلم",
                color="green",
            ).to_dict(),
            "quality": bar_chart(
                "جودة الأنماط",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="warning",
            ).to_dict(),
            "reliability": line_chart(
                "خط موثوقية الأنماط",
                *self._dict_chart_values(reliability or reliability_timeline),
                label="الموثوقية",
                color="blue",
            ).to_dict(),
        }

    def market_regime_analytics(self) -> dict[str, Any]:
        """Return latest market regime analytics."""
        summary_payload = self._latest_json_dict("market_regime", "regime_summary")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        regime = summary_payload.get("regime_distribution", {}) if summary_payload else {}
        historical = summary_payload.get("historical_performance", {}) if summary_payload else {}
        volatility = self._latest_json_dict("market_regime", "volatility")
        trend = self._latest_json_dict("market_regime", "trend")
        transition = self._latest_json_dict("market_regime", "transition")
        compatibility = self._latest_json_dict("market_regime", "compatibility")
        stability = self._latest_json_dict("market_regime", "stability")
        quality = self._latest_json_dict("market_regime", "quality")
        if not summary:
            summary = {
                "regime_state": "غير متاح",
                "regime_score": 0.0,
                "volatility_score": 0.0,
                "trend_strength": 0.0,
                "compatibility_score": 0.0,
                "stability_score": 0.0,
                "quality_score": 0.0,
            }
        return {
            "summary": summary,
            "regime": bar_chart(
                "توزيع حالات السوق",
                *self._dict_chart_values(regime),
                label="الحالة",
                color="green",
            ).to_dict(),
            "volatility": bar_chart(
                "توزيع التقلب",
                *self._dict_chart_values(volatility),
                label="التقلب",
                color="warning",
            ).to_dict(),
            "trend": bar_chart(
                "توزيع الاتجاه",
                *self._dict_chart_values(trend),
                label="الاتجاه",
                color="blue",
            ).to_dict(),
            "transition": bar_chart(
                "تحليل الانتقال",
                *self._dict_chart_values(transition),
                label="الانتقال",
                color="accent",
            ).to_dict(),
            "compatibility": bar_chart(
                "تحليل التوافق",
                *self._dict_chart_values(compatibility),
                label="التوافق",
                color="green",
            ).to_dict(),
            "stability": bar_chart(
                "استقرار حالة السوق",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "جودة حالة السوق",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="warning",
            ).to_dict(),
            "historical": bar_chart(
                "الأداء التاريخي لحالات السوق",
                *self._dict_chart_values(historical),
                label="الأداء",
                color="accent",
            ).to_dict(),
        }

    def research_certification_analytics(self) -> dict[str, Any]:
        """Return latest research certification analytics."""
        payload = self._latest_json_dict("research_certification", "certification_summary")
        summary = payload.get("summary", {}) if payload else {}
        certification = payload.get("certification_distribution", {}) if payload else {}
        certification_timeline = payload.get("certification_timeline", {}) if payload else {}
        maturity_timeline = payload.get("maturity_timeline", {}) if payload else {}
        maturity = self._latest_json_dict("research_certification", "maturity")
        robustness = self._latest_json_dict("research_certification", "robustness")
        consistency = self._latest_json_dict("research_certification", "consistency")
        stability = self._latest_json_dict("research_certification", "stability")
        requirements = self._latest_json_dict("research_certification", "requirements")
        diagnostics = self._latest_json_dict("research_certification", "diagnostics")
        recommendations = self._latest_json_dict(
            "research_certification",
            "recommendations",
        )
        if not summary:
            summary = {
                "certification_score": 0.0,
                "certification_state": "غير متاح",
                "maturity_score": 0.0,
                "stability_score": 0.0,
                "consistency_score": 0.0,
                "robustness_score": 0.0,
                "warning_count": 0,
                "failure_count": 0,
                "recommendation_count": 0,
                "sample_size": 0,
            }
        return {
            "summary": summary,
            "certification": bar_chart(
                "توزيع الاعتماد",
                *self._dict_chart_values(certification),
                label="الاعتماد",
                color="green",
            ).to_dict(),
            "maturity": bar_chart(
                "توزيع النضج",
                *self._dict_chart_values(maturity),
                label="النضج",
                color="blue",
            ).to_dict(),
            "stability": bar_chart(
                "توزيع الثبات",
                *self._dict_chart_values(stability),
                label="الثبات",
                color="accent",
            ).to_dict(),
            "consistency": bar_chart(
                "توزيع الاتساق",
                *self._dict_chart_values(consistency),
                label="الاتساق",
                color="green",
            ).to_dict(),
            "robustness": bar_chart(
                "توزيع المتانة",
                *self._dict_chart_values(robustness),
                label="المتانة",
                color="warning",
            ).to_dict(),
            "requirements": bar_chart(
                "نتائج المتطلبات",
                *self._dict_chart_values(requirements),
                label="المتطلبات",
                color="blue",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الفشل",
                *self._dict_chart_values(diagnostics),
                label="الفشل",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="accent",
            ).to_dict(),
            "certification_timeline": line_chart(
                "تطور الاعتماد بمرور الوقت",
                *self._dict_chart_values(certification_timeline),
                label="الاعتماد",
                color="green",
            ).to_dict(),
            "maturity_timeline": line_chart(
                "تطور النضج",
                *self._dict_chart_values(maturity_timeline),
                label="النضج",
                color="blue",
            ).to_dict(),
        }

    def broker_readiness_analytics(self) -> dict[str, Any]:
        """Return latest passive broker observation readiness analytics."""
        payload = self._latest_json_dict("broker_readiness", "readiness_summary")
        summary = payload.get("summary", {}) if payload else {}
        readiness = payload.get("readiness_distribution", {}) if payload else {}
        readiness_timeline = payload.get("readiness_timeline", {}) if payload else {}
        capability_timeline = payload.get("capability_timeline", {}) if payload else {}
        safety_timeline = payload.get("safety_timeline", {}) if payload else {}
        capability = self._latest_json_dict("broker_readiness", "capability")
        validation = self._latest_json_dict("broker_readiness", "validation")
        restrictions = self._latest_json_dict("broker_readiness", "restriction")
        diagnostics = self._latest_json_dict("broker_readiness", "diagnostics")
        recommendations = self._latest_json_dict("broker_readiness", "recommendations")
        safety = {
            "السلامة": summary.get("safety_score", 0),
            "القيود": 100.0 if restrictions.get("ناجح") else 0.0,
        }
        if not summary:
            summary = {
                "readiness_score": 0.0,
                "readiness_state": "غير متاح",
                "capability_score": 0.0,
                "safety_score": 0.0,
                "validation_score": 0.0,
                "warning_count": 0,
                "failure_count": 0,
                "recommendation_count": 0,
                "coverage_level": 0.0,
            }
        return {
            "summary": summary,
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="green",
            ).to_dict(),
            "capability": bar_chart(
                "توزيع القدرات",
                *self._dict_chart_values(capability),
                label="القدرات",
                color="blue",
            ).to_dict(),
            "safety": bar_chart(
                "توزيع السلامة",
                *self._dict_chart_values(safety),
                label="السلامة",
                color="warning",
            ).to_dict(),
            "validation": bar_chart(
                "توزيع التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "restrictions": bar_chart(
                "نتائج القيود",
                *self._dict_chart_values(restrictions),
                label="القيود",
                color="green",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الإخفاق",
                *self._dict_chart_values(diagnostics),
                label="الإخفاق",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="blue",
            ).to_dict(),
            "readiness_timeline": line_chart(
                "تطور الجاهزية",
                *self._dict_chart_values(readiness_timeline),
                label="الجاهزية",
                color="green",
            ).to_dict(),
            "capability_timeline": line_chart(
                "تطور القدرات",
                *self._dict_chart_values(capability_timeline),
                label="القدرات",
                color="blue",
            ).to_dict(),
            "safety_timeline": line_chart(
                "تطور السلامة",
                *self._dict_chart_values(safety_timeline),
                label="السلامة",
                color="warning",
            ).to_dict(),
        }

    def external_observation_analytics(self) -> dict[str, Any]:
        """Return latest external observation sandbox analytics."""
        payload = self._latest_json_dict("external_observation", "sandbox_summary")
        summary = payload.get("summary", {}) if payload else {}
        sources = payload.get("source_distribution", {}) if payload else {}
        validation = self._latest_json_dict("external_observation", "validation")
        monitoring = self._latest_json_dict("external_observation", "monitoring")
        health = self._latest_json_dict("external_observation", "health")
        diagnostics = self._latest_json_dict("external_observation", "diagnostics")
        recommendations = self._latest_json_dict(
            "external_observation",
            "recommendations",
        )
        latest = payload.get("latest", {}) if payload else {}
        analytics = self._latest_json_dict("external_observation", "diagnostics")
        isolation = latest.get("isolation", {}) if isinstance(latest.get("isolation"), dict) else {}
        isolation_chart = {
            "لا اتصال وسيط": 100.0 if isolation.get("no_broker_connectivity") else 0.0,
            "لا وصول حساب": 100.0 if isolation.get("no_account_access") else 0.0,
            "لا مسارات تنفيذ": 100.0 if isolation.get("no_execution_paths") else 0.0,
            "لا مصادقة": 100.0 if isolation.get("no_authentication_flows") else 0.0,
            "لا أوامر": 100.0 if isolation.get("no_order_apis") else 0.0,
        }
        source_quality = latest.get("sources", []) if isinstance(latest, dict) else []
        quality = {
            item.get("source_name", "مصدر"): (
                100.0 if item.get("validation_status") == "ناجح" else 50.0
            )
            for item in source_quality
            if isinstance(item, dict)
        }
        stability = {
            item.get("source_name", "مصدر"): (
                100.0 if item.get("observation_status") == "نشط" else 50.0
            )
            for item in source_quality
            if isinstance(item, dict)
        }
        coverage = {
            item.get("source_name", "مصدر"): 100.0 if item.get("visibility_scope") else 0.0
            for item in source_quality
            if isinstance(item, dict)
        }
        if not summary:
            summary = {
                "source_count": 0,
                "sandbox_score": 0.0,
                "sandbox_state": "غير متاح",
                "health_score": 0.0,
                "validation_score": 0.0,
                "monitoring_score": 0.0,
                "isolation_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
            }
        return {
            "summary": summary,
            "sources": bar_chart(
                "توزيع المصادر",
                *self._dict_chart_values(sources),
                label="المصادر",
                color="blue",
            ).to_dict(),
            "health": bar_chart(
                "توزيع الصحة",
                *self._dict_chart_values(health),
                label="الصحة",
                color="green",
            ).to_dict(),
            "validation": bar_chart(
                "توزيع التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "monitoring": bar_chart(
                "توزيع المراقبة",
                *self._dict_chart_values(monitoring),
                label="المراقبة",
                color="blue",
            ).to_dict(),
            "isolation": bar_chart(
                "توزيع العزل",
                *self._dict_chart_values(isolation_chart),
                label="العزل",
                color="warning",
            ).to_dict(),
            "source_quality": bar_chart(
                "جودة المصادر",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "source_stability": bar_chart(
                "استقرار المصادر",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "source_coverage": bar_chart(
                "تغطية المصادر",
                *self._dict_chart_values(coverage),
                label="التغطية",
                color="accent",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الإخفاق",
                *self._dict_chart_values(diagnostics),
                label="الإخفاق",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "analytics": analytics,
        }

    def browser_observation_analytics(self) -> dict[str, Any]:
        """Return latest read-only browser observation analytics."""
        payload = self._latest_json_dict("browser_observation", "observation_summary")
        summary = payload.get("summary", {}) if payload else {}
        artifacts = payload.get("artifact_distribution", {}) if payload else {}
        readiness = payload.get("readiness_distribution", {}) if payload else {}
        validation = self._latest_json_dict("browser_observation", "validation")
        visibility = self._latest_json_dict("browser_observation", "visibility")
        monitoring = self._latest_json_dict("browser_observation", "monitoring")
        diagnostics = self._latest_json_dict("browser_observation", "diagnostics")
        recommendations = self._latest_json_dict(
            "browser_observation",
            "recommendations",
        )
        latest = payload.get("latest", {}) if payload else {}
        safety = latest.get("safety", {}) if isinstance(latest, dict) else {}
        safety_chart = {
            "لا تسجيل دخول": 100.0 if safety.get("no_login") else 0.0,
            "لا مصادقة": 100.0 if safety.get("no_authentication") else 0.0,
            "لا تحكم متصفح": 100.0 if safety.get("no_browser_control") else 0.0,
            "لا تنفيذ": 100.0 if safety.get("no_execution") else 0.0,
            "لا أوامر": 100.0 if safety.get("no_order_apis") else 0.0,
            "لا وصول حساب": 100.0 if safety.get("no_account_access") else 0.0,
            "لا أتمتة": 100.0 if safety.get("no_automation") else 0.0,
        }
        artifact_rows = latest.get("artifacts", []) if isinstance(latest, dict) else []
        quality = {
            item.get("artifact_id", "لقطة"): (
                100.0 if item.get("validation_status") == "ناجح" else 50.0
            )
            for item in artifact_rows
            if isinstance(item, dict)
        }
        stability = {
            item.get("artifact_id", "لقطة"): (
                100.0 if item.get("monitoring_status") == "مستقر" else 50.0
            )
            for item in artifact_rows
            if isinstance(item, dict)
        }
        if not summary:
            summary = {
                "artifact_count": 0,
                "adapter_score": 0.0,
                "adapter_state": "غير متاح",
                "safety_score": 0.0,
                "validation_score": 0.0,
                "visibility_score": 0.0,
                "monitoring_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
            }
        return {
            "summary": summary,
            "artifacts": bar_chart(
                "توزيع اللقطات",
                *self._dict_chart_values(artifacts),
                label="اللقطات",
                color="blue",
            ).to_dict(),
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="green",
            ).to_dict(),
            "safety": bar_chart(
                "توزيع السلامة",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="warning",
            ).to_dict(),
            "validation": bar_chart(
                "توزيع التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "visibility": bar_chart(
                "توزيع الرؤية",
                *self._dict_chart_values(visibility),
                label="الرؤية",
                color="blue",
            ).to_dict(),
            "monitoring": bar_chart(
                "توزيع المراقبة",
                *self._dict_chart_values(monitoring),
                label="المراقبة",
                color="green",
            ).to_dict(),
            "artifact_quality": bar_chart(
                "جودة اللقطات",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "artifact_stability": bar_chart(
                "استقرار اللقطات",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الإخفاق",
                *self._dict_chart_values(diagnostics),
                label="الإخفاق",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="accent",
            ).to_dict(),
        }

    def snapshot_import_analytics(self) -> dict[str, Any]:
        """Return latest manual snapshot import analytics."""
        payload = self._latest_json_dict("snapshot_import", "import_summary")
        summary = payload.get("summary", {}) if payload else {}
        imports = payload.get("import_distribution", {}) if payload else {}
        quality_timeline = payload.get("quality_timeline", {}) if payload else {}
        validation = self._latest_json_dict("snapshot_import", "validation")
        processing = self._latest_json_dict("snapshot_import", "processing")
        quality = self._latest_json_dict("snapshot_import", "quality")
        diagnostics = self._latest_json_dict("snapshot_import", "diagnostics")
        recommendations = self._latest_json_dict("snapshot_import", "recommendations")
        latest = payload.get("latest", {}) if payload else {}
        safety = latest.get("safety", {}) if isinstance(latest, dict) else {}
        safety_chart = {
            "لا تسجيل دخول": 100.0 if safety.get("no_login") else 0.0,
            "لا مصادقة": 100.0 if safety.get("no_authentication") else 0.0,
            "لا أتمتة متصفح": 100.0 if safety.get("no_browser_automation") else 0.0,
            "لا وصول وسيط": 100.0 if safety.get("no_broker_access") else 0.0,
            "لا تنفيذ": 100.0 if safety.get("no_execution") else 0.0,
            "لا تفاعل حساب": 100.0 if safety.get("no_account_interaction") else 0.0,
        }
        rows = latest.get("imports", []) if isinstance(latest, dict) else []
        file_quality = {
            item.get("filename", "ملف"): 100.0 if item.get("validation_status") == "ناجح" else 50.0
            for item in rows
            if isinstance(item, dict)
        }
        file_completeness = {
            item.get("filename", "ملف"): 100.0 if item.get("size_bytes", 0) else 0.0
            for item in rows
            if isinstance(item, dict)
        }
        if not summary:
            summary = {
                "import_count": 0,
                "workflow_score": 0.0,
                "workflow_state": "غير متاح",
                "quality_score": 0.0,
                "validation_score": 0.0,
                "processing_score": 0.0,
                "safety_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
                "last_import": "غير متاح",
            }
        return {
            "summary": summary,
            "imports": bar_chart(
                "توزيع اللقطات",
                *self._dict_chart_values(imports),
                label="اللقطات",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "توزيع الجودة",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "validation": bar_chart(
                "توزيع التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "processing": bar_chart(
                "توزيع المعالجة",
                *self._dict_chart_values(processing),
                label="المعالجة",
                color="blue",
            ).to_dict(),
            "safety": bar_chart(
                "توزيع السلامة",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="warning",
            ).to_dict(),
            "file_quality": bar_chart(
                "جودة الملفات",
                *self._dict_chart_values(file_quality),
                label="الملفات",
                color="green",
            ).to_dict(),
            "file_completeness": bar_chart(
                "اكتمال الملفات",
                *self._dict_chart_values(file_completeness),
                label="الاكتمال",
                color="accent",
            ).to_dict(),
            "failures": bar_chart(
                "أسباب الرفض",
                *self._dict_chart_values(diagnostics),
                label="الرفض",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="blue",
            ).to_dict(),
            "quality_timeline": line_chart(
                "تطور الجودة",
                *self._dict_chart_values(quality_timeline),
                label="الجودة",
                color="green",
            ).to_dict(),
        }

    def observation_intelligence_analytics(self) -> dict[str, Any]:
        """Return latest unified observation intelligence analytics."""
        payload = self._latest_json_dict(
            "observation_intelligence",
            "observation_summary",
        )
        summary = payload.get("summary", {}) if payload else {}
        sources = payload.get("source_distribution", {}) if payload else {}
        readiness = payload.get("readiness_distribution", {}) if payload else {}
        quality = self._latest_json_dict("observation_intelligence", "quality")
        confidence = self._latest_json_dict("observation_intelligence", "confidence")
        coverage = self._latest_json_dict("observation_intelligence", "coverage")
        diagnostics = self._latest_json_dict("observation_intelligence", "diagnostics")
        recommendations = self._latest_json_dict(
            "observation_intelligence",
            "recommendations",
        )
        latest = payload.get("latest", {}) if payload else {}
        aggregation = latest.get("aggregation", {}) if isinstance(latest, dict) else {}
        validation = latest.get("validation", {}) if isinstance(latest, dict) else {}
        source_quality = (
            {
                item.get("source_name", "مصدر"): item.get("quality_score", 0)
                for item in latest.get("observations", [])
                if isinstance(item, dict)
            }
            if isinstance(latest, dict)
            else {}
        )
        consistency = {
            "الاتساق": aggregation.get("consistency", 0),
            "التحقق": validation.get("consistency", 0),
        }
        conflicts = {
            "تضارب": aggregation.get("conflicts", 0),
            "اتساق": aggregation.get("consistency", 0),
        }
        if not summary:
            summary = {
                "observation_count": 0,
                "quality_score": 0.0,
                "confidence_score": 0.0,
                "consistency_score": 0.0,
                "coverage_score": 0.0,
                "readiness_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
            }
        return {
            "summary": summary,
            "sources": bar_chart(
                "توزيع المصادر",
                *self._dict_chart_values(sources),
                label="المصادر",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "توزيع الجودة",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                *self._dict_chart_values(confidence),
                label="الثقة",
                color="accent",
            ).to_dict(),
            "consistency": bar_chart(
                "توزيع الاتساق",
                *self._dict_chart_values(consistency),
                label="الاتساق",
                color="blue",
            ).to_dict(),
            "coverage": bar_chart(
                "توزيع التغطية",
                *self._dict_chart_values(coverage),
                label="التغطية",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="warning",
            ).to_dict(),
            "conflicts": bar_chart(
                "تضارب البيانات",
                *self._dict_chart_values(conflicts),
                label="التضارب",
                color="warning",
            ).to_dict(),
            "source_quality": bar_chart(
                "جودة المصادر",
                *self._dict_chart_values(source_quality),
                label="المصادر",
                color="green",
            ).to_dict(),
            "diagnostics": bar_chart(
                "أسباب التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="blue",
            ).to_dict(),
        }

    def market_observation_analytics(self) -> dict[str, Any]:
        """Return latest canonical market observation analytics."""
        payload = self._latest_json_dict("market_observation", "observation_summary")
        summary = payload.get("summary", {}) if payload else {}
        latest = payload.get("latest", {}) if payload else {}
        sources = self._latest_json_dict("market_observation", "source")
        quality = self._latest_json_dict("market_observation", "quality")
        confidence = self._latest_json_dict("market_observation", "confidence")
        scores = self._latest_json_dict("market_observation", "coverage")
        validation = self._latest_json_dict("market_observation", "validation")
        diagnostics = self._latest_json_dict("market_observation", "diagnostics")
        aggregate = latest.get("aggregate", {}) if isinstance(latest, dict) else {}
        market = {
            "الأصول": aggregate.get("asset_count", summary.get("asset_count", 0)),
            "العوائد": aggregate.get("payout_count", summary.get("payout_count", 0)),
            "الجلسات": aggregate.get("session_count", summary.get("session_count", 0)),
            "الرموز": aggregate.get("symbol_count", summary.get("symbol_count", 0)),
        }
        validation_chart = {
            "الاكتمال": validation.get("completeness", 0),
            "الاتساق": validation.get("consistency", 0),
            "السلامة": validation.get("integrity", 0),
        }
        if not summary:
            summary = {
                "observation_count": 0,
                "canonical_score": 0.0,
                "canonical_state": "غير متاح",
                "coverage_score": 0.0,
                "quality_score": 0.0,
                "confidence_score": 0.0,
                "visibility_score": 0.0,
                "freshness_score": 0.0,
                "consistency_score": 0.0,
                "asset_count": 0,
                "payout_count": 0,
                "session_count": 0,
                "symbol_count": 0,
                "diagnostic_count": 0,
                "research_only": True,
                "observation_only": True,
                "canonical_market_observation": True,
            }
        return {
            "summary": summary,
            "sources": bar_chart(
                "توزيع المصادر",
                *self._dict_chart_values(sources),
                label="المصادر",
                color="blue",
            ).to_dict(),
            "scores": bar_chart(
                "درجات مصدر المراقبة",
                *self._dict_chart_values(scores),
                label="الدرجة",
                color="green",
            ).to_dict(),
            "market": bar_chart(
                "مكونات السوق",
                *self._dict_chart_values(market),
                label="المكونات",
                color="accent",
            ).to_dict(),
            "source_quality": bar_chart(
                "جودة المصادر",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "source_confidence": bar_chart(
                "ثقة المصادر",
                *self._dict_chart_values(confidence),
                label="الثقة",
                color="blue",
            ).to_dict(),
            "validation": bar_chart(
                "تحقق المصدر",
                *self._dict_chart_values(validation_chart),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "diagnostics": bar_chart(
                "تشخيص المصدر",
                *self._dict_chart_values(diagnostics),
                label="التشخيص",
                color="warning",
            ).to_dict(),
        }

    def live_observation_analytics(self) -> dict[str, Any]:
        """Return latest deterministic live observation replay analytics."""
        payload = self._latest_json_dict("live_observation", "replay_summary")
        summary = payload.get("summary", {}) if payload else {}
        sources = payload.get("source_distribution", {}) if payload else {}
        timeline = self._latest_json_dict("live_observation", "timeline")
        quality = self._latest_json_dict("live_observation", "quality")
        readiness = self._latest_json_dict("live_observation", "readiness")
        validation = self._latest_json_dict("live_observation", "validation")
        diagnostics = self._latest_json_dict("live_observation", "diagnostics")
        recommendations = self._latest_json_dict("live_observation", "recommendations")
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        replay = latest.get("replay", {}) if isinstance(latest, dict) else {}
        timeline_payload = latest.get("timeline", {}) if isinstance(latest, dict) else {}
        coverage = {
            "التغطية": summary.get("coverage_score", 0),
            "الأحداث": replay.get("event_count", 0),
            "التسلسل": timeline_payload.get("sequence_count", 0),
        }
        speed = {
            f"{summary.get('speed_multiplier', 0)}x": summary.get("replay_score", 0),
            "مدعوم": 100.0 if summary else 0.0,
        }
        stability = {
            "الاستقرار": quality.get("stability", 0),
            "الاعتمادية": quality.get("reliability", 0),
            "الاتساق": quality.get("consistency", 0),
        }
        if not summary:
            summary = {
                "observation_count": 0,
                "replay_state": "غير متاح",
                "replay_score": 0.0,
                "quality_score": 0.0,
                "readiness_score": 0.0,
                "validation_score": 0.0,
                "coverage_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
                "research_only": True,
                "observation_only": True,
                "live_observation_replay": True,
            }
        return {
            "summary": summary,
            "timeline": line_chart(
                "التسلسل الزمني",
                *self._dict_chart_values(timeline),
                label="التسلسل",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "جودة التشغيل",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="accent",
            ).to_dict(),
            "validation": bar_chart(
                "التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="blue",
            ).to_dict(),
            "coverage": bar_chart(
                "التغطية",
                *self._dict_chart_values(coverage),
                label="التغطية",
                color="green",
            ).to_dict(),
            "speed": bar_chart(
                "السرعة",
                *self._dict_chart_values(speed),
                label="السرعة",
                color="warning",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(timeline),
                label="النشاط",
                color="accent",
            ).to_dict(),
            "sources": bar_chart(
                "مصادر الملاحظات",
                *self._dict_chart_values(sources),
                label="المصادر",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "أسباب التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "stability": bar_chart(
                "استقرار التشغيل",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="accent",
            ).to_dict(),
        }

    def signal_stream_analytics(self) -> dict[str, Any]:
        """Return latest research-only signal stream analytics."""
        payload = self._latest_json_dict("signal_stream", "signal_summary")
        summary = payload.get("summary", {}) if payload else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        stream = self._latest_json_dict("signal_stream", "stream")
        quality = self._latest_json_dict("signal_stream", "quality")
        readiness = self._latest_json_dict("signal_stream", "readiness")
        validation = self._latest_json_dict("signal_stream", "validation")
        diagnostics = self._latest_json_dict("signal_stream", "diagnostics")
        recommendations = self._latest_json_dict("signal_stream", "recommendations")
        timeline = latest.get("timeline", {}) if isinstance(latest, dict) else {}
        timeline_activity = timeline.get("activity", {}) if isinstance(timeline, dict) else {}
        events = latest.get("stream", {}).get("events", []) if isinstance(latest, dict) else []
        assets: dict[str, float] = {}
        sessions: dict[str, float] = {}
        confidence: dict[str, float] = {}
        density = {
            "الكثافة": timeline.get("density", 0) if isinstance(timeline, dict) else 0,
            "التكرار": timeline.get("frequency", 0) if isinstance(timeline, dict) else 0,
        }
        for item in events[:20] if isinstance(events, list) else []:
            if isinstance(item, dict):
                assets[str(item.get("asset", "أصل"))] = (
                    assets.get(
                        str(item.get("asset", "أصل")),
                        0.0,
                    )
                    + 1.0
                )
                sessions[str(item.get("session", "جلسة"))] = (
                    sessions.get(
                        str(item.get("session", "جلسة")),
                        0.0,
                    )
                    + 1.0
                )
                confidence[str(item.get("signal_id", "إشارة"))] = self._float(
                    item.get("confidence")
                )
        if not summary:
            summary = {
                "signal_count": 0,
                "call_count": 0,
                "put_count": 0,
                "no_trade_count": 0,
                "average_confidence": 0.0,
                "quality_score": 0.0,
                "readiness_score": 0.0,
                "warning_count": 0,
                "research_only": True,
                "signal_generation_only": True,
            }
        return {
            "summary": summary,
            "distribution": bar_chart(
                "توزيع الإشارات",
                *self._dict_chart_values(stream),
                label="الإشارات",
                color="blue",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                *self._dict_chart_values(confidence),
                label="الثقة",
                color="accent",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(timeline_activity),
                label="النشاط",
                color="green",
            ).to_dict(),
            "quality": bar_chart(
                "جودة الإشارات",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="blue",
            ).to_dict(),
            "assets": bar_chart(
                "توزيع الأصول",
                *self._dict_chart_values(assets),
                label="الأصول",
                color="accent",
            ).to_dict(),
            "sessions": bar_chart(
                "توزيع الجلسات",
                *self._dict_chart_values(sessions),
                label="الجلسات",
                color="green",
            ).to_dict(),
            "density": bar_chart(
                "كثافة الإشارات",
                *self._dict_chart_values(density),
                label="الكثافة",
                color="warning",
            ).to_dict(),
            "validation": bar_chart(
                "التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "أسباب التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def execution_readiness_analytics(self) -> dict[str, Any]:
        """Return latest research-only execution readiness analytics."""
        payload = self._latest_json_dict("execution_readiness", "execution_summary")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        readiness = self._latest_json_dict("execution_readiness", "readiness")
        qualification = self._latest_json_dict("execution_readiness", "qualification")
        gates = self._latest_json_dict("execution_readiness", "gate")
        validation = self._latest_json_dict("execution_readiness", "validation")
        diagnostics = self._latest_json_dict("execution_readiness", "diagnostics")
        recommendations = self._latest_json_dict("execution_readiness", "recommendations")
        candidates = latest.get("candidates", []) if isinstance(latest, dict) else []
        confidence: dict[str, float] = {}
        quality: dict[str, float] = {}
        confluence: dict[str, float] = {}
        rejections: dict[str, float] = {}
        activity: dict[str, float] = {}
        for item in candidates[:20] if isinstance(candidates, list) else []:
            if not isinstance(item, dict):
                continue
            label = str(item.get("candidate_id", "مرشح"))
            confidence[label] = self._float(item.get("confidence"))
            quality[label] = self._float(item.get("quality"))
            confluence[label] = self._float(item.get("confluence"))
            day = str(item.get("timestamp", ""))[:10] or "غير محدد"
            activity[day] = activity.get(day, 0.0) + 1.0
            if item.get("qualification") == "مرفوض":
                if self._float(item.get("confidence")) < 50:
                    reason = "الثقة منخفضة"
                elif self._float(item.get("quality")) < 50:
                    reason = "الجودة منخفضة"
                elif self._float(item.get("confluence")) < 50:
                    reason = "التوافق منخفض"
                else:
                    reason = "الجاهزية منخفضة"
                rejections[reason] = rejections.get(reason, 0.0) + 1.0
        if not summary:
            summary = {
                "candidate_count": 0,
                "qualified_count": 0,
                "conditional_count": 0,
                "rejected_count": 0,
                "average_readiness": 0.0,
                "average_confidence": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
                "qualification_state": "غير متاح",
                "research_only": True,
                "readiness_only": True,
                "not_execution": True,
            }
        return {
            "summary": summary,
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="blue",
            ).to_dict(),
            "qualification": bar_chart(
                "توزيع التأهيل",
                *self._dict_chart_values(qualification),
                label="التأهيل",
                color="green",
            ).to_dict(),
            "confidence": bar_chart(
                "توزيع الثقة",
                *self._dict_chart_values(confidence),
                label="الثقة",
                color="accent",
            ).to_dict(),
            "quality": bar_chart(
                "توزيع الجودة",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "confluence": bar_chart(
                "توزيع التوافق",
                *self._dict_chart_values(confluence),
                label="التوافق",
                color="blue",
            ).to_dict(),
            "gates": bar_chart(
                "نتائج البوابات",
                *self._dict_chart_values(gates),
                label="البوابات",
                color="warning",
            ).to_dict(),
            "rejections": bar_chart(
                "أسباب الرفض",
                *self._dict_chart_values(rejections),
                label="الأسباب",
                color="warning",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(activity),
                label="النشاط",
                color="blue",
            ).to_dict(),
            "validation": bar_chart(
                "التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
        }

    def paper_execution_analytics(self) -> dict[str, Any]:
        """Return latest paper-only execution analytics."""
        payload = self._latest_json_dict("paper_execution", "paper_execution_summary")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        orders_report = self._latest_json_dict("paper_execution", "orders")
        results_report = self._latest_json_dict("paper_execution", "results")
        risk_report = self._latest_json_dict("paper_execution", "risk")
        diagnostics = self._latest_json_dict("paper_execution", "diagnostics")
        recommendations = self._latest_json_dict("paper_execution", "recommendations")
        orders = latest.get("orders", []) if isinstance(latest, dict) else []
        confidence: dict[str, float] = {}
        readiness: dict[str, float] = {}
        rejections: dict[str, float] = {}
        activity: dict[str, float] = {}
        for item in orders[:20] if isinstance(orders, list) else []:
            if not isinstance(item, dict):
                continue
            label = str(item.get("order_id", "أمر ورقي"))
            confidence[label] = self._float(item.get("confidence"))
            readiness[label] = self._float(item.get("readiness_score"))
            day = str(item.get("created_at", ""))[:10] or "غير محدد"
            activity[day] = activity.get(day, 0.0) + 1.0
            if item.get("status") == "REJECTED":
                reason = "جاهزية منخفضة"
                if str(item.get("direction")) == "NO_TRADE":
                    reason = "اتجاه غير قابل للورق"
                elif self._float(item.get("confidence")) < 60:
                    reason = "ثقة منخفضة"
                rejections[reason] = rejections.get(reason, 0.0) + 1.0
        if not summary:
            summary = {
                "total_paper_orders": 0,
                "accepted": 0,
                "rejected": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "average_readiness": 0.0,
                "warning_count": 0,
                "paper_only": True,
                "research_only": True,
                "not_real_execution": True,
            }
        return {
            "summary": summary,
            "orders": bar_chart(
                "توزيع الأوامر الورقية",
                *self._dict_chart_values(orders_report),
                label="الأوامر",
                color="blue",
            ).to_dict(),
            "results": bar_chart(
                "توزيع النتائج",
                *self._dict_chart_values(results_report),
                label="النتائج",
                color="green",
            ).to_dict(),
            "win_rate": bar_chart(
                "نسبة النجاح الورقية",
                ["النجاح", "غير ناجحة"],
                [
                    self._float(summary.get("win_rate")) * 100,
                    max(0.0, 100 - self._float(summary.get("win_rate")) * 100),
                ],
                label="النسبة",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="blue",
            ).to_dict(),
            "confidence": bar_chart(
                "الثقة",
                *self._dict_chart_values(confidence),
                label="الثقة",
                color="accent",
            ).to_dict(),
            "risk": bar_chart(
                "المخاطر الورقية",
                *self._dict_chart_values(risk_report),
                label="المخاطر",
                color="warning",
            ).to_dict(),
            "rejections": bar_chart(
                "أسباب الرفض",
                *self._dict_chart_values(rejections),
                label="الأسباب",
                color="warning",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(activity),
                label="النشاط",
                color="blue",
            ).to_dict(),
        }

    def paper_portfolio_analytics(self) -> dict[str, Any]:
        """Return latest paper-only portfolio governance analytics."""
        payload = self._latest_json_dict("paper_portfolio", "portfolio_summary")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        portfolio = latest.get("portfolio", {}) if isinstance(latest, dict) else {}
        exposure = self._latest_json_dict("paper_portfolio", "exposure")
        drawdown = self._latest_json_dict("paper_portfolio", "drawdown")
        governance = self._latest_json_dict("paper_portfolio", "governance")
        limits = self._latest_json_dict("paper_portfolio", "limits")
        diagnostics = self._latest_json_dict("paper_portfolio", "diagnostics")
        recommendations = self._latest_json_dict("paper_portfolio", "recommendations")
        if not summary:
            summary = {
                "portfolio_score": 0.0,
                "warning_count": 0,
                "recommendation_count": 0,
                "paper_only": True,
                "research_only": True,
            }
        if isinstance(portfolio, dict):
            summary = {**portfolio, **summary}
        exposure_assets = exposure.get("asset_exposure", {}) if isinstance(exposure, dict) else {}
        exposure_sessions = (
            exposure.get("session_exposure", {}) if isinstance(exposure, dict) else {}
        )
        performance = {
            "الرابحة": self._float(summary.get("wins")),
            "الخاسرة": self._float(summary.get("losses")),
            "تعادل": self._float(summary.get("breakeven")),
        }
        health = {
            "الصحة": self._float(summary.get("health_score")),
            "المخاطر": self._float(summary.get("risk_score")),
        }
        stability = {"الاستقرار": self._float(summary.get("stability_score"))}
        return {
            "summary": summary,
            "performance": bar_chart(
                "الأداء الورقي",
                *self._dict_chart_values(performance),
                label="الأداء",
                color="green",
            ).to_dict(),
            "drawdown": bar_chart(
                "السحب",
                *self._dict_chart_values(drawdown),
                label="السحب",
                color="warning",
            ).to_dict(),
            "exposure": (
                bar_chart(
                    "التعرض",
                    *self._dict_chart_values(exposure.get("direction_exposure", {})),
                    label="التعرض",
                    color="blue",
                ).to_dict()
                if isinstance(exposure, dict)
                else bar_chart("التعرض", [], []).to_dict()
            ),
            "assets": bar_chart(
                "توزيع الأصول",
                *self._dict_chart_values(exposure_assets),
                label="الأصول",
                color="accent",
            ).to_dict(),
            "sessions": bar_chart(
                "توزيع الجلسات",
                *self._dict_chart_values(exposure_sessions),
                label="الجلسات",
                color="green",
            ).to_dict(),
            "stability": bar_chart(
                "الاستقرار",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "health": bar_chart(
                "الصحة",
                *self._dict_chart_values(health),
                label="الصحة",
                color="green",
            ).to_dict(),
            "governance": bar_chart(
                "الحوكمة",
                *self._dict_chart_values({**governance, **limits}),
                label="الحوكمة",
                color="warning",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def paper_control_analytics(self) -> dict[str, Any]:
        """Return latest paper-only control center analytics."""
        payload = self._latest_json_dict(
            "paper_control_center",
            "control_center_summary",
        )
        health = self._latest_json_dict("paper_control_center", "health")
        monitoring = self._latest_json_dict("paper_control_center", "monitoring")
        governance = self._latest_json_dict("paper_control_center", "governance")
        decision = self._latest_json_dict("paper_control_center", "decision")
        diagnostics = self._latest_json_dict("paper_control_center", "diagnostics")
        recommendations = self._latest_json_dict(
            "paper_control_center",
            "recommendations",
        )
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        latest_decision = latest.get("decision", {}) if isinstance(latest, dict) else {}
        if not summary:
            summary = {
                "portfolio_health": 0.0,
                "portfolio_stability": 0.0,
                "execution_status": "WARNING",
                "readiness_status": "WARNING",
                "governance_status": "WARNING",
                "risk_status": "WARNING",
                "recommendation_count": 0,
                "warning_count": 0,
                "overall_score": 0.0,
                "paper_only": True,
                "research_only": True,
            }
        decision_label = (
            latest_decision.get("arabic_label")
            or latest_decision.get("decision_label")
            or "مراجعة مطلوبة"
        )
        summary = {
            **summary,
            "decision_label": decision_label,
            "paper_only": True,
            "research_only": True,
        }
        health_chart = {
            "الصحة العامة": self._float(summary.get("overall_score")),
            "صحة المحفظة": self._float(summary.get("portfolio_health")),
            "صحة التنفيذ": self._float(health.get("execution_health")),
            "صحة الجاهزية": self._float(health.get("readiness_health")),
        }
        stability_chart = {
            "الاستقرار": self._float(summary.get("portfolio_stability")),
            "استقرار الصحة": self._float(health.get("stability_health")),
            "المراقبة": self._float(monitoring.get("monitoring_score")),
        }
        readiness_chart = {
            "الجاهزية": self._status_score(summary.get("readiness_status")),
            "الصحة": self._float(health.get("readiness_health")),
            "تغير الجاهزية": self._float(monitoring.get("readiness_changes")),
        }
        execution_chart = {
            "التنفيذ الورقي": self._status_score(summary.get("execution_status")),
            "الأوامر النشطة": self._float(monitoring.get("active_paper_orders")),
            "الأوامر المكتملة": self._float(monitoring.get("completed_paper_orders")),
        }
        portfolio_chart = {
            "أداء المحفظة": self._float(summary.get("portfolio_health")),
            "الاستقرار": self._float(summary.get("portfolio_stability")),
            "تغيرات المحفظة": self._float(monitoring.get("portfolio_changes")),
            "تغيرات السحب": self._float(monitoring.get("drawdown_changes")),
        }
        decision_chart = {
            str(decision_label): self._float(summary.get("overall_score")),
            "التحذيرات": self._float(summary.get("warning_count")),
            "التوصيات": self._float(summary.get("recommendation_count")),
        }
        activity_chart = {
            "الأوامر النشطة": self._float(monitoring.get("active_paper_orders")),
            "الأوامر المكتملة": self._float(monitoring.get("completed_paper_orders")),
            "تغيرات الحوكمة": self._float(monitoring.get("governance_changes")),
            "تغيرات الجاهزية": self._float(monitoring.get("readiness_changes")),
        }
        return {
            "summary": summary,
            "latest": latest,
            "health": bar_chart(
                "الصحة العامة",
                *self._dict_chart_values(health_chart),
                label="الصحة العامة",
                color="green",
            ).to_dict(),
            "stability": bar_chart(
                "الاستقرار",
                *self._dict_chart_values(stability_chart),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "readiness": bar_chart(
                "الجاهزية",
                *self._dict_chart_values(readiness_chart),
                label="الجاهزية",
                color="accent",
            ).to_dict(),
            "governance": bar_chart(
                "الحوكمة",
                *self._dict_chart_values(governance),
                label="الحوكمة",
                color="warning",
            ).to_dict(),
            "execution": bar_chart(
                "التنفيذ الورقي",
                *self._dict_chart_values(execution_chart),
                label="التنفيذ الورقي",
                color="blue",
            ).to_dict(),
            "portfolio": bar_chart(
                "أداء المحفظة",
                *self._dict_chart_values(portfolio_chart),
                label="أداء المحفظة",
                color="green",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(activity_chart),
                label="النشاط الزمني",
                color="blue",
            ).to_dict(),
            "decision": bar_chart(
                "القرار الحالي",
                *self._dict_chart_values({**decision_chart, **decision}),
                label="القرار الحالي",
                color="accent",
            ).to_dict(),
        }

    def paper_live_readiness_analytics(self) -> dict[str, Any]:
        """Return latest readiness-only paper-to-live gate analytics."""
        payload = self._latest_json_dict(
            "paper_live_readiness",
            "readiness_summary",
        )
        gates = self._latest_json_dict("paper_live_readiness", "gate")
        safety = self._latest_json_dict("paper_live_readiness", "safety")
        maturity = self._latest_json_dict("paper_live_readiness", "maturity")
        stability = self._latest_json_dict("paper_live_readiness", "stability")
        diagnostics = self._latest_json_dict("paper_live_readiness", "diagnostics")
        recommendations = self._latest_json_dict(
            "paper_live_readiness",
            "recommendations",
        )
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            summary = {
                "paper_health": 0.0,
                "paper_stability": 0.0,
                "paper_governance": 0.0,
                "execution_readiness": 0.0,
                "observation_readiness": 0.0,
                "certification_score": 0.0,
                "safety_score": 0.0,
                "maturity_score": 0.0,
                "overall_score": 0.0,
                "readiness_state": "غير مؤهلة",
                "readiness_only": True,
                "paper_only": True,
                "research_only": True,
            }
        latest_diagnostics = latest.get("diagnostics", []) if isinstance(latest, dict) else []
        latest_recommendations = (
            latest.get("recommendations", []) if isinstance(latest, dict) else []
        )
        summary = {
            **summary,
            "warning_count": len(latest_diagnostics),
            "recommendation_count": len(latest_recommendations),
            "readiness_only": True,
            "paper_only": True,
            "research_only": True,
        }
        readiness_chart = {
            "صحة الورقي": self._float(summary.get("paper_health")),
            "استقرار الورقي": self._float(summary.get("paper_stability")),
            "جودة الحوكمة": self._float(summary.get("paper_governance")),
            "جاهزية التنفيذ": self._float(summary.get("execution_readiness")),
            "جاهزية المراقبة": self._float(summary.get("observation_readiness")),
            "الاعتماد": self._float(summary.get("certification_score")),
        }
        paper_chart = {
            "صحة الورقي": self._float(summary.get("paper_health")),
            "استقرار الورقي": self._float(summary.get("paper_stability")),
            "جودة الحوكمة": self._float(summary.get("paper_governance")),
        }
        observation_chart = {
            "المراقبة": self._float(summary.get("observation_readiness")),
            "السلامة": self._float(summary.get("safety_score")),
        }
        certification_chart = {
            "الاعتماد": self._float(summary.get("certification_score")),
            "النضج": self._float(summary.get("maturity_score")),
        }
        safety_chart = {
            "السلامة": self._float(safety.get("safety_score")),
            "بدون تنفيذ": 100.0 if safety.get("no_execution") else 0.0,
            "بدون تداول حي": 100.0 if safety.get("no_live_trading") else 0.0,
            "بدون وسيط": 100.0 if safety.get("no_broker_access") else 0.0,
            "بدون مصادقة": 100.0 if safety.get("no_authentication") else 0.0,
        }
        return {
            "summary": summary,
            "latest": latest,
            "readiness": bar_chart(
                "توزيع الجاهزية",
                *self._dict_chart_values(readiness_chart),
                label="توزيع الجاهزية",
                color="green",
            ).to_dict(),
            "gates": bar_chart(
                "نتائج البوابات",
                *self._dict_chart_values(gates),
                label="نتائج البوابات",
                color="warning",
            ).to_dict(),
            "stability": bar_chart(
                "الاستقرار",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
            "maturity": bar_chart(
                "النضج",
                *self._dict_chart_values(maturity),
                label="النضج",
                color="accent",
            ).to_dict(),
            "safety": bar_chart(
                "السلامة",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="green",
            ).to_dict(),
            "paper": bar_chart(
                "الورقي",
                *self._dict_chart_values(paper_chart),
                label="الورقي",
                color="blue",
            ).to_dict(),
            "observation": bar_chart(
                "المراقبة",
                *self._dict_chart_values(observation_chart),
                label="المراقبة",
                color="warning",
            ).to_dict(),
            "certification": bar_chart(
                "الاعتماد",
                *self._dict_chart_values(certification_chart),
                label="الاعتماد",
                color="accent",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def integration_safety_analytics(self) -> dict[str, Any]:
        """Return latest safety-boundary-only integration analytics."""
        payload = self._latest_json_dict("integration_safety", "safety_summary")
        permissions = self._latest_json_dict("integration_safety", "permission")
        restrictions = self._latest_json_dict("integration_safety", "restriction")
        compliance = self._latest_json_dict("integration_safety", "compliance")
        audit = self._latest_json_dict("integration_safety", "audit")
        diagnostics = self._latest_json_dict("integration_safety", "diagnostics")
        recommendations = self._latest_json_dict(
            "integration_safety",
            "recommendations",
        )
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            summary = {
                "boundary_status": "تحتاج مراجعة",
                "safety_score": 0.0,
                "compliance_score": 0.0,
                "allowed_capabilities": [],
                "forbidden_capabilities": [],
                "safety_boundary_only": True,
                "readiness_only": True,
                "research_only": True,
            }
        allowed = summary.get("allowed_capabilities", [])
        forbidden = summary.get("forbidden_capabilities", [])
        latest_diagnostics = latest.get("diagnostics", []) if isinstance(latest, dict) else []
        latest_recommendations = (
            latest.get("recommendations", []) if isinstance(latest, dict) else []
        )
        summary = {
            **summary,
            "restriction_score": self._float(restrictions.get("restriction_score")),
            "permission_score": self._float(permissions.get("permission_score")),
            "allowed_count": len(allowed) if isinstance(allowed, list) else 0,
            "forbidden_count": len(forbidden) if isinstance(forbidden, list) else 0,
            "warning_count": len(latest_diagnostics),
            "recommendation_count": len(latest_recommendations),
            "safety_boundary_only": True,
            "readiness_only": True,
            "research_only": True,
        }
        safety_chart = {
            "درجة السلامة": self._float(summary.get("safety_score")),
            "درجة الامتثال": self._float(summary.get("compliance_score")),
            "درجة القيود": self._float(summary.get("restriction_score")),
            "درجة الأذونات": self._float(summary.get("permission_score")),
        }
        restriction_chart = {
            "المسموحة": self._float(summary.get("allowed_count")),
            "المحظورة": self._float(summary.get("forbidden_count")),
            "المخالفات": self._float(len(restrictions.get("violations", []))),
        }
        allowed_chart = {str(value): 1.0 for value in allowed if isinstance(value, str)}
        forbidden_chart = {str(value): 1.0 for value in forbidden if isinstance(value, str)}
        audit_chart = {
            "المسموحة": self._float(len(audit.get("allowed_capabilities", []))),
            "المحظورة": self._float(len(audit.get("forbidden_capabilities", []))),
            "المخالفات": self._float(len(audit.get("detected_violations", []))),
            "التحذيرات": self._float(len(audit.get("warnings", []))),
        }
        return {
            "summary": summary,
            "latest": latest,
            "safety": bar_chart(
                "توزيع السلامة",
                *self._dict_chart_values(safety_chart),
                label="توزيع السلامة",
                color="green",
            ).to_dict(),
            "compliance": bar_chart(
                "توزيع الامتثال",
                *self._dict_chart_values(compliance),
                label="توزيع الامتثال",
                color="blue",
            ).to_dict(),
            "restrictions": bar_chart(
                "توزيع القيود",
                *self._dict_chart_values(restriction_chart),
                label="توزيع القيود",
                color="warning",
            ).to_dict(),
            "allowed": bar_chart(
                "القدرات المسموحة",
                *self._dict_chart_values(allowed_chart),
                label="القدرات المسموحة",
                color="green",
            ).to_dict(),
            "forbidden": bar_chart(
                "القدرات المحظورة",
                *self._dict_chart_values(forbidden_chart),
                label="القدرات المحظورة",
                color="warning",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "boundary": bar_chart(
                "حالة الحدود",
                *self._dict_chart_values(
                    {str(summary.get("boundary_status")): summary.get("safety_score")}
                ),
                label="حالة الحدود",
                color="accent",
            ).to_dict(),
            "audit": bar_chart(
                "سجل التدقيق",
                *self._dict_chart_values(audit_chart),
                label="سجل التدقيق",
                color="blue",
            ).to_dict(),
        }

    def architecture_audit_analytics(self) -> dict[str, Any]:
        """Return latest architecture-audit-only hardening analytics."""
        payload = self._latest_json_dict("architecture_audit", "architecture_summary")
        consistency = self._latest_json_dict("architecture_audit", "consistency")
        dependency = self._latest_json_dict("architecture_audit", "dependency")
        performance = self._latest_json_dict("architecture_audit", "performance")
        safety = self._latest_json_dict("architecture_audit", "safety")
        diagnostics = self._latest_json_dict("architecture_audit", "diagnostics")
        recommendations = self._latest_json_dict(
            "architecture_audit",
            "recommendations",
        )
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            summary = {
                "architecture_score": 0.0,
                "consistency_score": 0.0,
                "dependency_score": 0.0,
                "performance_score": 0.0,
                "safety_score": 0.0,
                "overall_score": 0.0,
                "certification_state": "تحتاج مراجعة",
                "architecture_audit_only": True,
                "hardening_only": True,
                "research_only": True,
            }
        latest_diagnostics = latest.get("diagnostics", []) if isinstance(latest, dict) else []
        latest_recommendations = (
            latest.get("recommendations", []) if isinstance(latest, dict) else []
        )
        summary = {
            **summary,
            "warning_count": len(latest_diagnostics),
            "recommendation_count": len(latest_recommendations),
            "architecture_audit_only": True,
            "hardening_only": True,
            "research_only": True,
        }
        scores = {
            "المعمارية": self._float(summary.get("architecture_score")),
            "الاتساق": self._float(summary.get("consistency_score")),
            "الاعتمادية": self._float(summary.get("dependency_score")),
            "الأداء": self._float(summary.get("performance_score")),
            "السلامة": self._float(summary.get("safety_score")),
        }
        consistency_chart = {
            "التقارير": self._float(consistency.get("report_count")),
            "التخزين": self._float(consistency.get("storage_count")),
            "القوالب": self._float(consistency.get("dashboard_template_count")),
            "واجهات API": self._float(consistency.get("api_route_count")),
        }
        safety_chart = {
            "السلامة": self._float(safety.get("safety_score")),
            "بدون تنفيذ": 100.0 if safety.get("no_execution_paths") else 0.0,
            "بدون وسيط": 100.0 if safety.get("no_broker_paths") else 0.0,
            "بدون مصادقة": 100.0 if safety.get("no_login_auth_paths") else 0.0,
            "بدون أتمتة": 100.0 if safety.get("no_automation_paths") else 0.0,
        }
        return {
            "summary": summary,
            "latest": latest,
            "scores": bar_chart(
                "درجات التدقيق",
                *self._dict_chart_values(scores),
                label="درجات التدقيق",
                color="green",
            ).to_dict(),
            "consistency": bar_chart(
                "اتساق التقارير",
                *self._dict_chart_values(consistency_chart),
                label="اتساق التقارير",
                color="blue",
            ).to_dict(),
            "safety": bar_chart(
                "السلامة",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="green",
            ).to_dict(),
            "performance": bar_chart(
                "الأداء",
                *self._dict_chart_values(performance),
                label="الأداء",
                color="warning",
            ).to_dict(),
            "dependency": bar_chart(
                "الاعتمادية",
                *self._dict_chart_values(dependency),
                label="الاعتمادية",
                color="accent",
            ).to_dict(),
            "certification": bar_chart(
                "حالة الاعتماد النهائي",
                *self._dict_chart_values(
                    {str(summary.get("certification_state")): summary.get("overall_score")}
                ),
                label="حالة الاعتماد النهائي",
                color="blue",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def knowledge_graph_analytics(self) -> dict[str, Any]:
        """Return latest research-only knowledge graph analytics."""
        payload = self._latest_json_dict("knowledge_graph", "knowledge_summary")
        nodes = self._latest_json_dict("knowledge_graph", "node")
        edges = self._latest_json_dict("knowledge_graph", "edge")
        analytics = self._latest_json_dict("knowledge_graph", "analytics")
        diagnostics = self._latest_json_dict("knowledge_graph", "diagnostics")
        recommendations = self._latest_json_dict(
            "knowledge_graph",
            "recommendations",
        )
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            summary = {
                "node_count": 0,
                "edge_count": 0,
                "strongest_relationship": "غير متاح",
                "weakest_relationship": "غير متاح",
                "relationship_density": 0.0,
                "knowledge_score": 0.0,
                "research_only": True,
            }
        latest_diagnostics = latest.get("diagnostics", []) if isinstance(latest, dict) else []
        latest_recommendations = (
            latest.get("recommendations", []) if isinstance(latest, dict) else []
        )
        summary = {
            **summary,
            "warning_count": len(latest_diagnostics),
            "recommendation_count": len(latest_recommendations),
            "research_only": True,
        }
        strongest = analytics.get("strongest_relationships", {})
        weakest = analytics.get("weakest_relationships", {})
        density = analytics.get("relationship_density", {})
        quality = analytics.get("graph_quality", {})
        activity = {
            "العقد": self._float(summary.get("node_count")),
            "العلاقات": self._float(summary.get("edge_count")),
            "التحذيرات": self._float(summary.get("warning_count")),
            "التوصيات": self._float(summary.get("recommendation_count")),
        }
        return {
            "summary": summary,
            "latest": latest,
            "edges": bar_chart(
                "توزيع العلاقات",
                *self._dict_chart_values(edges),
                label="توزيع العلاقات",
                color="blue",
            ).to_dict(),
            "nodes": bar_chart(
                "توزيع العقد",
                *self._dict_chart_values(nodes),
                label="توزيع العقد",
                color="green",
            ).to_dict(),
            "strongest": bar_chart(
                "أقوى العلاقات",
                *self._dict_chart_values(strongest),
                label="أقوى العلاقات",
                color="green",
            ).to_dict(),
            "weakest": bar_chart(
                "أضعف العلاقات",
                *self._dict_chart_values(weakest),
                label="أضعف العلاقات",
                color="warning",
            ).to_dict(),
            "density": bar_chart(
                "كثافة المعرفة",
                *self._dict_chart_values(density),
                label="كثافة المعرفة",
                color="blue",
            ).to_dict(),
            "quality": bar_chart(
                "جودة المعرفة",
                *self._dict_chart_values(quality),
                label="جودة المعرفة",
                color="accent",
            ).to_dict(),
            "warnings": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "activity": line_chart(
                "النشاط الزمني",
                *self._dict_chart_values(activity),
                label="النشاط الزمني",
                color="blue",
            ).to_dict(),
        }

    def research_api_analytics(self) -> dict[str, Any]:
        """Return latest unified research API dashboard analytics."""
        payload = self._latest_json_dict("research_api", "research_summary")
        diagnostics = self._latest_json_dict("research_api", "diagnostics")
        recommendations = self._latest_json_dict("research_api", "recommendations")
        summary_payload = payload if isinstance(payload, dict) else {}
        metadata = summary_payload.get("metadata", {})
        labels = summary_payload.get("labels_ar", {})
        if not isinstance(metadata, dict):
            metadata = {}
        if not isinstance(labels, dict):
            labels = {}
        views = {
            "الإشارات": 100.0 if summary_payload.get("signals", {}).get("available") else 0.0,
            "الفرص": 100.0 if summary_payload.get("opportunities", {}).get("available") else 0.0,
            "الورقي": 100.0 if summary_payload.get("paper", {}).get("available") else 0.0,
            "الجاهزية": 100.0 if summary_payload.get("readiness", {}).get("available") else 0.0,
            "خريطة المعرفة": (
                100.0 if summary_payload.get("knowledge_graph", {}).get("available") else 0.0
            ),
        }
        available_views = sum(1 for value in views.values() if value > 0)
        diag_data = (
            summary_payload.get("diagnostics", {}).get("data", {})
            if isinstance(summary_payload.get("diagnostics"), dict)
            else {}
        )
        diag_summary = diag_data.get("summary", {}) if isinstance(diag_data, dict) else {}
        source_count = self._float(diag_summary.get("available_source_count")) + self._float(
            diag_summary.get("missing_source_count")
        )
        summary = {
            "available_views": available_views,
            "source_count": source_count,
            "available_sources": self._float(diag_summary.get("available_source_count")),
            "missing_source_count": self._float(diag_summary.get("missing_source_count")),
            "schema_version": metadata.get("schema_version", "research_api.v1"),
            "stable_json_schema": 100.0 if metadata.get("stable_json_schema") else 0.0,
            "signals_available": views["الإشارات"],
            "opportunities_available": views["الفرص"],
            "paper_available": views["الورقي"],
            "readiness_available": views["الجاهزية"],
            "knowledge_graph_available": views["خريطة المعرفة"],
            "research_only": True,
            "local_only": True,
        }
        source_chart = {
            "المتاحة": summary["available_sources"],
            "الناقصة": summary["missing_source_count"],
        }
        label_chart = {str(value): 1.0 for value in labels.values()}
        safety_chart = {
            "بحث فقط": 100.0 if summary_payload.get("research_only") else 0.0,
            "محلي فقط": 100.0 if summary_payload.get("local_only") else 0.0,
            "بدون تنفيذ": 100.0 if summary_payload.get("not_execution") else 0.0,
            "بدون وسيط": 100.0 if summary_payload.get("not_broker_access") else 0.0,
            "بدون متصفح": (100.0 if summary_payload.get("not_browser_automation") else 0.0),
        }
        return {
            "summary": summary,
            "snapshot": summary_payload,
            "views": bar_chart(
                "الواجهات الموحدة",
                *self._dict_chart_values(views),
                label="الواجهات الموحدة",
                color="green",
            ).to_dict(),
            "sources": bar_chart(
                "المصادر البحثية",
                *self._dict_chart_values(source_chart),
                label="المصادر البحثية",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التشخيص الموحد",
                *self._dict_chart_values(diagnostics.get("data", diagnostics)),
                label="التشخيص الموحد",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات الموحدة",
                *self._dict_chart_values(recommendations.get("data", recommendations)),
                label="التوصيات الموحدة",
                color="green",
            ).to_dict(),
            "labels": bar_chart(
                "تسميات عربية",
                *self._dict_chart_values(label_chart),
                label="تسميات عربية",
                color="accent",
            ).to_dict(),
            "safety": bar_chart(
                "حدود السلامة",
                *self._dict_chart_values(safety_chart),
                label="حدود السلامة",
                color="green",
            ).to_dict(),
        }

    def research_archive_analytics(self) -> dict[str, Any]:
        """Return latest research archive and versioning analytics."""
        summary = self._latest_json_dict("research_archive", "archive_summary")
        latest = self._latest_json_dict("research_archive", "latest_version_report")
        diff = self._latest_json_dict("research_archive", "diff_report")
        evolution = self._latest_json_dict("research_archive", "evolution_report")
        diagnostics_payload = self._latest_json_list(
            "research_archive",
            "diagnostics_report",
        )
        recommendations_payload = self._latest_json_dict(
            "research_archive",
            "recommendations_report",
        )
        history = self._latest_json_list("research_archive", "version_history")
        recommendations = recommendations_payload.get("items", [])
        if not isinstance(recommendations, list):
            recommendations = []
        safety = summary.get("safety_status", {}) if isinstance(summary, dict) else {}
        coverage = {
            "المؤرشفة": self._float(summary.get("archived_source_count")),
            "المفقودة": self._float(summary.get("missing_source_count")),
        }
        trends = {
            "جودة البحث": self._trend_score(evolution.get("research_quality_trend")),
            "الجاهزية": self._trend_score(evolution.get("readiness_trend")),
            "خريطة المعرفة": self._trend_score(evolution.get("knowledge_score_trend")),
            "تغطية المصادر": self._trend_score(evolution.get("source_coverage_trend")),
        }
        diff_chart = {
            "المضافة": self._float(len(diff.get("added_keys", []))),
            "المحذوفة": self._float(len(diff.get("removed_keys", []))),
            "المتغيرة": self._float(len(diff.get("changed_values", []))),
            "المحسنة": self._float(len(diff.get("improved_metrics", []))),
            "المتراجعة": self._float(len(diff.get("degraded_metrics", []))),
        }
        history_chart = {
            str(item.get("version_label", index + 1)): index + 1.0
            for index, item in enumerate(history)
        }
        diagnostics_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics_payload)
        }
        recommendations_chart = {str(item): 1.0 for item in recommendations}
        safety_chart = {
            "بحث فقط": 100.0 if safety.get("research_only") else 0.0,
            "محلي فقط": 100.0 if safety.get("local_only") else 0.0,
            "بدون وسيط": 100.0 if safety.get("no_broker_access") else 0.0,
            "بدون متصفح": 100.0 if safety.get("no_browser_automation") else 0.0,
            "بدون أموال": 100.0 if safety.get("no_money_handling") else 0.0,
        }
        archive_summary = {
            "latest_version": summary.get("latest_version", latest.get("version_label")),
            "version_count": self._float(summary.get("version_count")),
            "latest_snapshot": summary.get("latest_snapshot"),
            "archived_source_count": self._float(summary.get("archived_source_count")),
            "missing_source_count": self._float(summary.get("missing_source_count")),
            "checksum": summary.get("checksum"),
            "safety_status": "بحث فقط" if safety.get("research_only") else "مراجعة",
            "research_quality_trend": evolution.get("research_quality_trend", "غير كاف للتقييم"),
            "readiness_trend": evolution.get("readiness_trend", "غير كاف للتقييم"),
            "knowledge_trend": evolution.get("knowledge_score_trend", "غير كاف للتقييم"),
            "diagnostics_count": self._float(summary.get("diagnostics_count")),
            "recommendation_count": self._float(summary.get("recommendation_count")),
            "research_only": True,
            "local_only": True,
        }
        return {
            "summary": archive_summary,
            "latest": latest,
            "diff": diff,
            "evolution": evolution,
            "diagnostics_items": diagnostics_payload,
            "recommendations_items": recommendations,
            "version_history": history,
            "history": bar_chart(
                "تاريخ الإصدارات",
                *self._dict_chart_values(history_chart),
                label="الإصدارات",
                color="blue",
            ).to_dict(),
            "coverage": bar_chart(
                "تغطية المصادر",
                *self._dict_chart_values(coverage),
                label="المصادر",
                color="green",
            ).to_dict(),
            "trends": bar_chart(
                "اتجاه جودة البحث",
                *self._dict_chart_values(trends),
                label="الاتجاه",
                color="accent",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendations_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "diff_chart": bar_chart(
                "الفروقات بين الإصدارات",
                *self._dict_chart_values(diff_chart),
                label="الفروقات",
                color="blue",
            ).to_dict(),
            "safety": bar_chart(
                "حالة الأمان",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="green",
            ).to_dict(),
        }

    def platform_certification_analytics(self) -> dict[str, Any]:
        """Return latest final research platform certification analytics."""
        report = self._latest_json_dict(
            "platform_certification",
            "certification_report",
        )
        executive = self._latest_json_dict(
            "platform_certification",
            "executive_summary",
        )
        domains = self._latest_json_list("platform_certification", "domain_report")
        diagnostics = self._latest_json_list(
            "platform_certification",
            "diagnostics_report",
        )
        recommendations = self._latest_json_list(
            "platform_certification",
            "recommendations_report",
        )
        summary = {
            "final_platform_score": self._float(
                executive.get("final_platform_score", report.get("final_platform_score"))
            ),
            "certification_state": executive.get(
                "certification_state",
                report.get("certification_state", "Not Certified"),
            ),
            "research_maturity_level": executive.get(
                "research_maturity_level",
                report.get("research_maturity_level", "غير متاح"),
            ),
            "maturity_score": self._float(
                executive.get("maturity_score", report.get("maturity_score"))
            ),
            "domain_count": self._float(len(domains)),
            "diagnostics_count": self._float(len(diagnostics)),
            "recommendation_count": self._float(len(recommendations)),
            "research_only": True,
            "local_only": True,
        }
        domain_scores = {
            str(item.get("label_ar", item.get("domain_id"))): self._float(item.get("score"))
            for item in domains
        }
        diagnostics_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {str(item): 1.0 for item in recommendations}
        maturity_chart = {
            "النضج البحثي": summary["maturity_score"],
            "الدرجة النهائية": summary["final_platform_score"],
        }
        state_chart = {
            "Not Certified": 100.0 if summary["certification_state"] == "Not Certified" else 0.0,
            "Conditionally Certified": (
                100.0 if summary["certification_state"] == "Conditionally Certified" else 0.0
            ),
            "Certified For Advanced Research": (
                100.0
                if summary["certification_state"] == "Certified For Advanced Research"
                else 0.0
            ),
        }
        return {
            "summary": summary,
            "report": report,
            "domains": domains,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "domain_scores": bar_chart(
                "درجات المجالات",
                *self._dict_chart_values(domain_scores),
                label="درجات المجالات",
                color="green",
            ).to_dict(),
            "maturity": bar_chart(
                "النضج البحثي",
                *self._dict_chart_values(maturity_chart),
                label="النضج",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "state": bar_chart(
                "حالة الشهادة",
                *self._dict_chart_values(state_chart),
                label="الشهادة",
                color="accent",
            ).to_dict(),
        }

    def release_packaging_analytics(self) -> dict[str, Any]:
        """Return latest release packaging analytics."""
        summary_payload = self._latest_json_dict("release_packaging", "release_summary")
        manifest = self._latest_json_dict(
            "release_packaging",
            "release_manifest_report",
        )
        status = self._latest_json_dict(
            "release_packaging",
            "project_status_report",
        )
        audit = self._latest_json_dict(
            "release_packaging",
            "repository_audit_report",
        )
        diagnostics = self._latest_json_list("release_packaging", "diagnostics_report")
        recommendations = self._latest_json_list(
            "release_packaging",
            "recommendations_report",
        )
        release_status = summary_payload.get(
            "release_status",
            manifest.get("release_status", "Not Ready"),
        )
        summary = {
            "release_id": manifest.get("release_id", "research-platform-v1.0"),
            "release_status": release_status,
            "certification_state": manifest.get(
                "certification_state",
                summary_payload.get("certification_state", "Not Certified"),
            ),
            "test_count": self._float(manifest.get("test_count", 260)),
            "phase_count": self._float(len(manifest.get("completed_phases", []))),
            "dashboard_page_count": self._float(len(manifest.get("dashboard_pages", []))),
            "api_endpoint_count": self._float(len(manifest.get("api_endpoints", []))),
            "script_count": self._float(len(manifest.get("scripts", []))),
            "test_file_count": self._float(len(manifest.get("tests", []))),
            "report_count": self._float(len(manifest.get("reports", []))),
            "storage_count": self._float(len(manifest.get("storage_outputs", []))),
            "safety_status": "بحث فقط",
            "diagnostics_count": self._float(len(diagnostics)),
            "recommendation_count": self._float(len(recommendations)),
            "recommended_next_decision": status.get(
                "recommended_next_decision",
                "Run targeted cleanup before release",
            ),
            "research_only": True,
            "local_only": True,
        }
        components = {
            "الصفحات": summary["dashboard_page_count"],
            "واجهات API": summary["api_endpoint_count"],
            "السكريبتات": summary["script_count"],
            "الاختبارات": summary["test_file_count"],
            "التقارير": summary["report_count"],
            "التخزين": summary["storage_count"],
        }
        phases = {
            "المراحل المكتملة": summary["phase_count"],
            "النطاق": 55.0,
        }
        validation = {
            "الاختبارات": summary["test_count"],
            "التحذيرات": summary["diagnostics_count"],
        }
        safety = {
            str(key): 100.0 if value else 0.0
            for key, value in manifest.get("safety_boundary", {}).items()
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {str(item): 1.0 for item in recommendations}
        readiness = {
            "Ready For Research Release": (
                100.0 if release_status == "Ready For Research Release" else 0.0
            ),
            "Ready With Warnings": 100.0 if release_status == "Ready With Warnings" else 0.0,
            "Not Ready": 100.0 if release_status == "Not Ready" else 0.0,
        }
        return {
            "summary": summary,
            "manifest": manifest,
            "project_status": status,
            "repository_audit": audit,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "components": bar_chart(
                "توزيع مكونات الإصدار",
                *self._dict_chart_values(components),
                label="المكونات",
                color="blue",
            ).to_dict(),
            "phases": bar_chart(
                "تغطية المراحل",
                *self._dict_chart_values(phases),
                label="المراحل",
                color="green",
            ).to_dict(),
            "validation": bar_chart(
                "حالة التحقق",
                *self._dict_chart_values(validation),
                label="التحقق",
                color="accent",
            ).to_dict(),
            "safety": bar_chart(
                "حالة الأمان",
                *self._dict_chart_values(safety),
                label="الأمان",
                color="green",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "readiness": bar_chart(
                "جاهزية الإصدار",
                *self._dict_chart_values(readiness),
                label="الإصدار",
                color="blue",
            ).to_dict(),
        }

    def post_research_architecture_analytics(self) -> dict[str, Any]:
        """Return latest post-research strategic architecture analytics."""
        summary_payload = self._latest_json_dict(
            "post_research_architecture",
            "post_research_summary",
        )
        roadmap = self._latest_json_dict(
            "post_research_architecture",
            "roadmap_report",
        )
        gaps = self._latest_json_dict(
            "post_research_architecture",
            "gap_analysis_report",
        )
        transition = self._latest_json_dict(
            "post_research_architecture",
            "transition_plan_report",
        )
        diagnostics = self._latest_json_list(
            "post_research_architecture",
            "diagnostics_report",
        )
        recommendations = self._latest_json_list(
            "post_research_architecture",
            "recommendations_report",
        )
        technical_gaps = gaps.get("technical_gaps", []) if isinstance(gaps, dict) else []
        summary = {
            "current_platform_state": summary_payload.get(
                "current_platform_state",
                "Research Platform v1.0",
            ),
            "recommended_future_program": summary_payload.get(
                "recommended_future_program",
                "Trading System Architecture Program",
            ),
            "architecture_separation_decision": summary_payload.get(
                "architecture_separation_decision",
                "Separate future program required",
            ),
            "gap_count": self._float(summary_payload.get("gap_count", len(technical_gaps))),
            "highest_gap_level": summary_payload.get("highest_gap_level", "حرج"),
            "future_execution_status": summary_payload.get(
                "future_execution_status",
                "Blueprint only; not implemented",
            ),
            "future_broker_status": summary_payload.get(
                "future_broker_status",
                "Blueprint only; not implemented",
            ),
            "risk_status": summary_payload.get(
                "risk_status",
                "Future governance design required",
            ),
            "monitoring_status": summary_payload.get(
                "monitoring_status",
                "Future monitoring design required",
            ),
            "governance_status": summary_payload.get(
                "governance_status",
                "Human approval gates required",
            ),
            "warning_count": self._float(summary_payload.get("warning_count", len(diagnostics))),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "first_safe_next_step": summary_payload.get(
                "first_safe_next_step",
                transition.get("first_safe_next_step", "غير متاح"),
            ),
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        gap_distribution: dict[str, float] = {}
        risk_distribution: dict[str, float] = {}
        domain_readiness: dict[str, float] = {}
        for item in technical_gaps:
            if not isinstance(item, dict):
                continue
            gap_level = str(item.get("gap_level", "غير متاح"))
            risk_level = str(item.get("risk_level", "غير متاح"))
            category = str(item.get("category", "غير متاح"))
            gap_distribution[gap_level] = gap_distribution.get(gap_level, 0.0) + 1.0
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0.0) + 1.0
            domain_readiness[category] = 100.0 if gap_level == "منخفض" else 25.0
        roadmap_stages = {
            str(stage): float(index + 1)
            for index, stage in enumerate(roadmap.get("roadmap_stages", []))
        }
        diagnostics_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {str(item): 1.0 for item in recommendations}
        transition_chart = {
            str(stage): float(index + 1)
            for index, stage in enumerate(transition.get("safe_transition_sequence", []))
        }
        return {
            "summary": summary,
            "roadmap": roadmap,
            "gap_analysis": gaps,
            "transition": transition,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "gap_distribution": bar_chart(
                "توزيع الفجوات",
                *self._dict_chart_values(gap_distribution),
                label="الفجوات",
                color="warning",
            ).to_dict(),
            "risk_levels": bar_chart(
                "مستويات المخاطر",
                *self._dict_chart_values(risk_distribution),
                label="المخاطر",
                color="warning",
            ).to_dict(),
            "roadmap_stages": bar_chart(
                "مراحل خارطة الطريق",
                *self._dict_chart_values(roadmap_stages),
                label="المراحل",
                color="blue",
            ).to_dict(),
            "domain_readiness": bar_chart(
                "جاهزية المجالات",
                *self._dict_chart_values(domain_readiness),
                label="الجاهزية",
                color="green",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostics_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "safe_transition": bar_chart(
                "تسلسل الانتقال الآمن",
                *self._dict_chart_values(transition_chart),
                label="الانتقال",
                color="accent",
            ).to_dict(),
        }

    def trading_architecture_program_analytics(self) -> dict[str, Any]:
        """Return latest trading architecture program analytics."""
        summary_payload = self._latest_json_dict(
            "trading_architecture_program",
            "program_summary",
        )
        domains = self._latest_json_list(
            "trading_architecture_program",
            "domain_report",
        )
        gates = self._latest_json_list("trading_architecture_program", "gate_report")
        workstreams = self._latest_json_list(
            "trading_architecture_program",
            "workstream_report",
        )
        diagnostics = self._latest_json_list(
            "trading_architecture_program",
            "diagnostics_report",
        )
        recommendations = self._latest_json_list(
            "trading_architecture_program",
            "recommendations_report",
        )
        summary = {
            "program_name": summary_payload.get(
                "program_name",
                "Trading System Architecture Program",
            ),
            "program_status": summary_payload.get(
                "program_status",
                "Architecture Program Foundation Only",
            ),
            "domain_count": self._float(summary_payload.get("domain_count", len(domains))),
            "workstream_count": self._float(
                summary_payload.get("workstream_count", len(workstreams))
            ),
            "gate_count": self._float(summary_payload.get("gate_count", len(gates))),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "architecture_only": True,
            "no_execution_capability": True,
            "no_broker_capability": True,
            "no_trading_capability": True,
        }
        domain_chart = {
            str(item.get("name", item.get("domain_id", index + 1))): 1.0
            for index, item in enumerate(domains)
        }
        gate_chart = {
            str(item.get("name", item.get("gate_id", index + 1))): 1.0
            for index, item in enumerate(gates)
        }
        workstream_chart = {
            str(item.get("name", item.get("workstream_id", index + 1))): 1.0
            for index, item in enumerate(workstreams)
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {str(item): 1.0 for item in recommendations}
        safety_chart = {
            "لا تنفيذ": 100.0,
            "لا وسيط": 100.0,
            "لا تداول": 100.0,
            "لا بيانات اعتماد": 100.0,
            "لا اتصال خارجي": 100.0,
        }
        return {
            "summary": summary,
            "domains_items": domains,
            "gates_items": gates,
            "workstreams_items": workstreams,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "domains": bar_chart(
                "المجالات المعمارية",
                *self._dict_chart_values(domain_chart),
                label="المجالات",
                color="blue",
            ).to_dict(),
            "gates": bar_chart(
                "بوابات القرار",
                *self._dict_chart_values(gate_chart),
                label="البوابات",
                color="green",
            ).to_dict(),
            "workstreams": bar_chart(
                "مسارات العمل",
                *self._dict_chart_values(workstream_chart),
                label="المسارات",
                color="accent",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التشخيصات",
                *self._dict_chart_values(diagnostic_chart),
                label="التشخيصات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "safety": bar_chart(
                "حدود السلامة",
                *self._dict_chart_values(safety_chart),
                label="السلامة",
                color="green",
            ).to_dict(),
        }

    def trading_requirements_analytics(self) -> dict[str, Any]:
        """Return latest trading requirements analytics."""
        summary_payload = self._latest_json_dict("trading_requirements", "requirements_summary")
        coverage = self._latest_json_dict("trading_requirements", "coverage_summary")
        go_no_go = self._latest_json_dict("trading_requirements", "go_no_go")
        diagnostics = self._latest_json_list("trading_requirements", "diagnostics_report")
        recommendations = self._latest_json_list(
            "trading_requirements",
            "recommendations_report",
        )
        documents = {
            "functional": self._latest_json_dict(
                "trading_requirements",
                "functional_requirements_report",
            ),
            "non_functional": self._latest_json_dict(
                "trading_requirements",
                "non_functional_requirements_report",
            ),
            "safety": self._latest_json_dict(
                "trading_requirements",
                "safety_requirements_report",
            ),
            "risk": self._latest_json_dict(
                "trading_requirements",
                "risk_requirements_report",
            ),
            "compliance": self._latest_json_dict(
                "trading_requirements",
                "compliance_constraints_report",
            ),
            "broker": self._latest_json_dict(
                "trading_requirements",
                "broker_constraints_report",
            ),
            "execution": self._latest_json_dict(
                "trading_requirements",
                "execution_constraints_report",
            ),
            "monitoring": self._latest_json_dict(
                "trading_requirements",
                "monitoring_constraints_report",
            ),
            "data": self._latest_json_dict(
                "trading_requirements",
                "data_constraints_report",
            ),
        }
        requirement_count = self._float(
            summary_payload.get("requirement_count", coverage.get("requirement_count"))
        )
        constraint_count = self._float(
            summary_payload.get("constraint_count", coverage.get("constraint_count"))
        )
        summary = {
            "requirements_status": summary_payload.get(
                "requirements_status",
                "Requirements Incomplete",
            ),
            "requirement_count": requirement_count,
            "constraint_count": constraint_count,
            "highest_priority": summary_payload.get(
                "highest_priority",
                coverage.get("highest_priority", "مرتفع"),
            ),
            "go_no_go_state": summary_payload.get(
                "go_no_go_state",
                go_no_go.get("decision_state", "Not Ready"),
            ),
            "safety_requirement_count": self._float(coverage.get("safety_requirement_count", 0)),
            "risk_requirement_count": self._float(coverage.get("risk_requirement_count", 0)),
            "compliance_constraint_count": self._float(
                coverage.get("compliance_constraint_count", 0)
            ),
            "execution_constraint_count": self._float(
                coverage.get("execution_constraint_count", 0)
            ),
            "broker_constraint_count": self._float(coverage.get("broker_constraint_count", 0)),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "requirements_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        requirement_distribution = {
            label: self._float(len(doc.get("items", [])))
            for label, doc in documents.items()
            if label in {"functional", "non_functional", "safety", "risk"}
        }
        constraint_distribution = {
            label: self._float(len(doc.get("items", [])))
            for label, doc in documents.items()
            if label not in {"functional", "non_functional", "safety", "risk"}
        }
        priorities: dict[str, float] = {}
        for doc in documents.values():
            for item in doc.get("items", []):
                priority = str(item.get("priority", "متوسط"))
                priorities[priority] = priorities.get(priority, 0.0) + 1.0
        decision = {
            "Not Ready": 100.0 if summary["go_no_go_state"] == "Not Ready" else 0.0,
            "Requirements Incomplete": (
                100.0 if summary["go_no_go_state"] == "Requirements Incomplete" else 0.0
            ),
            "Ready For Architecture Review": (
                100.0 if summary["go_no_go_state"] == "Ready For Architecture Review" else 0.0
            ),
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {str(item): 1.0 for item in recommendations}
        return {
            "summary": summary,
            "coverage": coverage,
            "go_no_go": go_no_go,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "requirements_distribution": bar_chart(
                "توزيع المتطلبات",
                *self._dict_chart_values(requirement_distribution),
                label="المتطلبات",
                color="blue",
            ).to_dict(),
            "constraints_distribution": bar_chart(
                "توزيع القيود",
                *self._dict_chart_values(constraint_distribution),
                label="القيود",
                color="warning",
            ).to_dict(),
            "priorities": bar_chart(
                "مستويات الأولوية",
                *self._dict_chart_values(priorities),
                label="الأولوية",
                color="accent",
            ).to_dict(),
            "coverage_chart": bar_chart(
                "تغطية المتطلبات",
                ["المتطلبات", "القيود"],
                [requirement_count, constraint_count],
                label="التغطية",
                color="green",
            ).to_dict(),
            "go_no_go_chart": bar_chart(
                "حالة Go/No-Go",
                *self._dict_chart_values(decision),
                label="القرار",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def production_system_design_analytics(self) -> dict[str, Any]:
        """Return latest production system design analytics."""
        summary_payload = self._latest_json_dict(
            "production_system_design",
            "production_design_summary",
        )
        documents = {
            "topology": self._latest_json_dict(
                "production_system_design",
                "topology_report",
            ),
            "service_boundaries": self._latest_json_dict(
                "production_system_design",
                "service_boundaries_report",
            ),
            "runtime_architecture": self._latest_json_dict(
                "production_system_design",
                "runtime_architecture_report",
            ),
            "environment_strategy": self._latest_json_dict(
                "production_system_design",
                "environment_strategy_report",
            ),
            "configuration_strategy": self._latest_json_dict(
                "production_system_design",
                "configuration_strategy_report",
            ),
            "secrets_strategy": self._latest_json_dict(
                "production_system_design",
                "secrets_strategy_report",
            ),
            "database_strategy": self._latest_json_dict(
                "production_system_design",
                "database_strategy_report",
            ),
            "event_queue_strategy": self._latest_json_dict(
                "production_system_design",
                "event_queue_strategy_report",
            ),
            "logging_strategy": self._latest_json_dict(
                "production_system_design",
                "logging_strategy_report",
            ),
            "monitoring_strategy": self._latest_json_dict(
                "production_system_design",
                "monitoring_strategy_report",
            ),
            "alerting_strategy": self._latest_json_dict(
                "production_system_design",
                "alerting_strategy_report",
            ),
            "incident_response": self._latest_json_dict(
                "production_system_design",
                "incident_response_report",
            ),
            "backup_recovery": self._latest_json_dict(
                "production_system_design",
                "backup_recovery_report",
            ),
            "release_rollback": self._latest_json_dict(
                "production_system_design",
                "release_rollback_report",
            ),
            "readiness_gates": self._latest_json_dict(
                "production_system_design",
                "readiness_gates_report",
            ),
        }
        diagnostics = self._latest_json_list(
            "production_system_design",
            "diagnostics_report",
        )
        reports = self.loader.list_reports()
        recommendations_report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            "production_system_design",
            "recommendations_report",
        )
        recommendations_content = (
            self.loader.get_report(recommendations_report.report_id)
            if recommendations_report
            else None
        )
        recommendations_payload = (
            recommendations_content.json_data if recommendations_content else []
        )
        recommendations = (
            [str(item) for item in recommendations_payload]
            if isinstance(recommendations_payload, list)
            else []
        )
        readiness = documents["readiness_gates"]
        gates = readiness.get("gates", []) if isinstance(readiness, dict) else []
        summary = {
            "design_status": summary_payload.get("design_status", "Design Incomplete"),
            "design_domain_count": self._float(summary_payload.get("design_domain_count", 14)),
            "service_boundary_count": self._float(
                summary_payload.get(
                    "service_boundary_count",
                    len(documents["service_boundaries"].get("items", [])),
                )
            ),
            "environment_strategy_status": summary_payload.get(
                "environment_strategy_status",
                "Design only",
            ),
            "configuration_strategy_status": summary_payload.get(
                "configuration_strategy_status",
                "Design only",
            ),
            "secrets_strategy_status": summary_payload.get(
                "secrets_strategy_status",
                "Design only",
            ),
            "database_strategy_status": summary_payload.get(
                "database_strategy_status",
                "Design only",
            ),
            "event_queue_strategy_status": summary_payload.get(
                "event_queue_strategy_status",
                "Design only",
            ),
            "monitoring_status": summary_payload.get("monitoring_status", "Design only"),
            "alerting_status": summary_payload.get("alerting_status", "Design only"),
            "incident_response_status": summary_payload.get(
                "incident_response_status",
                "Design only",
            ),
            "backup_recovery_status": summary_payload.get(
                "backup_recovery_status",
                "Design only",
            ),
            "release_rollback_status": summary_payload.get(
                "release_rollback_status",
                "Design only",
            ),
            "readiness_state": summary_payload.get(
                "readiness_state",
                readiness.get("readiness_state", "Not Ready"),
            ),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "design_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        domain_distribution = {
            label: self._float(len(doc.get("items", [])))
            for label, doc in documents.items()
            if label != "readiness_gates"
        }
        boundary_status = {
            str(item.get("status", "Design only")): 0.0
            for item in documents["service_boundaries"].get("items", [])
        }
        for item in documents["service_boundaries"].get("items", []):
            status = str(item.get("status", "Design only"))
            boundary_status[status] = boundary_status.get(status, 0.0) + 1.0
        priorities: dict[str, float] = {}
        for doc in documents.values():
            for item in doc.get("items", []):
                priority = str(item.get("priority", "متوسط"))
                priorities[priority] = priorities.get(priority, 0.0) + 1.0
        readiness_chart = {
            "Not Ready": 100.0 if summary["readiness_state"] == "Not Ready" else 0.0,
            "Design Incomplete": (
                100.0 if summary["readiness_state"] == "Design Incomplete" else 0.0
            ),
            "Ready For Design Review": (
                100.0 if summary["readiness_state"] == "Ready For Design Review" else 0.0
            ),
        }
        gate_chart: dict[str, float] = {}
        for gate in gates:
            status = str(gate.get("current_status", "missing"))
            gate_chart[status] = gate_chart.get(status, 0.0) + 1.0
        operational_status = {
            "monitoring": 1.0 if summary["monitoring_status"] == "Design only" else 0.0,
            "alerting": 1.0 if summary["alerting_status"] == "Design only" else 0.0,
            "incidents": 1.0 if summary["incident_response_status"] == "Design only" else 0.0,
            "backup": 1.0 if summary["backup_recovery_status"] == "Design only" else 0.0,
            "release": 1.0 if summary["release_rollback_status"] == "Design only" else 0.0,
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {item: 1.0 for item in recommendations}
        return {
            "summary": summary,
            "documents": documents,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "design_domains": bar_chart(
                "توزيع مجالات التصميم",
                *self._dict_chart_values(domain_distribution),
                label="مجالات التصميم",
                color="blue",
            ).to_dict(),
            "service_boundaries": bar_chart(
                "حالة حدود الخدمات",
                *self._dict_chart_values(boundary_status),
                label="حدود الخدمات",
                color="accent",
            ).to_dict(),
            "readiness": bar_chart(
                "حالة الجاهزية",
                *self._dict_chart_values(readiness_chart),
                label="الجاهزية",
                color="warning",
            ).to_dict(),
            "readiness_gates": bar_chart(
                "بوابات الجاهزية",
                *self._dict_chart_values(gate_chart),
                label="البوابات",
                color="warning",
            ).to_dict(),
            "priorities": bar_chart(
                "مستويات الأولوية",
                *self._dict_chart_values(priorities),
                label="الأولوية",
                color="green",
            ).to_dict(),
            "operations_status": bar_chart(
                "تصميم التشغيل والمراقبة",
                *self._dict_chart_values(operational_status),
                label="الحالة",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التشخيص",
                *self._dict_chart_values(diagnostic_chart),
                label="التشخيص",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def operational_governance_analytics(self) -> dict[str, Any]:
        """Return latest operational governance analytics."""
        summary_payload = self._latest_json_dict(
            "operational_governance",
            "operational_governance_summary",
        )
        documents = {
            "authority_model": self._latest_json_dict(
                "operational_governance",
                "authority_model_report",
            ),
            "approval_workflows": self._latest_json_dict(
                "operational_governance",
                "approval_workflows_report",
            ),
            "change_management": self._latest_json_dict(
                "operational_governance",
                "change_management_report",
            ),
            "release_governance": self._latest_json_dict(
                "operational_governance",
                "release_governance_report",
            ),
            "incident_escalation": self._latest_json_dict(
                "operational_governance",
                "incident_escalation_report",
            ),
            "kill_switch_governance": self._latest_json_dict(
                "operational_governance",
                "kill_switch_governance_report",
            ),
            "audit_controls": self._latest_json_dict(
                "operational_governance",
                "audit_controls_report",
            ),
            "operator_responsibility": self._latest_json_dict(
                "operational_governance",
                "operator_responsibility_report",
            ),
            "review_boards": self._latest_json_dict(
                "operational_governance",
                "review_boards_report",
            ),
            "decision_matrix": self._latest_json_dict(
                "operational_governance",
                "decision_matrix_report",
            ),
            "control_evidence": self._latest_json_dict(
                "operational_governance",
                "control_evidence_report",
            ),
            "policy_registry": self._latest_json_dict(
                "operational_governance",
                "policy_registry_report",
            ),
            "readiness_gates": self._latest_json_dict(
                "operational_governance",
                "readiness_gates_report",
            ),
        }
        diagnostics = self._latest_json_list(
            "operational_governance",
            "diagnostics_report",
        )
        reports = self.loader.list_reports()
        recommendations_report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            "operational_governance",
            "recommendations_report",
        )
        recommendations_content = (
            self.loader.get_report(recommendations_report.report_id)
            if recommendations_report
            else None
        )
        recommendation_payload = (
            recommendations_content.json_data if recommendations_content else []
        )
        recommendations = (
            [str(item) for item in recommendation_payload]
            if isinstance(recommendation_payload, list)
            else []
        )
        readiness = documents["readiness_gates"]
        gates = readiness.get("gates", []) if isinstance(readiness, dict) else []
        summary = {
            "governance_status": summary_payload.get(
                "governance_status",
                "Governance Incomplete",
            ),
            "governance_domain_count": self._float(
                summary_payload.get("governance_domain_count", 12)
            ),
            "authority_role_count": self._float(
                summary_payload.get(
                    "authority_role_count",
                    len(documents["authority_model"].get("items", [])),
                )
            ),
            "approval_workflow_count": self._float(
                summary_payload.get(
                    "approval_workflow_count",
                    len(documents["approval_workflows"].get("items", [])),
                )
            ),
            "change_control_count": self._float(
                summary_payload.get(
                    "change_control_count",
                    len(documents["change_management"].get("items", [])),
                )
            ),
            "release_governance_status": summary_payload.get(
                "release_governance_status",
                "Governance only",
            ),
            "incident_escalation_status": summary_payload.get(
                "incident_escalation_status",
                "Governance only",
            ),
            "kill_switch_governance_status": summary_payload.get(
                "kill_switch_governance_status",
                "Governance only",
            ),
            "audit_control_count": self._float(
                summary_payload.get(
                    "audit_control_count",
                    len(documents["audit_controls"].get("items", [])),
                )
            ),
            "review_board_count": self._float(
                summary_payload.get(
                    "review_board_count",
                    len(documents["review_boards"].get("items", [])),
                )
            ),
            "decision_rule_count": self._float(
                summary_payload.get(
                    "decision_rule_count",
                    len(documents["decision_matrix"].get("items", [])),
                )
            ),
            "policy_count": self._float(
                summary_payload.get(
                    "policy_count",
                    len(documents["policy_registry"].get("items", [])),
                )
            ),
            "readiness_state": summary_payload.get(
                "readiness_state",
                readiness.get("readiness_state", "Not Ready"),
            ),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "governance_only": True,
            "design_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        domain_distribution = {
            label: self._float(len(doc.get("items", [])))
            for label, doc in documents.items()
            if label != "readiness_gates"
        }
        priorities: dict[str, float] = {}
        for doc in documents.values():
            for item in doc.get("items", []):
                priority = str(item.get("priority", "متوسط"))
                priorities[priority] = priorities.get(priority, 0.0) + 1.0
        gate_chart: dict[str, float] = {}
        for gate in gates:
            status = str(gate.get("current_status", "missing"))
            gate_chart[status] = gate_chart.get(status, 0.0) + 1.0
        audit_chart = {
            str(item.get("title", index + 1)): 1.0
            for index, item in enumerate(documents["audit_controls"].get("items", []))
        }
        workflow_chart = {
            str(item.get("title", index + 1)): 1.0
            for index, item in enumerate(documents["approval_workflows"].get("items", []))
        }
        policy_chart = {
            str(item.get("title", index + 1)): 1.0
            for index, item in enumerate(documents["policy_registry"].get("items", []))
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {item: 1.0 for item in recommendations}
        return {
            "summary": summary,
            "documents": documents,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "governance_domains": bar_chart(
                "توزيع مجالات الحوكمة",
                *self._dict_chart_values(domain_distribution),
                label="مجالات الحوكمة",
                color="blue",
            ).to_dict(),
            "readiness_gates": bar_chart(
                "حالة بوابات الجاهزية",
                *self._dict_chart_values(gate_chart),
                label="البوابات",
                color="warning",
            ).to_dict(),
            "priorities": bar_chart(
                "مستويات الأولوية",
                *self._dict_chart_values(priorities),
                label="الأولوية",
                color="green",
            ).to_dict(),
            "audit_controls": bar_chart(
                "ضوابط التدقيق",
                *self._dict_chart_values(audit_chart),
                label="التدقيق",
                color="accent",
            ).to_dict(),
            "approval_workflows": bar_chart(
                "مسارات الموافقة",
                *self._dict_chart_values(workflow_chart),
                label="الموافقات",
                color="blue",
            ).to_dict(),
            "policies": bar_chart(
                "السياسات",
                *self._dict_chart_values(policy_chart),
                label="السياسات",
                color="green",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def governance_traceability_analytics(self) -> dict[str, Any]:
        """Return latest governance traceability analytics."""
        summary_payload = self._latest_json_dict(
            "governance_traceability",
            "governance_traceability_summary",
        )
        coverage = self._latest_json_dict(
            "governance_traceability",
            "coverage_summary_report",
        )
        documents = {
            "control_mappings": self._latest_json_dict(
                "governance_traceability",
                "control_mappings_report",
            ),
            "control_matrix": self._latest_json_dict(
                "governance_traceability",
                "control_matrix_report",
            ),
            "evidence_matrix": self._latest_json_dict(
                "governance_traceability",
                "evidence_matrix_report",
            ),
            "readiness_mapping": self._latest_json_dict(
                "governance_traceability",
                "readiness_mapping_report",
            ),
            "policy_mapping": self._latest_json_dict(
                "governance_traceability",
                "policy_mapping_report",
            ),
        }
        diagnostics = self._latest_json_list(
            "governance_traceability",
            "diagnostics_report",
        )
        reports = self.loader.list_reports()
        recommendations_report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            "governance_traceability",
            "recommendations_report",
        )
        recommendations_content = (
            self.loader.get_report(recommendations_report.report_id)
            if recommendations_report
            else None
        )
        recommendation_payload = (
            recommendations_content.json_data if recommendations_content else []
        )
        recommendations = (
            [str(item) for item in recommendation_payload]
            if isinstance(recommendation_payload, list)
            else []
        )
        summary = {
            "traceability_status": summary_payload.get(
                "traceability_status",
                "Traceability Incomplete",
            ),
            "overall_traceability_score": self._float(
                summary_payload.get(
                    "overall_traceability_score",
                    coverage.get("overall_traceability_score", 0),
                )
            ),
            "control_coverage_score": self._float(
                summary_payload.get(
                    "control_coverage_score",
                    coverage.get("control_coverage_score", 0),
                )
            ),
            "evidence_coverage_score": self._float(
                summary_payload.get(
                    "evidence_coverage_score",
                    coverage.get("evidence_coverage_score", 0),
                )
            ),
            "readiness_traceability_score": self._float(
                summary_payload.get(
                    "readiness_traceability_score",
                    coverage.get("readiness_traceability_score", 0),
                )
            ),
            "policy_coverage_score": self._float(
                summary_payload.get(
                    "policy_coverage_score",
                    coverage.get("policy_coverage_score", 0),
                )
            ),
            "mapping_count": self._float(
                summary_payload.get(
                    "mapping_count",
                    len(documents["control_mappings"].get("items", [])),
                )
            ),
            "strong_mapping_count": self._float(
                summary_payload.get(
                    "strong_mapping_count",
                    coverage.get("strong_mappings", 0),
                )
            ),
            "weak_mapping_count": self._float(
                summary_payload.get("weak_mapping_count", coverage.get("weak_mappings", 0))
            ),
            "missing_mapping_count": self._float(
                summary_payload.get(
                    "missing_mapping_count",
                    coverage.get("unmapped_design_areas", 0),
                )
            ),
            "uncovered_control_count": self._float(
                summary_payload.get(
                    "uncovered_control_count",
                    coverage.get("missing_controls", 0),
                )
            ),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "traceability_only": True,
            "governance_only": True,
            "design_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        mapping_distribution: dict[str, float] = {}
        strength_distribution: dict[str, float] = {}
        for item in documents["control_mappings"].get("items", []):
            mapping_type = str(item.get("mapping_type", "control"))
            strength = str(item.get("strength", "متوسط"))
            mapping_distribution[mapping_type] = mapping_distribution.get(mapping_type, 0.0) + 1.0
            strength_distribution[strength] = strength_distribution.get(strength, 0.0) + 1.0
        score_chart = {
            "control": summary["control_coverage_score"],
            "evidence": summary["evidence_coverage_score"],
            "readiness": summary["readiness_traceability_score"],
            "policy": summary["policy_coverage_score"],
        }
        policy_chart = {
            str(item.get("source_area", index + 1)): 1.0
            for index, item in enumerate(documents["policy_mapping"].get("items", []))
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {item: 1.0 for item in recommendations}
        return {
            "summary": summary,
            "coverage": coverage,
            "documents": documents,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "mapping_distribution": bar_chart(
                "توزيع الخرائط",
                *self._dict_chart_values(mapping_distribution),
                label="الخرائط",
                color="blue",
            ).to_dict(),
            "mapping_strength": bar_chart(
                "قوة الخرائط",
                *self._dict_chart_values(strength_distribution),
                label="القوة",
                color="green",
            ).to_dict(),
            "coverage_scores": bar_chart(
                "تغطية الضوابط والأدلة",
                *self._dict_chart_values(score_chart),
                label="التغطية",
                color="accent",
            ).to_dict(),
            "readiness_traceability": bar_chart(
                "تتبع الجاهزية",
                ["traceability"],
                [summary["readiness_traceability_score"]],
                label="الجاهزية",
                color="warning",
            ).to_dict(),
            "policies": bar_chart(
                "السياسات",
                *self._dict_chart_values(policy_chart),
                label="السياسات",
                color="blue",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def control_assurance_analytics(self) -> dict[str, Any]:
        """Return latest control assurance analytics."""
        summary_payload = self._latest_json_dict(
            "control_assurance",
            "control_assurance_summary",
        )
        scorecard = self._latest_json_dict("control_assurance", "scorecard_report")
        documents = {
            "control_quality": self._latest_json_dict(
                "control_assurance",
                "control_quality_report",
            ),
            "evidence_sufficiency": self._latest_json_dict(
                "control_assurance",
                "evidence_sufficiency_report",
            ),
            "owner_clarity": self._latest_json_dict(
                "control_assurance",
                "owner_clarity_report",
            ),
            "policy_completeness": self._latest_json_dict(
                "control_assurance",
                "policy_completeness_report",
            ),
            "gate_maturity": self._latest_json_dict(
                "control_assurance",
                "gate_maturity_report",
            ),
            "weakness_assessment": self._latest_json_dict(
                "control_assurance",
                "weakness_assessment_report",
            ),
        }
        diagnostics = self._latest_json_list("control_assurance", "diagnostics_report")
        reports = self.loader.list_reports()
        recommendations_report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            "control_assurance",
            "recommendations_report",
        )
        recommendations_content = (
            self.loader.get_report(recommendations_report.report_id)
            if recommendations_report
            else None
        )
        recommendation_payload = (
            recommendations_content.json_data if recommendations_content else []
        )
        recommendations = (
            [str(item) for item in recommendation_payload]
            if isinstance(recommendation_payload, list)
            else []
        )
        summary = {
            "assurance_status": summary_payload.get(
                "assurance_status",
                scorecard.get("score_status", "غير جاهز"),
            ),
            "review_readiness_state": summary_payload.get(
                "review_readiness_state",
                "Review Blocked",
            ),
            "overall_assurance_score": self._float(
                summary_payload.get(
                    "overall_assurance_score",
                    scorecard.get("overall_assurance_score", 0),
                )
            ),
            "control_quality_score": self._float(
                summary_payload.get(
                    "control_quality_score",
                    scorecard.get("control_quality_score", 0),
                )
            ),
            "evidence_sufficiency_score": self._float(
                summary_payload.get(
                    "evidence_sufficiency_score",
                    scorecard.get("evidence_sufficiency_score", 0),
                )
            ),
            "owner_clarity_score": self._float(
                summary_payload.get(
                    "owner_clarity_score",
                    scorecard.get("owner_clarity_score", 0),
                )
            ),
            "policy_completeness_score": self._float(
                summary_payload.get(
                    "policy_completeness_score",
                    scorecard.get("policy_completeness_score", 0),
                )
            ),
            "gate_maturity_score": self._float(
                summary_payload.get("gate_maturity_score", scorecard.get("gate_maturity_score", 0))
            ),
            "audit_readiness_score": self._float(
                summary_payload.get(
                    "audit_readiness_score",
                    scorecard.get("audit_readiness_score", 0),
                )
            ),
            "governance_review_readiness_score": self._float(
                summary_payload.get(
                    "governance_review_readiness_score",
                    scorecard.get("governance_review_readiness_score", 0),
                )
            ),
            "weakness_count": self._float(
                summary_payload.get(
                    "weakness_count",
                    len(documents["weakness_assessment"].get("items", [])),
                )
            ),
            "blocker_count": self._float(summary_payload.get("blocker_count", 0)),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "assurance_only": True,
            "review_readiness_only": True,
            "governance_only": True,
            "design_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        score_chart = {
            "control": summary["control_quality_score"],
            "evidence": summary["evidence_sufficiency_score"],
            "owner": summary["owner_clarity_score"],
            "policy": summary["policy_completeness_score"],
            "gate": summary["gate_maturity_score"],
            "audit": summary["audit_readiness_score"],
            "review": summary["governance_review_readiness_score"],
        }
        status_counts: dict[str, float] = {}
        for key in (
            "control_quality",
            "evidence_sufficiency",
            "owner_clarity",
            "policy_completeness",
            "gate_maturity",
        ):
            for item in documents[key].get("items", []):
                status = str(item.get("status", "مقبول"))
                status_counts[status] = status_counts.get(status, 0.0) + 1.0
        weakness_chart = {
            str(item.get("source_area", index + 1)): 1.0
            for index, item in enumerate(documents["weakness_assessment"].get("items", []))
        }
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {item: 1.0 for item in recommendations}
        return {
            "summary": summary,
            "scorecard": scorecard,
            "documents": documents,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "assurance_scores": bar_chart(
                "درجات التأكيد",
                *self._dict_chart_values(score_chart),
                label="الدرجات",
                color="blue",
            ).to_dict(),
            "assessment_status": bar_chart(
                "جودة الضوابط",
                *self._dict_chart_values(status_counts),
                label="الحالة",
                color="green",
            ).to_dict(),
            "weaknesses": bar_chart(
                "نقاط الضعف",
                *self._dict_chart_values(weakness_chart),
                label="نقاط الضعف",
                color="warning",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
        }

    def review_board_simulation_analytics(self) -> dict[str, Any]:
        """Return latest review board simulation analytics."""
        summary_payload = self._latest_json_dict(
            "review_board_simulation",
            "review_board_simulation_summary",
        )
        scores = self._latest_json_dict("review_board_simulation", "decision_scores_report")
        board_results = self._latest_json_dict(
            "review_board_simulation",
            "board_simulation_report",
        )
        gate_results = self._latest_json_dict(
            "review_board_simulation",
            "gate_dry_run_report",
        )
        evidence = self._latest_json_dict(
            "review_board_simulation",
            "evidence_review_report",
        )
        blocker_analysis = self._latest_json_dict(
            "review_board_simulation",
            "blocker_analysis_report",
        )
        diagnostics = self._latest_json_list(
            "review_board_simulation",
            "diagnostics_report",
        )
        reports = self.loader.list_reports()
        recommendations_report = self.loader.latest(
            [item for item in reports if item.report_type == "json"],
            "review_board_simulation",
            "recommendations_report",
        )
        recommendations_content = (
            self.loader.get_report(recommendations_report.report_id)
            if recommendations_report
            else None
        )
        recommendation_payload = (
            recommendations_content.json_data if recommendations_content else []
        )
        recommendations = (
            [str(item) for item in recommendation_payload]
            if isinstance(recommendation_payload, list)
            else []
        )
        board_scores = {
            str(item.get("board_name", index + 1)): self._float(item.get("score"))
            for index, item in enumerate(scores.get("board_scores", []))
        }
        gate_scores = {
            str(item.get("gate_name", index + 1)): self._float(item.get("score"))
            for index, item in enumerate(scores.get("gate_scores", []))
        }
        evidence_scores = {
            str(item.get("source_group", index + 1)): self._float(item.get("linkage_score"))
            for index, item in enumerate(evidence.get("items", []))
        }
        blockers = {
            str(item.get("scope", index + 1)): 1.0
            for index, item in enumerate(blocker_analysis.get("items", []))
        }
        condition_counts: dict[str, float] = {}
        human_review_counts: dict[str, float] = {}
        state_counts: dict[str, float] = {}
        for item in gate_results.get("items", []):
            gate = str(item.get("gate_name", "gate"))
            condition_counts[gate] = self._float(len(item.get("conditions", [])))
            human_review_counts[gate] = 1.0 if item.get("required_human_review") else 0.0
            state = str(item.get("simulated_state", "Requires Human Review"))
            state_counts[state] = state_counts.get(state, 0.0) + 1.0
        for board in board_results.get("items", []):
            for decision in board.get("simulated_decisions", []):
                state = str(decision.get("simulated_state", "Requires Human Review"))
                state_counts[state] = state_counts.get(state, 0.0) + 1.0
        diagnostic_chart = {
            str(item.get("code", index + 1)): 1.0 for index, item in enumerate(diagnostics)
        }
        recommendation_chart = {item: 1.0 for item in recommendations}
        summary = {
            "simulation_status": summary_payload.get(
                "simulation_status",
                scores.get("score_status", "Requires Human Review"),
            ),
            "overall_review_readiness_score": self._float(
                summary_payload.get(
                    "overall_review_readiness_score",
                    scores.get("overall_review_readiness_score", 0),
                )
            ),
            "board_readiness_score": self._float(summary_payload.get("board_readiness_score", 0)),
            "evidence_readiness_score": self._float(
                summary_payload.get(
                    "evidence_readiness_score",
                    scores.get("evidence_readiness_score", 0),
                )
            ),
            "gate_readiness_score": self._float(
                summary_payload.get(
                    "gate_readiness_score",
                    scores.get("gate_readiness_score", 0),
                )
            ),
            "simulated_decision_count": self._float(
                summary_payload.get("simulated_decision_count", 0)
            ),
            "blocker_count": self._float(summary_payload.get("blocker_count", 0)),
            "condition_count": self._float(summary_payload.get("condition_count", 0)),
            "required_human_review_count": self._float(
                summary_payload.get("required_human_review_count", 0)
            ),
            "diagnostic_count": self._float(
                summary_payload.get("diagnostic_count", len(diagnostics))
            ),
            "recommendation_count": self._float(
                summary_payload.get("recommendation_count", len(recommendations))
            ),
            "simulation_only": True,
            "review_only": True,
            "dry_run_only": True,
            "governance_only": True,
            "design_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }
        return {
            "summary": summary,
            "scores": scores,
            "board_results": board_results,
            "gate_results_payload": gate_results,
            "evidence_payload": evidence,
            "blocker_analysis": blocker_analysis,
            "diagnostics_items": diagnostics,
            "recommendations_items": recommendations,
            "board_scores": bar_chart(
                "درجات مجالس المراجعة",
                *self._dict_chart_values(board_scores),
                label="الدرجات",
                color="blue",
            ).to_dict(),
            "gate_results": bar_chart(
                "نتائج البوابات",
                *self._dict_chart_values(gate_scores),
                label="البوابات",
                color="green",
            ).to_dict(),
            "evidence": bar_chart(
                "جاهزية الأدلة",
                *self._dict_chart_values(evidence_scores),
                label="الأدلة",
                color="accent",
            ).to_dict(),
            "blockers": bar_chart(
                "العوائق",
                *self._dict_chart_values(blockers),
                label="العوائق",
                color="warning",
            ).to_dict(),
            "conditions": bar_chart(
                "الشروط",
                *self._dict_chart_values(condition_counts),
                label="الشروط",
                color="blue",
            ).to_dict(),
            "human_reviews": bar_chart(
                "المراجعات البشرية المطلوبة",
                *self._dict_chart_values(human_review_counts),
                label="المراجعة",
                color="warning",
            ).to_dict(),
            "diagnostics": bar_chart(
                "التحذيرات",
                *self._dict_chart_values(diagnostic_chart),
                label="التحذيرات",
                color="warning",
            ).to_dict(),
            "recommendations": bar_chart(
                "التوصيات",
                *self._dict_chart_values(recommendation_chart),
                label="التوصيات",
                color="green",
            ).to_dict(),
            "decision_states": bar_chart(
                "حالات القرارات المحاكاة",
                *self._dict_chart_values(state_counts),
                label="الحالات",
                color="accent",
            ).to_dict(),
        }

    def research_operations_analytics(self) -> dict[str, Any]:
        """Return latest research operations analytics."""
        summary_payload = self._latest_json_dict("research_ops", "operations")
        summary = summary_payload.get("summary", {}) if summary_payload else {}
        latest = summary_payload.get("latest", {}) if summary_payload else {}
        health = summary_payload.get("health_trends", {}) if summary_payload else {}
        readiness = summary_payload.get("readiness_trends", {}) if summary_payload else {}
        confluence = summary_payload.get("confluence_trends", {}) if summary_payload else {}
        performance = summary_payload.get("performance_trends", {}) if summary_payload else {}
        opportunity = (
            summary_payload.get("opportunity_quality_trends", {}) if summary_payload else {}
        )
        quality = summary_payload.get("quality_trends", {}) if summary_payload else {}
        stability = summary_payload.get("stability_trends", {}) if summary_payload else {}
        alerts = self._latest_json_dict("research_ops", "alerts")
        recommendations = self._latest_json_dict("research_ops", "recommendations")
        risks = self._latest_json_dict("research_ops", "risk")
        if not summary:
            summary = {
                "health_score": 0.0,
                "readiness_score": 0.0,
                "opportunity_count": 0,
                "alert_count": 0,
                "risk_count": 0,
                "recommendation_count": 0,
                "best_opportunity": "غير متاح",
                "last_update": "غير متاح",
            }
        return {
            "summary": summary,
            "latest": latest,
            "health": line_chart(
                "صحة الأبحاث بمرور الوقت",
                *self._dict_chart_values(health),
                label="الصحة",
                color="green",
            ).to_dict(),
            "readiness": line_chart(
                "تطور الجاهزية",
                *self._dict_chart_values(readiness),
                label="الجاهزية",
                color="blue",
            ).to_dict(),
            "confluence": line_chart(
                "تطور التوافق",
                *self._dict_chart_values(confluence),
                label="التوافق",
                color="accent",
            ).to_dict(),
            "performance": line_chart(
                "تطور الأداء",
                *self._dict_chart_values(performance),
                label="الأداء",
                color="warning",
            ).to_dict(),
            "opportunity": line_chart(
                "تطور جودة الفرص",
                *self._dict_chart_values(opportunity),
                label="الفرص",
                color="green",
            ).to_dict(),
            "risks": bar_chart(
                "توزيع المخاطر",
                *self._dict_chart_values(risks),
                label="المخاطر",
                color="warning",
            ).to_dict(),
            "alerts": bar_chart(
                "توزيع التنبيهات",
                *self._dict_chart_values(alerts),
                label="التنبيهات",
                color="blue",
            ).to_dict(),
            "recommendations": bar_chart(
                "توزيع التوصيات",
                *self._dict_chart_values(recommendations),
                label="التوصيات",
                color="accent",
            ).to_dict(),
            "quality": line_chart(
                "اتجاهات الجودة",
                *self._dict_chart_values(quality),
                label="الجودة",
                color="green",
            ).to_dict(),
            "stability": line_chart(
                "اتجاهات الاستقرار",
                *self._dict_chart_values(stability),
                label="الاستقرار",
                color="blue",
            ).to_dict(),
        }

    def _best_confirmation(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {}
        return max(rows, key=lambda row: self._float(row.get("confirmation_score")))

    def _state_map(self, row: dict[str, Any]) -> dict[str, str]:
        states = {"M1": "غير متاح", "M5": "غير متاح", "M15": "غير متاح", "H1": "غير متاح"}
        for item in row.get("timeframe_states", []) if isinstance(row, dict) else []:
            if isinstance(item, dict):
                states[str(item.get("timeframe"))] = str(item.get("state"))
        return states

    def _timeline_from_confirmations(self, rows: list[dict[str, Any]]) -> dict[str, float]:
        values: dict[str, list[float]] = {}
        for row in rows:
            label = self._short_time(row.get("timestamp"))
            values.setdefault(label, []).append(self._float(row.get("confirmation_score")))
        return {key: round(sum(items) / len(items), 2) for key, items in values.items() if items}

    def _fvg_from_opportunities(self, rows: list[dict[str, Any]]) -> dict[str, float]:
        values: dict[str, list[float]] = {}
        for row in rows:
            factors = row.get("supporting_factors", [])
            label = "لا يوجد"
            if isinstance(factors, list):
                label = next((str(item) for item in factors if "FVG" in str(item)), label)
            values.setdefault(label, []).append(self._float(row.get("fvg_score")))
        return {key: round(sum(items) / len(items), 2) for key, items in values.items() if items}

    def _timeline_from_opportunities(self, rows: list[dict[str, Any]]) -> dict[str, float]:
        values: dict[str, list[float]] = {}
        for row in rows:
            label = self._short_time(row.get("timestamp"))
            values.setdefault(label, []).append(self._float(row.get("qualification_score")))
        return {key: round(sum(items) / len(items), 2) for key, items in values.items() if items}
