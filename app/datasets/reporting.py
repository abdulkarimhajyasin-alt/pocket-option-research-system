"""Dataset report generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app.datasets.models import (
    DatasetComparisonReport,
    DatasetMetadata,
    DatasetStatistics,
    DatasetVersion,
    IntegrityReport,
    QualityReport,
)


class DatasetReportExporter:
    """Export reproducible dataset reports."""

    def __init__(self, output_dir: Path | str = "reports/datasets") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_dataset_report(
        self,
        metadata: DatasetMetadata,
        version: DatasetVersion,
        quality: QualityReport,
        integrity: IntegrityReport,
        statistics: DatasetStatistics,
    ) -> dict[str, Path]:
        """Export JSON, CSV, and text report files."""
        base = self.output_dir / f"{metadata.dataset_name}_{metadata.version}"
        payload = {
            "metadata": metadata.to_dict(),
            "version": version.to_dict(),
            "quality": quality.to_dict(),
            "integrity": integrity.to_dict(),
            "statistics": statistics.to_dict(),
        }
        json_path = base.with_suffix(".json")
        csv_path = base.with_suffix(".csv")
        text_path = base.with_suffix(".txt")
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._write_csv(csv_path, payload)
        text_path.write_text(self._text_report(payload), encoding="utf-8")
        return {"json": json_path, "csv": csv_path, "text": text_path}

    def export_comparison(self, report: DatasetComparisonReport) -> dict[str, Path]:
        """Export dataset comparison report."""
        base = self.output_dir / "dataset_comparison"
        json_path = base.with_suffix(".json")
        csv_path = base.with_suffix(".csv")
        text_path = base.with_suffix(".txt")
        payload = report.to_dict()
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "dataset_id",
                    "dataset_name",
                    "row_count",
                    "quality_score",
                    "volatility",
                    "gap_count",
                    "duplicate_count",
                ],
            )
            writer.writeheader()
            writer.writerows(report.rankings)
        lines = ["Dataset Comparison", f"Report: {report.report_id}", "Rankings:"]
        lines.extend(
            f"- {row['dataset_name']}: quality={row['quality_score']} rows={row['row_count']}"
            for row in report.rankings
        )
        text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"json": json_path, "csv": csv_path, "text": text_path}

    def _write_csv(self, path: Path, payload: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["section", "key", "value"])
            writer.writeheader()
            for section, values in payload.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        writer.writerow({"section": section, "key": key, "value": value})

    def _text_report(self, payload: dict[str, Any]) -> str:
        metadata = payload["metadata"]
        quality = payload["quality"]
        integrity = payload["integrity"]
        statistics = payload["statistics"]
        return (
            "\n".join(
                [
                    "Dataset Quality Report",
                    f"Dataset: {metadata['dataset_name']} ({metadata['dataset_id']})",
                    f"Version: {metadata['version']}",
                    f"Symbol/timeframe: {metadata['symbol']} {metadata['timeframe']}",
                    f"Rows: {metadata['row_count']}",
                    f"Quality score: {quality['quality_score']}",
                    f"Integrity passed: {integrity['passed']}",
                    f"Gaps: {statistics['gap_count']}",
                    f"Duplicates: {statistics['duplicate_count']}",
                ]
            )
            + "\n"
        )
