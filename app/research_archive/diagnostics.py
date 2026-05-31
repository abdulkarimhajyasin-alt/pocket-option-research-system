"""Diagnostics and recommendations for research archive outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research_archive.schemas import SCHEMA_VERSION


class ResearchArchiveDiagnostics:
    """Validate archive completeness, safety, and schema integrity."""

    def evaluate(
        self,
        snapshot: dict[str, Any],
        versions: list[dict[str, Any]],
        archive_index: list[dict[str, Any]],
        storage_dir: Path,
        corrupted_sources: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        self._missing_sources(snapshot, diagnostics)
        self._empty_snapshot(snapshot, diagnostics)
        self._duplicate_checksums(versions, diagnostics)
        self._broken_index(archive_index, diagnostics)
        self._missing_links(versions, diagnostics)
        self._latest_snapshot(storage_dir, diagnostics)
        self._schema(snapshot, diagnostics)
        self._safety(snapshot, diagnostics)
        self._corrupted(corrupted_sources, diagnostics)
        self._package(versions, storage_dir, diagnostics)
        return diagnostics

    def recommendations(self, diagnostics: list[dict[str, Any]]) -> list[str]:
        recommendations = [
            "تحسين اكتمال الأرشيف",
            "زيادة تغطية المصادر",
            "تقوية تتبع الإصدارات",
            "مراجعة الفروقات البحثية",
            "تحسين جودة البيانات التاريخية",
            "تقليل الملفات المفقودة",
            "الحفاظ على حدود البحث فقط",
        ]
        if not diagnostics:
            recommendations.append(
                "الأرشيف البحثي مكتمل ضمن الحدود المحلية الحالية."
            )
        return recommendations

    def _add(
        self,
        diagnostics: list[dict[str, Any]],
        code: str,
        severity: str,
        message: str,
    ) -> None:
        diagnostics.append({"code": code, "severity": severity, "message": message})

    def _missing_sources(self, snapshot: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
        missing = snapshot.get("missing_sources", [])
        if missing:
            self._add(diagnostics, "missing_expected_sources", "متوسط", "توجد مصادر بحثية مفقودة.")

    def _empty_snapshot(self, snapshot: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
        if not snapshot.get("included_sources"):
            self._add(diagnostics, "empty_snapshot", "مرتفع", "اللقطة البحثية فارغة.")

    def _duplicate_checksums(
        self,
        versions: list[dict[str, Any]],
        diagnostics: list[dict[str, Any]],
    ) -> None:
        checksums = [item.get("checksum") for item in versions if item.get("checksum")]
        if len(checksums) != len(set(checksums)):
            self._add(diagnostics, "duplicate_checksums", "منخفض", "توجد إصدارات بنفس البصمة.")

    def _broken_index(
        self,
        archive_index: list[dict[str, Any]],
        diagnostics: list[dict[str, Any]],
    ) -> None:
        if any(not item.get("archive_id") for item in archive_index):
            self._add(diagnostics, "broken_archive_index", "مرتفع", "فهرس الأرشيف غير مكتمل.")

    def _missing_links(
        self,
        versions: list[dict[str, Any]],
        diagnostics: list[dict[str, Any]],
    ) -> None:
        known = {item.get("version_id") for item in versions}
        for item in versions[1:]:
            if item.get("previous_version_id") not in known:
                self._add(diagnostics, "missing_version_links", "متوسط", "رابط إصدار سابق مفقود.")

    def _latest_snapshot(self, storage_dir: Path, diagnostics: list[dict[str, Any]]) -> None:
        if not (storage_dir / "latest_snapshot.json").exists():
            self._add(diagnostics, "missing_latest_snapshot", "متوسط", "آخر لقطة غير موجودة.")

    def _schema(self, snapshot: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
        if snapshot.get("schema_version") != SCHEMA_VERSION:
            self._add(diagnostics, "invalid_schema_version", "مرتفع", "إصدار المخطط غير صالح.")

    def _safety(self, snapshot: dict[str, Any], diagnostics: list[dict[str, Any]]) -> None:
        safety = snapshot.get("safety_status", {})
        if not snapshot.get("research_only") or not all(safety.values()):
            self._add(diagnostics, "unsafe_metadata", "مرتفع", "بيانات السلامة غير مؤكدة.")

    def _corrupted(
        self,
        corrupted_sources: list[dict[str, str]],
        diagnostics: list[dict[str, Any]],
    ) -> None:
        for item in corrupted_sources:
            self._add(
                diagnostics,
                "corrupted_json",
                "متوسط",
                f"ملف JSON غير صالح: {item.get('source_id')}",
            )

    def _package(
        self,
        versions: list[dict[str, Any]],
        storage_dir: Path,
        diagnostics: list[dict[str, Any]],
    ) -> None:
        for item in versions:
            label = str(item.get("version_label", ""))
            base = storage_dir / "snapshots" / label
            for name in (
                "snapshot.json",
                "source_manifest.json",
                "safety_manifest.json",
                "diagnostics.json",
            ):
                path = base / name
                if not path.exists():
                    self._add(
                        diagnostics,
                        "incomplete_archive_package",
                        "متوسط",
                        f"حزمة ناقصة: {path}",
                    )
                elif not self._valid_json(path):
                    self._add(
                        diagnostics,
                        "corrupted_json",
                        "متوسط",
                        f"JSON غير صالح: {path}",
                    )

    def _valid_json(self, path: Path) -> bool:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return True
