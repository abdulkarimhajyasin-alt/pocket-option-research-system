"""Analytics export utilities."""

import csv
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.analytics.models import AnalyticsSnapshot, EquityCurvePoint, TradeJournalEntry


class AnalyticsExporter:
    """Exports analytics artifacts to configurable report directories."""

    def __init__(self, export_dir: Path | str = "reports/analytics") -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_snapshot(self, snapshot: AnalyticsSnapshot, name: str) -> dict[str, Path]:
        """Export analytics snapshot as JSON."""
        path = self.export_dir / f"{name}_analytics.json"
        self._write_json(path, snapshot.to_dict())
        logger.bind(component="analytics").info("Analytics snapshot exported: {}", path)
        return {"json": path}

    def export_journal(self, entries: list[TradeJournalEntry], name: str) -> dict[str, Path]:
        """Export journal entries as JSON and CSV."""
        json_path = self.export_dir / f"{name}_journal.json"
        csv_path = self.export_dir / f"{name}_journal.csv"
        self._write_json(json_path, [entry.to_dict() for entry in entries])
        self._write_csv(csv_path, [entry.to_dict() for entry in entries])
        logger.bind(component="analytics").info("Analytics journal exported: {}", self.export_dir)
        return {"json": json_path, "csv": csv_path}

    def export_equity_curve(
        self,
        points: list[EquityCurvePoint],
        name: str,
    ) -> dict[str, Path]:
        """Export equity curve points as JSON and CSV."""
        rows = [point.to_dict() for point in points]
        json_path = self.export_dir / f"{name}_equity.json"
        csv_path = self.export_dir / f"{name}_equity.csv"
        self._write_json(json_path, rows)
        self._write_csv(csv_path, rows)
        logger.bind(component="analytics").info("Equity curve exported: {}", self.export_dir)
        return {"json": json_path, "csv": csv_path}

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({key for row in rows for key in row.keys()})
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def parquet_supported(self) -> bool:
        """Return whether Parquet export is currently available."""
        return False
