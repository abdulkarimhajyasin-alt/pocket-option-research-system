"""Service functions for the unified local research API."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.research_api.aggregation import ResearchAggregationEngine
from app.research_api.diagnostics import ResearchAPIDiagnostics
from app.research_api.models import UnifiedResearchSnapshot
from app.research_api.registry import ResearchSourceRegistry
from app.research_api.reports import ResearchAPIReportWriter
from app.research_api.storage import ResearchAPIStorage


@dataclass(frozen=True)
class ResearchAPIRunResult:
    """Result of one unified research API materialization."""

    snapshot: UnifiedResearchSnapshot
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class UnifiedResearchAPIService:
    """Aggregate existing local research outputs into stable API views."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.registry = ResearchSourceRegistry()
        self.aggregation = ResearchAggregationEngine()
        self.diagnostics = ResearchAPIDiagnostics()
        self.storage = ResearchAPIStorage(self.project_root / "storage" / "research_api")
        self.reports = ResearchAPIReportWriter(self.project_root / "reports" / "research_api")

    def run(self) -> ResearchAPIRunResult:
        """Build, store, and report the unified snapshot."""
        snapshot = self.snapshot()
        storage_paths = self.storage.save(snapshot)
        report_paths = self.reports.export(snapshot)
        return ResearchAPIRunResult(snapshot, storage_paths, report_paths)

    def snapshot(self) -> UnifiedResearchSnapshot:
        """Return the deterministic unified research snapshot."""
        sources = self._sources()
        diagnostics = self.diagnostics.evaluate(sources)
        recommendations = self.diagnostics.recommendations(diagnostics)
        return self.aggregation.build_snapshot(
            sources,
            diagnostics,
            {"summary": recommendations, "research_only": True},
            self._metadata(),
        )

    def signals(self) -> dict[str, Any]:
        return self.snapshot().signals.to_dict()

    def opportunities(self) -> dict[str, Any]:
        return self.snapshot().opportunities.to_dict()

    def paper(self) -> dict[str, Any]:
        return self.snapshot().paper.to_dict()

    def readiness(self) -> dict[str, Any]:
        return self.snapshot().readiness.to_dict()

    def knowledge_graph(self) -> dict[str, Any]:
        return self.snapshot().knowledge_graph.to_dict()

    def diagnostics_view(self) -> dict[str, Any]:
        return self.snapshot().diagnostics.to_dict()

    def _sources(self) -> dict[str, dict[str, Any]]:
        sources: dict[str, dict[str, Any]] = {}
        for source in self.registry.all():
            payload = self._read_json(*source.report_path)
            sources[source.source_id] = payload if isinstance(payload, dict) else {}
        return sources

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _metadata(self) -> dict[str, bool]:
        return {
            "research_only": True,
            "local_only": True,
            "unified_api_only": True,
            "safe_internal_endpoints": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_account_login": True,
            "not_authentication": True,
            "not_external_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_money_handling": True,
            "not_position_management": True,
            "not_live_trading": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
            "not_broker_control": True,
        }
