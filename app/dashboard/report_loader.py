"""Report discovery and parsing for the local dashboard."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.dashboard.models import ReportContent, ReportFile


SUPPORTED_SUFFIXES = {".json": "json", ".txt": "text", ".csv": "csv"}


class DashboardReportLoader:
    """Discover and parse local report artifacts."""

    def __init__(self, project_root: Path | str = ".", reports_dir: Path | str = "reports") -> None:
        self.project_root = Path(project_root)
        self.reports_dir = self._resolve_inside_project(reports_dir)

    def list_reports(self) -> list[ReportFile]:
        """Return supported reports sorted by newest first."""
        if not self.reports_dir.exists():
            logger.bind(component="dashboard").warning(
                "Reports directory missing: {}",
                self.reports_dir,
            )
            return []
        reports: list[ReportFile] = []
        for path in self.reports_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            stat = path.stat()
            relative = path.relative_to(self.project_root).as_posix()
            reports.append(
                ReportFile(
                    report_id=self._report_id(relative),
                    name=path.name,
                    path=path,
                    relative_path=relative,
                    report_type=SUPPORTED_SUFFIXES[path.suffix.lower()],
                    size_bytes=stat.st_size,
                    modified_at=self._format_timestamp(stat.st_mtime),
                )
            )
        return sorted(reports, key=lambda item: item.path.stat().st_mtime, reverse=True)

    def get_report(self, report_id: str) -> ReportContent | None:
        """Return parsed report content for a report ID."""
        report = next((item for item in self.list_reports() if item.report_id == report_id), None)
        if report is None:
            logger.bind(component="dashboard").warning("Report not found: {}", report_id)
            return None
        raw_text = self._read_text(report.path)
        title = report.relative_path
        if report.report_type == "json":
            return self._parse_json(report, title, raw_text)
        if report.report_type == "csv":
            return self._parse_csv(report, title, raw_text)
        return ReportContent(file=report, title=title, raw_text=raw_text)

    def latest(self, reports: list[ReportFile], *parts: str) -> ReportFile | None:
        """Return newest report whose relative path contains all requested parts."""
        lowered = [part.lower() for part in parts]
        for report in reports:
            path = report.relative_path.lower()
            if all(part in path for part in lowered):
                return report
        return None

    def latest_json(self, reports: list[ReportFile], *parts: str) -> dict[str, Any]:
        """Return parsed JSON from the newest matching JSON report."""
        report = self.latest(
            [item for item in reports if item.report_type == "json"],
            *parts,
        )
        if report is None:
            return {}
        content = self.get_report(report.report_id)
        return dict(content.json_data) if content and isinstance(content.json_data, dict) else {}

    def _parse_json(self, report: ReportFile, title: str, raw_text: str) -> ReportContent:
        try:
            parsed = json.loads(raw_text)
            pretty = json.dumps(parsed, indent=2, sort_keys=True)
            return ReportContent(file=report, title=title, raw_text=pretty, json_data=parsed)
        except json.JSONDecodeError as exc:
            logger.bind(component="dashboard").warning(
                "Failed to parse JSON report {}: {}",
                report.relative_path,
                exc,
            )
            return ReportContent(file=report, title=title, raw_text=raw_text, error=str(exc))

    def _parse_csv(self, report: ReportFile, title: str, raw_text: str) -> ReportContent:
        try:
            rows = list(csv.reader(raw_text.splitlines()))
            headers = rows[0] if rows else []
            return ReportContent(
                file=report,
                title=title,
                raw_text=raw_text,
                csv_headers=headers,
                csv_rows=rows[1:201],
            )
        except csv.Error as exc:
            logger.bind(component="dashboard").warning(
                "Failed to parse CSV report {}: {}",
                report.relative_path,
                exc,
            )
            return ReportContent(file=report, title=title, raw_text=raw_text, error=str(exc))

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="replace")

    def _resolve_inside_project(self, reports_dir: Path | str) -> Path:
        path = Path(reports_dir)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def _report_id(self, relative_path: str) -> str:
        return hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:16]

    def _format_timestamp(self, timestamp: float) -> str:
        from datetime import UTC, datetime

        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
