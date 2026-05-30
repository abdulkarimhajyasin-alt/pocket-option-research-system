"""High-level orchestration for research validation scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from app.config.strategy_config import StrategyConfigLoader
from app.data.csv_loader import CsvCandleLoader
from app.datasets.config import DatasetLayerConfig
from app.datasets.service import DatasetQualityService
from app.storage.persistence import PersistenceService
from app.validation.config import ValidationResearchConfig, config_to_dict
from app.validation.dataset import DatasetManager
from app.validation.models import ResearchValidationReport
from app.validation.out_of_sample import OutOfSampleValidator
from app.validation.overfitting import OverfittingDetector
from app.validation.parameter_sweep import ParameterSweepEngine
from app.validation.reporting import ResearchReportBuilder, ResearchReportExporter
from app.validation.robustness import RobustnessScorer
from app.validation.runner import ValidationBacktestRunner
from app.validation.walk_forward import WalkForwardValidator


class ValidationExecutionService:
    """Runs validation computations without export or persistence side effects."""

    def __init__(self, project_root: Path, config: ValidationResearchConfig) -> None:
        self.project_root = project_root
        self.config = config
        self.dataset_manager = DatasetManager()
        self.strategy_config = StrategyConfigLoader().load(
            project_root / config.strategy_config_path
        )
        self.candles = CsvCandleLoader().load(
            project_root / config.dataset_path,
            symbol=self.strategy_config.symbols[0],
            timeframe=self.strategy_config.timeframes[0],
        )
        self.dataset_quality = DatasetQualityService(
            project_root,
            DatasetLayerConfig(
                dataset_name=config.dataset_name,
                dataset_path=config.dataset_path,
                symbol=self.strategy_config.symbols[0],
                timeframe=self.strategy_config.timeframes[0],
                reports_dir="reports/datasets",
                tags=("validation", "research"),
            ),
        )
        metadata, version, quality, integrity, statistics = self.dataset_quality.inspect(
            candles=self.candles,
            dataset_name=config.dataset_name,
            source=str(project_root / config.dataset_path),
            persist=False,
        )
        if not quality.passed or not integrity.passed:
            raise ValueError(
                "Dataset failed validation quality gate: "
                f"quality_passed={quality.passed} integrity_passed={integrity.passed}"
            )
        self.runner = ValidationBacktestRunner(project_root / config.risk_profile_path)
        self.dataset = self.dataset_manager.describe(
            self.candles,
            config.dataset_name,
            project_root / config.dataset_path,
            {
                "config": config_to_dict(config),
                "dataset_metadata": metadata.to_dict(),
                "dataset_version": version.to_dict(),
                "dataset_quality": quality.to_dict(),
                "dataset_integrity": integrity.to_dict(),
                "dataset_statistics": statistics.to_dict(),
            },
        )

    def run_walk_forward(self) -> Any:
        """Run configured walk-forward validation."""
        return WalkForwardValidator(self.runner, self.dataset_manager).run(
            self.strategy_config,
            self.candles,
            self.config.dataset_name,
            str(self.project_root / self.config.dataset_path),
            self.config.walk_forward,
        )

    def run_out_of_sample(self) -> Any:
        """Run configured out-of-sample validation."""
        return OutOfSampleValidator(self.runner, self.dataset_manager).run(
            self.strategy_config,
            self.candles,
            self.config.dataset_name,
            str(self.project_root / self.config.dataset_path),
            self.config.out_of_sample,
        )

    def run_parameter_sweep(self) -> Any:
        """Run configured parameter sensitivity analysis."""
        return ParameterSweepEngine(self.runner, self.dataset_manager).run(
            self.strategy_config,
            self.candles,
            self.config.dataset_name,
            str(self.project_root / self.config.dataset_path),
            self.config.parameter_sweeps,
        )

    def run_report(self) -> ResearchValidationReport:
        """Run full validation and build a reusable report object."""
        walk_forward = self.run_walk_forward() if self.config.walk_forward.enabled else None
        out_of_sample = self.run_out_of_sample() if self.config.out_of_sample.enabled else None
        sweep = self.run_parameter_sweep() if self.config.parameter_sweeps.enabled else None
        robustness = RobustnessScorer().score(walk_forward, out_of_sample, sweep)
        warnings = OverfittingDetector().detect(walk_forward, out_of_sample, sweep)
        report = ResearchReportBuilder().build(
            self.strategy_config.name,
            self.dataset,
            self.strategy_config.parameters,
            robustness,
            warnings,
            walk_forward=walk_forward,
            out_of_sample=out_of_sample,
            sweep=sweep,
        )
        logger.bind(component="strategy_validation").info(
            "Validation report complete score={} warnings={}",
            robustness.score,
            len(warnings),
        )
        return report


class ValidationReportExporter:
    """Exports validation reports explicitly."""

    def __init__(self, project_root: Path, config: ValidationResearchConfig) -> None:
        self.project_root = project_root
        self.config = config

    def export(self, report: ResearchValidationReport) -> dict[str, Path]:
        """Export a reproducible research report."""
        return ResearchReportExporter(self.project_root / self.config.reports_dir).export(
            report,
            report.strategy_name,
        )


class ValidationPersistenceAdapter:
    """Persists validation reports explicitly."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def persist(self, report: ResearchValidationReport) -> None:
        """Persist validation output using existing append-only events."""
        persistence = PersistenceService(
            self.project_root / "storage" / "trading_system.db",
            session_id="strategy_validation",
        )
        persistence.persist_validation_run(report.strategy_name, report.to_dict())
        walk_forward = report.validation_results.get("walk_forward")
        if isinstance(walk_forward, dict):
            persistence.persist_walk_forward_result(report.strategy_name, walk_forward)
        sweep = report.validation_results.get("parameter_sweep")
        if isinstance(sweep, dict):
            persistence.persist_parameter_sweep(report.strategy_name, sweep)
        persistence.persist_robustness_score(
            report.strategy_name,
            report.robustness.to_dict(),
        )
        persistence.persist_overfitting_diagnostics(
            report.strategy_name,
            {"warnings": [warning.to_dict() for warning in report.overfitting_warnings]},
        )
        persistence.persist_dataset_metadata(report.dataset.name, report.dataset.to_dict())
        persistence.close()


class StrategyValidationService:
    """Orchestrates validation execution, export, and persistence explicitly."""

    def __init__(self, project_root: Path, config: ValidationResearchConfig) -> None:
        self.project_root = project_root
        self.config = config
        self.execution = ValidationExecutionService(project_root, config)
        self.exporter = ValidationReportExporter(project_root, config)
        self.persistence = ValidationPersistenceAdapter(project_root)
        self.strategy_config = self.execution.strategy_config
        self.candles = self.execution.candles
        self.dataset = self.execution.dataset

    def run_walk_forward(self) -> Any:
        """Run configured walk-forward validation."""
        return self.execution.run_walk_forward()

    def run_out_of_sample(self) -> Any:
        """Run configured out-of-sample validation."""
        return self.execution.run_out_of_sample()

    def run_parameter_sweep(self) -> Any:
        """Run configured parameter sensitivity analysis."""
        return self.execution.run_parameter_sweep()

    def run_report(
        self,
        export: bool = True,
        persist: bool = True,
    ) -> tuple[ResearchValidationReport, dict[str, Path]]:
        """Run validation and optionally export/persist for backward compatibility."""
        report = self.execution.run_report()
        paths = self.exporter.export(report) if export else {}
        if persist:
            self.persist(report)
        return report, paths

    def persist(self, report: ResearchValidationReport) -> None:
        """Persist validation output."""
        self.persistence.persist(report)
