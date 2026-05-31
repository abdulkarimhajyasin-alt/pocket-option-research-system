"""Service layer for research archive and versioning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.research_archive.archive import ResearchArchiveEngine
from app.research_archive.diagnostics import ResearchArchiveDiagnostics
from app.research_archive.diff import ResearchDiffEngine
from app.research_archive.evolution import ResearchEvolutionEngine
from app.research_archive.models import ResearchArchiveRecord, ResearchSnapshot, ResearchVersion
from app.research_archive.reports import ResearchArchiveReportWriter
from app.research_archive.snapshot import ResearchSnapshotEngine
from app.research_archive.storage import ResearchArchiveStorage
from app.research_archive.versioning import ResearchVersioningEngine


@dataclass(frozen=True)
class ResearchArchiveRunResult:
    """Result of a full research archive cycle."""

    snapshot: ResearchSnapshot
    version: ResearchVersion
    archive_record: ResearchArchiveRecord
    diff: dict[str, Any]
    evolution: dict[str, Any]
    diagnostics: list[dict[str, Any]]
    recommendations: list[str]
    report_paths: dict[str, str]


class ResearchArchiveService:
    """Build, version, compare, and report local research archives."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.storage = ResearchArchiveStorage(self.project_root / "storage" / "research_archive")
        self.snapshot_engine = ResearchSnapshotEngine(self.project_root)
        self.versioning = ResearchVersioningEngine(self.storage.output_dir)
        self.archive = ResearchArchiveEngine(self.storage)
        self.diff_engine = ResearchDiffEngine()
        self.evolution = ResearchEvolutionEngine()
        self.diagnostics = ResearchArchiveDiagnostics()
        self.reports = ResearchArchiveReportWriter(
            self.project_root / "reports" / "research_archive"
        )

    def build_current_snapshot(self) -> ResearchSnapshot:
        return self.snapshot_engine.build_snapshot()

    def create_archive_version(
        self,
        force: bool = False,
    ) -> tuple[ResearchVersion, ResearchArchiveRecord]:
        snapshot = self.build_current_snapshot()
        history = self.storage.load_versions()
        version, new_version = self.versioning.assign_version(snapshot, history, force=force)
        snapshot = ResearchSnapshot(
            snapshot_id=snapshot.snapshot_id,
            version=version.version_label,
            created_at=snapshot.created_at,
            source_summary=snapshot.source_summary,
            included_sources=snapshot.included_sources,
            missing_sources=snapshot.missing_sources,
            checksum=snapshot.checksum,
            safety_status=snapshot.safety_status,
        )
        diagnostics = self._diagnostics(snapshot)
        record = self.archive.persist(snapshot, version, diagnostics, new_version=new_version)
        return version, record

    def get_latest_version(self) -> dict[str, Any]:
        return self.versioning.latest_version(self.storage.load_versions())

    def get_version_history(self) -> list[dict[str, Any]]:
        return self.storage.load_versions()

    def compare_latest_with_previous(self) -> dict[str, Any]:
        history = self.storage.load_versions()
        if len(history) < 2:
            latest = history[-1] if history else {}
            current = (
                self.storage.load_snapshot(str(latest.get("version_label", "")))
                if latest
                else {}
            )
            diff = self.diff_engine.compare({}, current).to_dict()
        else:
            previous = self.storage.load_snapshot(str(history[-2].get("version_label", "")))
            current = self.storage.load_snapshot(str(history[-1].get("version_label", "")))
            diff = self.diff_engine.compare(previous, current).to_dict()
            previous_label = history[-2].get("version_label")
            current_label = history[-1].get("version_label")
            name = f"diff_{previous_label}_to_{current_label}.json"
            self.storage.save_diff(name, diff)
        self.storage.save_diff("latest_diff.json", diff)
        return diff

    def generate_evolution_report(self) -> dict[str, Any]:
        history = self.storage.load_versions()
        snapshots = [
            self.storage.load_snapshot(str(item.get("version_label", "")))
            for item in history
        ]
        diagnostics = self._load_all_diagnostics(history)
        recommendations = self.diagnostics.recommendations(diagnostics)
        report = self.evolution.analyze(history, snapshots, diagnostics, recommendations).to_dict()
        self.storage.save_evolution(report)
        return report

    def generate_archive_summary(self) -> dict[str, Any]:
        history = self.storage.load_versions()
        latest = self.get_latest_version()
        latest_snapshot = (
            self.storage.load_snapshot(str(latest.get("version_label", ""))) if latest else {}
        )
        diagnostics = self._diagnostics_from_current(latest_snapshot)
        recommendations = self.diagnostics.recommendations(diagnostics)
        return {
            "latest_version": latest.get("version_label"),
            "version_count": len(history),
            "latest_snapshot": latest_snapshot.get("snapshot_id"),
            "archived_source_count": latest_snapshot.get("source_summary", {}).get(
                "included_source_count",
                0,
            ),
            "missing_source_count": latest_snapshot.get("source_summary", {}).get(
                "missing_source_count",
                0,
            ),
            "checksum": latest_snapshot.get("checksum"),
            "safety_status": latest_snapshot.get("safety_status", {}),
            "diagnostics_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            "research_only": True,
            "local_only": True,
        }

    def run_full_archive_cycle(self, force: bool = False) -> ResearchArchiveRunResult:
        version, record = self.create_archive_version(force=force)
        latest_snapshot = self.storage.load_snapshot(version.version_label)
        diagnostics = self._diagnostics_from_current(latest_snapshot)
        diff = self.compare_latest_with_previous()
        evolution = self.generate_evolution_report()
        recommendations = self.diagnostics.recommendations(diagnostics)
        summary = self.generate_archive_summary()
        report_paths = self.reports.export(
            summary,
            self.get_version_history(),
            self.get_latest_version(),
            diff,
            evolution,
            diagnostics,
            recommendations,
        )
        return ResearchArchiveRunResult(
            snapshot=self.snapshot_engine.build_snapshot(version.version_label),
            version=version,
            archive_record=record,
            diff=diff,
            evolution=evolution,
            diagnostics=diagnostics,
            recommendations=recommendations,
            report_paths=report_paths,
        )

    def _diagnostics(self, snapshot: ResearchSnapshot) -> list[dict[str, Any]]:
        return self._diagnostics_from_current(snapshot.to_dict())

    def _diagnostics_from_current(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        return self.diagnostics.evaluate(
            snapshot,
            self.storage.load_versions(),
            self.storage.load_archive_index(),
            self.storage.output_dir,
            self.snapshot_engine.corrupted_sources,
        )

    def _load_all_diagnostics(self, history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        for item in history:
            label = str(item.get("version_label", ""))
            path = self.storage.output_dir / "snapshots" / label / "diagnostics.json"
            if not path.exists():
                continue
            loaded = self.storage._read_list(path)
            diagnostics.extend(loaded)
        return diagnostics
