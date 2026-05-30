"""Cached, path-safe report repository for dashboard and diagnostics."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.dashboard.models import ReportContent, ReportFile


SUPPORTED_SUFFIXES = {".json": "json", ".txt": "text", ".csv": "csv"}


@dataclass
class ReportRepositoryMetrics:
    """Operational metrics for report indexing."""

    cache_hits: int = 0
    cache_misses: int = 0
    refresh_count: int = 0

    def to_dict(self) -> dict[str, int]:
        """Return metrics as a plain dictionary."""
        return {
            "report_cache_hits": self.cache_hits,
            "report_cache_misses": self.cache_misses,
            "repository_refresh_count": self.refresh_count,
        }


class ReportIndex:
    """Lazy cached index of supported local report files."""

    def __init__(self, project_root: Path | str = ".", reports_dir: Path | str = "reports") -> None:
        self.project_root = Path(project_root).resolve()
        self.reports_dir = self._resolve_inside_project(reports_dir)
        self.metrics = ReportRepositoryMetrics()
        self._reports: list[ReportFile] | None = None
        self._by_id: dict[str, ReportFile] = {}

    def list_reports(self) -> list[ReportFile]:
        """Return cached reports, loading lazily on first access."""
        if self._reports is None:
            self.metrics.cache_misses += 1
            self.refresh()
        else:
            self.metrics.cache_hits += 1
        return list(self._reports or [])

    def get(self, report_id: str) -> ReportFile | None:
        """Return one report metadata record by id."""
        if self._reports is None:
            self.metrics.cache_misses += 1
            self.refresh()
        else:
            self.metrics.cache_hits += 1
        return self._by_id.get(report_id)

    def invalidate(self) -> None:
        """Clear cached report metadata."""
        self._reports = None
        self._by_id = {}

    def refresh(self) -> list[ReportFile]:
        """Rebuild the report metadata cache."""
        self.metrics.refresh_count += 1
        reports: list[ReportFile] = []
        if not self.reports_dir.exists():
            logger.bind(component="reports").warning(
                "Reports directory missing: {}",
                self.reports_dir,
            )
            self._reports = []
            self._by_id = {}
            return []

        for path in self.reports_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            safe_path = self.validate_report_path(path)
            stat = safe_path.stat()
            relative = safe_path.relative_to(self.project_root).as_posix()
            reports.append(
                ReportFile(
                    report_id=self._report_id(relative),
                    name=safe_path.name,
                    path=safe_path,
                    relative_path=relative,
                    report_type=SUPPORTED_SUFFIXES[safe_path.suffix.lower()],
                    size_bytes=stat.st_size,
                    modified_at=self._format_timestamp(stat.st_mtime),
                )
            )

        reports.sort(key=lambda item: item.path.stat().st_mtime, reverse=True)
        self._reports = reports
        self._by_id = {report.report_id: report for report in reports}
        return list(reports)

    def validate_report_path(self, path: Path | str) -> Path:
        """Resolve and validate that a report path is inside the configured report root."""
        resolved = Path(path).resolve()
        if not self._is_relative_to(resolved, self.reports_dir):
            raise ValueError(f"Report path escapes report directory: {path}")
        if not self._is_relative_to(resolved, self.project_root):
            raise ValueError(f"Report path escapes project root: {path}")
        if resolved.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported report type: {resolved.suffix}")
        return resolved

    def _resolve_inside_project(self, reports_dir: Path | str) -> Path:
        path = Path(reports_dir)
        if not path.is_absolute():
            path = self.project_root / path
        resolved = path.resolve()
        if not self._is_relative_to(resolved, self.project_root):
            raise ValueError(f"Reports directory escapes project root: {reports_dir}")
        return resolved

    def _is_relative_to(self, child: Path, parent: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    def _report_id(self, relative_path: str) -> str:
        return hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:16]

    def _format_timestamp(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


class ReportRepository:
    """Cached report lookup and parsing boundary for dashboard consumers."""

    def __init__(
        self,
        project_root: Path | str = ".",
        reports_dir: Path | str = "reports",
        index: ReportIndex | None = None,
    ) -> None:
        self.index = index or ReportIndex(project_root, reports_dir)
        self.project_root = self.index.project_root
        self.reports_dir = self.index.reports_dir
        self._content_cache: dict[str, ReportContent] = {}

    @property
    def metrics(self) -> ReportRepositoryMetrics:
        """Return repository metrics."""
        return self.index.metrics

    def list_reports(self) -> list[ReportFile]:
        """Return supported reports sorted by newest first."""
        return self.index.list_reports()

    def refresh(self) -> list[ReportFile]:
        """Refresh metadata and parsed content caches."""
        self._content_cache = {}
        return self.index.refresh()

    def invalidate(self) -> None:
        """Invalidate all report caches."""
        self._content_cache = {}
        self.index.invalidate()

    def get_report(self, report_id: str) -> ReportContent | None:
        """Return parsed report content for a report id."""
        if report_id in self._content_cache:
            self.metrics.cache_hits += 1
            return self._content_cache[report_id]
        self.metrics.cache_misses += 1
        report = self.index.get(report_id)
        if report is None:
            logger.bind(component="reports").warning("Report not found: {}", report_id)
            return None
        content = self._parse_report(report)
        self._content_cache[report_id] = content
        return content

    def latest(self, reports: list[ReportFile], *parts: str) -> ReportFile | None:
        """Return newest report whose path contains all requested path parts."""
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

    def diagnostics(self) -> dict[str, int]:
        """Return report repository diagnostics."""
        return self.metrics.to_dict()

    def _parse_report(self, report: ReportFile) -> ReportContent:
        path = self.index.validate_report_path(report.path)
        raw_text = self._read_text(path)
        title = report.relative_path
        if report.report_type == "json":
            return self._parse_json(report, title, raw_text)
        if report.report_type == "csv":
            return self._parse_csv(report, title, raw_text)
        return ReportContent(file=report, title=title, raw_text=raw_text)

    def _parse_json(self, report: ReportFile, title: str, raw_text: str) -> ReportContent:
        try:
            parsed = json.loads(raw_text)
            pretty = json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
            return ReportContent(file=report, title=title, raw_text=pretty, json_data=parsed)
        except json.JSONDecodeError as exc:
            logger.bind(component="reports").warning(
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
            logger.bind(component="reports").warning(
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
