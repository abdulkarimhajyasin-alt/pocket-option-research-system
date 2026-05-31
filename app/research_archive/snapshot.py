"""Deterministic local research snapshot engine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.research_archive.models import CREATED_AT, ResearchSnapshot
from app.research_archive.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class ArchiveSource:
    """One safe local source consumed by the archive."""

    source_id: str
    label_ar: str
    path: tuple[str, ...]


class ResearchSnapshotEngine:
    """Discover, normalize, and checksum local research outputs."""

    SOURCES = (
        ArchiveSource(
            "research_api",
            "واجهة البحث الموحدة",
            ("reports", "research_api", "research_summary.json"),
        ),
        ArchiveSource(
            "research_api_storage",
            "تخزين واجهة البحث",
            ("storage", "research_api", "unified_research_snapshot.json"),
        ),
        ArchiveSource(
            "knowledge_graph",
            "خريطة المعرفة",
            ("reports", "knowledge_graph", "knowledge_summary.json"),
        ),
        ArchiveSource(
            "knowledge_graph_storage",
            "تخزين خريطة المعرفة",
            ("storage", "knowledge_graph", "knowledge_summary.json"),
        ),
        ArchiveSource(
            "architecture_audit",
            "تدقيق المنصة",
            ("reports", "architecture_audit", "architecture_summary.json"),
        ),
        ArchiveSource(
            "architecture_storage",
            "تخزين تدقيق المنصة",
            ("storage", "architecture_audit", "architecture_summary.json"),
        ),
        ArchiveSource(
            "signals",
            "ذكاء الإشارات",
            ("reports", "signal_intelligence", "intelligence_summary.json"),
        ),
        ArchiveSource(
            "opportunities",
            "الفرص البحثية",
            ("reports", "opportunity_engine", "opportunity_summary.json"),
        ),
        ArchiveSource("confluence", "التوافق", ("reports", "confluence", "summary.json")),
        ArchiveSource(
            "market_regime",
            "أنظمة السوق",
            ("reports", "market_regime", "regime_summary.json"),
        ),
        ArchiveSource(
            "pattern_memory",
            "ذاكرة الأنماط",
            ("reports", "pattern_memory", "pattern_summary.json"),
        ),
        ArchiveSource(
            "observation",
            "المراقبة البحثية",
            ("reports", "market_observation", "observation_summary.json"),
        ),
        ArchiveSource(
            "signal_stream",
            "تدفق الإشارات",
            ("reports", "signal_stream", "signal_summary.json"),
        ),
        ArchiveSource(
            "paper_execution",
            "التنفيذ الورقي",
            ("reports", "paper_execution", "paper_execution_summary.json"),
        ),
        ArchiveSource(
            "paper_portfolio",
            "المحفظة الورقية",
            ("reports", "paper_portfolio", "portfolio_summary.json"),
        ),
        ArchiveSource(
            "readiness",
            "الجاهزية",
            ("reports", "paper_live_readiness", "readiness_summary.json"),
        ),
    )

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.corrupted_sources: list[dict[str, str]] = []

    def build_snapshot(self, version: str = "current") -> ResearchSnapshot:
        """Build a deterministic snapshot for the current local research state."""
        included = []
        missing = []
        self.corrupted_sources = []
        for source in self.SOURCES:
            path = self.project_root.joinpath(*source.path)
            payload = self._read_json(path, source.source_id)
            if payload is None:
                missing.append(self._source_entry(source, path))
                continue
            included.append(
                {
                    **self._source_entry(source, path),
                    "summary": self._summarize_payload(payload),
                    "payload": payload,
                }
            )
        source_summary = {
            "expected_source_count": len(self.SOURCES),
            "included_source_count": len(included),
            "missing_source_count": len(missing),
            "corrupted_source_count": len(self.corrupted_sources),
            "source_coverage": self._coverage(len(included), len(self.SOURCES)),
        }
        checksum_payload = {
            "schema_version": SCHEMA_VERSION,
            "source_summary": source_summary,
            "included_sources": included,
            "missing_sources": missing,
            "safety_status": self.safety_status(),
        }
        checksum = self._checksum(checksum_payload)
        return ResearchSnapshot(
            snapshot_id=f"snapshot-{checksum[:12]}",
            version=version,
            created_at=CREATED_AT,
            source_summary=source_summary,
            included_sources=included,
            missing_sources=missing,
            checksum=checksum,
            safety_status=self.safety_status(),
        )

    def safety_status(self) -> dict[str, bool]:
        """Return explicit research-only safety metadata."""
        return {
            "research_only": True,
            "local_only": True,
            "archive_only": True,
            "no_broker_access": True,
            "no_broker_api": True,
            "no_account_login": True,
            "no_credentials": True,
            "no_browser_automation": True,
            "no_real_trade_control": True,
            "no_order_placement": True,
            "no_live_trading": True,
            "no_money_handling": True,
            "no_external_service_calls": True,
        }

    def _source_entry(self, source: ArchiveSource, path: Path) -> dict[str, str]:
        return {
            "source_id": source.source_id,
            "label_ar": source.label_ar,
            "path": str(path.relative_to(self.project_root)),
        }

    def _read_json(self, path: Path, source_id: str) -> Any:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.corrupted_sources.append({"source_id": source_id, "error": str(exc)})
            return None

    def _summarize_payload(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {
                "payload_type": "dict",
                "key_count": len(payload),
                "top_level_keys": sorted(str(key) for key in payload.keys())[:30],
            }
        if isinstance(payload, list):
            return {"payload_type": "list", "item_count": len(payload)}
        return {"payload_type": type(payload).__name__}

    def _coverage(self, included: int, expected: int) -> float:
        if expected <= 0:
            return 0.0
        return round((included / expected) * 100.0, 4)

    def _checksum(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
