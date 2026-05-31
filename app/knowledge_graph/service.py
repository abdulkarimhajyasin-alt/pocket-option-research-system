"""Service orchestration for the research knowledge graph."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.knowledge_graph.analytics import KnowledgeGraphAnalytics
from app.knowledge_graph.diagnostics import KnowledgeGraphDiagnostics
from app.knowledge_graph.graph import KnowledgeGraphEngine
from app.knowledge_graph.intelligence import KnowledgeIntelligenceEngine
from app.knowledge_graph.models import KnowledgeGraphRun
from app.knowledge_graph.recommendations import KnowledgeGraphRecommendations
from app.knowledge_graph.reports import KnowledgeGraphReportWriter
from app.knowledge_graph.storage import KnowledgeGraphStorage


@dataclass(frozen=True)
class KnowledgeGraphRunResult:
    """Result of one knowledge graph run."""

    result: KnowledgeGraphRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class KnowledgeGraphService:
    """Build relationship intelligence from local research outputs only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.graph = KnowledgeGraphEngine()
        self.intelligence = KnowledgeIntelligenceEngine()
        self.analytics = KnowledgeGraphAnalytics()
        self.diagnostics = KnowledgeGraphDiagnostics()
        self.recommendations = KnowledgeGraphRecommendations()
        self.storage = KnowledgeGraphStorage(
            self.project_root / "storage" / "knowledge_graph"
        )
        self.reports = KnowledgeGraphReportWriter(
            self.project_root / "reports" / "knowledge_graph"
        )

    def run(self) -> KnowledgeGraphRunResult:
        metadata = self._metadata()
        sources = self._sources()
        graph = self.graph.build(sources, metadata)
        intelligence = self.intelligence.evaluate(graph)
        analytics = self.analytics.summarize(graph, intelligence)
        diagnostics = self.diagnostics.evaluate(graph)
        recommendations = self.recommendations.generate(diagnostics)
        result = KnowledgeGraphRun(
            timestamp=datetime.now(UTC),
            graph=graph,
            intelligence=intelligence,
            analytics=analytics,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=metadata,
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return KnowledgeGraphRunResult(result, storage_paths, report_paths)

    def _sources(self) -> dict[str, Any]:
        return {
            "signal_intelligence": self._read_json(
                "reports",
                "signal_intelligence",
                "intelligence_summary.json",
            ),
            "opportunity_engine": self._read_json(
                "reports",
                "opportunity_engine",
                "opportunity_summary.json",
            ),
            "confluence": self._read_json("reports", "confluence", "summary.json"),
            "market_regime": self._read_json(
                "reports",
                "market_regime",
                "regime_summary.json",
            ),
            "pattern_memory": self._read_json(
                "reports",
                "pattern_memory",
                "pattern_summary.json",
            ),
            "paper_execution": self._read_json(
                "reports",
                "paper_execution",
                "paper_execution_summary.json",
            ),
            "paper_portfolio": self._read_json(
                "reports",
                "paper_portfolio",
                "portfolio_summary.json",
            ),
            "paper_control_center": self._read_json(
                "reports",
                "paper_control_center",
                "control_center_summary.json",
            ),
            "research_certification": self._read_json(
                "reports",
                "research_certification",
                "certification_summary.json",
            ),
        }

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
            "relationship_intelligence_only": True,
            "local_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_account_login": True,
            "not_authentication": True,
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
