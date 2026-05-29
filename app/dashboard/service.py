"""Service layer that normalizes dashboard data for routes and templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.dashboard.actions import DashboardActionRunner
from app.dashboard.models import (
    DashboardConfig,
    DashboardOverview,
    DatasetSummary,
    StrategySummary,
    ValidationSummary,
)
from app.dashboard.report_loader import DashboardReportLoader
from app.strategies.registry import default_strategy_registry


class DashboardService:
    """Read-heavy facade for local dashboard data."""

    def __init__(
        self,
        project_root: Path | str = ".",
        config: DashboardConfig | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.config = config or load_dashboard_config(self.project_root)
        self.report_loader = DashboardReportLoader(self.project_root, self.config.reports_dir)
        self.actions = DashboardActionRunner(self.project_root)

    def overview(self) -> DashboardOverview:
        """Return aggregate dashboard home data."""
        reports = self.report_loader.list_reports()
        validations = self.validation_summaries()
        datasets = self.dataset_summaries()
        latest_validation = self.report_loader.latest(reports, "validation", "report")
        latest_dataset = self.report_loader.latest(reports, "datasets")
        latest_backtest = self.report_loader.latest(reports, "sample_eurusd_m1_report")
        return DashboardOverview(
            strategies=self.strategy_summaries(),
            datasets=datasets,
            validations=validations,
            reports=reports[:8],
            latest_validation_report=latest_validation,
            latest_dataset_report=latest_dataset,
            latest_backtest_report=latest_backtest,
            latest_robustness_score=validations[0].robustness_score if validations else None,
            latest_dataset_quality_score=datasets[0].quality_score if datasets else None,
            warning_counts=self.warning_counts(validations, datasets),
        )

    def strategy_summaries(self) -> list[StrategySummary]:
        """Return registered strategy summaries plus report-derived signal metrics."""
        registry = default_strategy_registry()
        reports = self.report_loader.list_reports()
        signal_summary = self.report_loader.latest_json(
            reports,
            "strategy_research",
            "summary",
        )
        config_by_name = self._strategy_configs()
        summaries: list[StrategySummary] = []
        for strategy_id in registry.names():
            strategy = registry.create(strategy_id)
            metadata = strategy.metadata
            config = config_by_name.get(strategy_id, {})
            summaries.append(
                StrategySummary(
                    strategy_id=strategy_id,
                    name=metadata.name,
                    description=metadata.description,
                    version=metadata.version,
                    metadata={
                        "required_indicators": list(metadata.required_indicators),
                        "supports_multi_timeframe": metadata.supports_multi_timeframe,
                    },
                    parameters=dict(strategy.parameters.values),
                    default_configuration=config,
                    latest_signal_summary=self._matching_signal_summary(
                        signal_summary,
                        strategy_id,
                    ),
                    latest_report=self.report_loader.latest(reports, "strategy_research"),
                )
            )
        return summaries

    def dataset_summaries(self) -> list[DatasetSummary]:
        """Return dataset summaries from dataset reports and configuration."""
        reports = self.report_loader.list_reports()
        dataset_reports = [
            item
            for item in reports
            if item.report_type == "json" and "/datasets/" in item.relative_path
        ]
        summaries = [self._dataset_from_report(report) for report in dataset_reports]
        summaries = [item for item in summaries if item is not None]
        if summaries:
            return summaries
        config = self._load_yaml("configs/datasets/research_datasets.yaml")
        return [
            DatasetSummary(
                dataset_id=str(config.get("dataset_name", "configured_dataset")),
                name=str(config.get("dataset_name", "Configured dataset")),
                symbol=str(config.get("symbol", "")),
                timeframe=str(config.get("timeframe", "")),
                version=str(config.get("version", "")),
                row_count=0,
                start_time=None,
                end_time=None,
                checksum=None,
                fingerprint=None,
                quality_score=None,
                gap_count=0,
                duplicate_count=0,
                integrity_status="not inspected",
            )
        ]

    def validation_summaries(self) -> list[ValidationSummary]:
        """Return validation summaries from validation JSON reports."""
        reports = self.report_loader.list_reports()
        validation_reports = [
            item
            for item in reports
            if item.report_type == "json" and "/validation/" in item.relative_path
        ]
        summaries = [self._validation_from_report(report) for report in validation_reports]
        return [item for item in summaries if item is not None]

    def warning_counts(
        self,
        validations: list[ValidationSummary],
        datasets: list[DatasetSummary],
    ) -> dict[str, int]:
        """Return warning counts by coarse severity."""
        counts = {"high": 0, "medium": 0, "low": 0, "dataset": 0}
        for validation in validations:
            for warning in validation.overfitting_warnings:
                severity = str(warning.get("severity", "low")).lower()
                if severity in counts:
                    counts[severity] += 1
        counts["dataset"] = sum(1 for item in datasets if item.integrity_status != "passed")
        return counts

    def _dataset_from_report(self, report: Any) -> DatasetSummary | None:
        content = self.report_loader.get_report(report.report_id)
        if not content or not isinstance(content.json_data, dict):
            return None
        payload = content.json_data
        metadata = payload.get("metadata", {})
        quality = payload.get("quality", {})
        integrity = payload.get("integrity", {})
        stats = payload.get("statistics", {})
        if not isinstance(metadata, dict):
            return None
        return DatasetSummary(
            dataset_id=str(metadata.get("dataset_id", report.report_id)),
            name=str(metadata.get("dataset_name", report.name)),
            symbol=str(metadata.get("symbol", "")),
            timeframe=str(metadata.get("timeframe", "")),
            version=str(metadata.get("version", "")),
            row_count=int(metadata.get("row_count") or stats.get("row_count") or 0),
            start_time=metadata.get("start_time") or stats.get("start_time"),
            end_time=metadata.get("end_time") or stats.get("end_time"),
            checksum=metadata.get("checksum") or integrity.get("checksum"),
            fingerprint=integrity.get("fingerprint"),
            quality_score=self._optional_float(
                quality.get("quality_score") or stats.get("quality_score")
            ),
            gap_count=int(len(quality.get("gaps", [])) or stats.get("gap_count") or 0),
            duplicate_count=int(stats.get("duplicate_count") or 0),
            integrity_status="passed" if integrity.get("passed") else "needs review",
            latest_report=report,
        )

    def _validation_from_report(self, report: Any) -> ValidationSummary | None:
        content = self.report_loader.get_report(report.report_id)
        if not content or not isinstance(content.json_data, dict):
            return None
        payload = content.json_data
        dataset = payload.get("dataset", {})
        robustness = payload.get("robustness", {})
        results = payload.get("validation_results", {})
        if not isinstance(results, dict):
            results = {}
        warnings = payload.get("overfitting_warnings", [])
        return ValidationSummary(
            report_id=str(payload.get("report_id", report.report_id)),
            strategy_name=str(payload.get("strategy_name", "unknown")),
            dataset_name=(
                str(dataset.get("name", "unknown"))
                if isinstance(dataset, dict)
                else "unknown"
            ),
            robustness_score=self._optional_float(robustness.get("score")),
            robustness_category=str(robustness.get("category", "unknown")),
            out_of_sample_summary=self._compact(results.get("out_of_sample")),
            walk_forward_summary=self._compact(results.get("walk_forward")),
            parameter_sweep_summary=self._compact(results.get("parameter_sweep")),
            overfitting_warnings=warnings if isinstance(warnings, list) else [],
            latest_report=report,
        )

    def _strategy_configs(self) -> dict[str, dict[str, Any]]:
        configs: dict[str, dict[str, Any]] = {}
        for path in (self.project_root / "configs" / "strategies").glob("*.yaml"):
            raw = self._load_yaml(path)
            name = raw.get("name")
            if name:
                configs[str(name)] = raw
        return configs

    def _matching_signal_summary(
        self,
        signal_summary: dict[str, Any],
        strategy_id: str,
    ) -> dict[str, Any] | None:
        if signal_summary.get("strategy_name") == strategy_id:
            return signal_summary
        return None

    def _load_yaml(self, relative_path: Path | str) -> dict[str, Any]:
        path = Path(relative_path)
        if not path.is_absolute():
            path = self.project_root / path
        if not path.exists():
            return {}
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return raw if isinstance(raw, dict) else {}

    def _optional_float(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _compact(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        compact: dict[str, Any] = {}
        for key in (
            "strategy_name",
            "mode",
            "aggregate_metrics",
            "stability_metrics",
            "degradation_metrics",
            "stability_score",
            "best_parameter_sets",
            "stable_parameter_regions",
        ):
            if key in value:
                compact[key] = value[key]
        if "windows" in value and isinstance(value["windows"], list):
            compact["windows"] = len(value["windows"])
        if "results" in value and isinstance(value["results"], list):
            compact["results"] = len(value["results"])
        return compact


def load_dashboard_config(project_root: Path | str = ".") -> DashboardConfig:
    """Load dashboard config with safe defaults."""
    config_path = Path(project_root) / "configs" / "dashboard.yaml"
    if not config_path.exists():
        return DashboardConfig()
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dashboard = raw.get("dashboard", raw)
    if not isinstance(dashboard, dict):
        return DashboardConfig()
    return DashboardConfig(
        enabled=bool(dashboard.get("enabled", True)),
        host=str(dashboard.get("host", "127.0.0.1")),
        port=int(dashboard.get("port", 8000)),
        reports_dir=str(dashboard.get("reports_dir", "reports")),
        allow_actions=bool(dashboard.get("allow_actions", True)),
    )
