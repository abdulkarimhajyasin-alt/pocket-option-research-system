"""Roadmap builder for post-research strategic architecture."""

from __future__ import annotations

from app.post_research_architecture.models import PostResearchRoadmap
from app.post_research_architecture.schemas import (
    CURRENT_PLATFORM_STATE,
    NEXT_PROGRAM_NAME,
)


class PostResearchRoadmapBuilder:
    """Create a deterministic future-program roadmap."""

    def build(self) -> PostResearchRoadmap:
        stages = [
            "Research Platform Freeze",
            "Documentation & Metadata Reconciliation",
            "Architecture Separation Decision",
            "Future Trading System Requirements",
            "Risk Governance Design",
            "Execution Safety Design",
            "Broker Isolation Design",
            "Monitoring & Incident Response Design",
            "Legal/Compliance Review",
            "Paper-to-External Simulation Boundary Review",
            "External Integration Feasibility Study",
            "Go/No-Go Decision",
        ]
        return PostResearchRoadmap(
            current_platform_state=CURRENT_PLATFORM_STATE,
            next_program_name=NEXT_PROGRAM_NAME,
            roadmap_stages=stages,
            forbidden_shortcuts=[
                "Do not add real trading into the research repository.",
                "Do not add broker connectivity before a separate architecture program.",
                "Do not add credential handling to this platform.",
                "Do not convert paper-only outputs into operational instructions.",
            ],
            recommended_sequence=stages,
            safety_notes=[
                "The current platform remains research-only.",
                "All future implementation decisions require separate approval.",
                "No roadmap stage grants approval for real-world trading operations.",
            ],
        )
