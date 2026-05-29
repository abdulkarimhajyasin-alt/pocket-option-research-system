"""Research validation report generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from uuid import uuid4

from loguru import logger

from app.validation.models import (
    DatasetDescriptor,
    OutOfSampleResult,
    OverfittingWarning,
    ParameterSweepSummary,
    ResearchValidationReport,
    RobustnessScore,
    WalkForwardResult,
)


class ResearchReportBuilder:
    """Builds structured, reproducible validation reports."""

    def build(
        self,
        strategy_name: str,
        dataset: DatasetDescriptor,
        parameters: dict[str, object],
        robustness: RobustnessScore,
        overfitting_warnings: list[OverfittingWarning],
        walk_forward: WalkForwardResult | None = None,
        out_of_sample: OutOfSampleResult | None = None,
        sweep: ParameterSweepSummary | None = None,
    ) -> ResearchValidationReport:
        """Build a complete report object."""
        validation_results = {}
        if walk_forward is not None:
            validation_results["walk_forward"] = walk_forward.to_dict()
        if out_of_sample is not None:
            validation_results["out_of_sample"] = out_of_sample.to_dict()
        if sweep is not None:
            validation_results["parameter_sweep"] = sweep.to_dict()
        conclusions = self._conclusions(robustness, overfitting_warnings)
        return ResearchValidationReport(
            report_id=str(uuid4()),
            strategy_name=strategy_name,
            dataset=dataset,
            parameters=parameters,
            validation_results=validation_results,
            robustness=robustness,
            overfitting_warnings=overfitting_warnings,
            conclusions=conclusions,
        )

    def _conclusions(
        self,
        robustness: RobustnessScore,
        warnings: list[OverfittingWarning],
    ) -> list[str]:
        conclusions = [
            f"Robustness category: {robustness.category.value}",
            "Evaluation is research-only and does not authorize execution.",
        ]
        if warnings:
            conclusions.append(
                f"{len(warnings)} overfitting warning(s) require review before expansion."
            )
        else:
            conclusions.append("No configured overfitting warning thresholds were triggered.")
        return conclusions


class ResearchReportExporter:
    """Exports validation reports as JSON, CSV, and human-readable text."""

    def __init__(self, export_dir: Path | str = "reports/validation") -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(self, report: ResearchValidationReport, run_name: str) -> dict[str, Path]:
        """Export a research report in supported formats."""
        json_path = self.export_dir / f"{run_name}_report.json"
        csv_path = self.export_dir / f"{run_name}_metrics.csv"
        text_path = self.export_dir / f"{run_name}_report.txt"
        json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        self._write_csv(csv_path, report)
        text_path.write_text(self._text_report(report), encoding="utf-8")
        logger.bind(component="strategy_validation").info(
            "Research validation report exported to {}",
            self.export_dir,
        )
        return {"json": json_path, "csv": csv_path, "text": text_path}

    def _write_csv(self, path: Path, report: ResearchValidationReport) -> None:
        rows = [
            {"metric": name, "value": value} for name, value in report.robustness.components.items()
        ]
        rows.append({"metric": "robustness_score", "value": report.robustness.score})
        rows.append({"metric": "warning_count", "value": len(report.overfitting_warnings)})
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["metric", "value"])
            writer.writeheader()
            writer.writerows(rows)

    def _text_report(self, report: ResearchValidationReport) -> str:
        warning_lines = [
            f"- {warning.severity.value}: {warning.code} - {warning.message}"
            for warning in report.overfitting_warnings
        ] or ["- none"]
        conclusion_lines = [f"- {item}" for item in report.conclusions]
        return "\n".join(
            [
                f"Strategy Validation Report: {report.strategy_name}",
                f"Dataset: {report.dataset.name} ({report.dataset.sample_count} samples)",
                f"Robustness: {report.robustness.score:.2f} "
                f"({report.robustness.category.value})",
                "Overfitting Warnings:",
                *warning_lines,
                "Conclusions:",
                *conclusion_lines,
                "",
            ]
        )
