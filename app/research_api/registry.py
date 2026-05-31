"""Source registry for unified local research data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchSource:
    """One local report source."""

    source_id: str
    label_ar: str
    report_path: tuple[str, ...]


class ResearchSourceRegistry:
    """Registry of local research reports consumed by the unified API."""

    SOURCES = (
        ResearchSource(
            "signals",
            "ذكاء الإشارات",
            ("reports", "signal_intelligence", "intelligence_summary.json"),
        ),
        ResearchSource(
            "opportunities",
            "الفرص البحثية",
            ("reports", "opportunity_engine", "opportunity_summary.json"),
        ),
        ResearchSource("confluence", "التوافق", ("reports", "confluence", "summary.json")),
        ResearchSource(
            "market_regimes",
            "أنظمة السوق",
            ("reports", "market_regime", "regime_summary.json"),
        ),
        ResearchSource(
            "pattern_memory",
            "ذاكرة الأنماط",
            ("reports", "pattern_memory", "pattern_summary.json"),
        ),
        ResearchSource(
            "observation_pipeline",
            "مراقبة السوق",
            ("reports", "market_observation", "observation_summary.json"),
        ),
        ResearchSource(
            "signal_stream",
            "تدفق الإشارات",
            ("reports", "signal_stream", "signal_summary.json"),
        ),
        ResearchSource(
            "paper_execution",
            "التنفيذ الورقي",
            ("reports", "paper_execution", "paper_execution_summary.json"),
        ),
        ResearchSource(
            "paper_portfolio",
            "المحفظة الورقية",
            ("reports", "paper_portfolio", "portfolio_summary.json"),
        ),
        ResearchSource(
            "readiness",
            "الجاهزية",
            ("reports", "paper_live_readiness", "readiness_summary.json"),
        ),
        ResearchSource(
            "architecture_audit",
            "تدقيق المنصة",
            ("reports", "architecture_audit", "architecture_summary.json"),
        ),
        ResearchSource(
            "knowledge_graph",
            "خريطة المعرفة",
            ("reports", "knowledge_graph", "knowledge_summary.json"),
        ),
    )

    def all(self) -> tuple[ResearchSource, ...]:
        """Return all registered local sources."""
        return self.SOURCES
