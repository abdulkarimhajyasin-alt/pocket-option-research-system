"""Boundary model for post-research architecture planning."""

from __future__ import annotations

from app.post_research_architecture.models import PostResearchBoundaryModel


class PostResearchBoundaryBuilder:
    """Build the current and future-only architecture boundaries."""

    def build(self) -> PostResearchBoundaryModel:
        return PostResearchBoundaryModel(
            allowed_now=[
                "research reports",
                "local dashboards",
                "local APIs",
                "architecture documents",
                "gap analysis",
                "simulation analysis",
                "paper-only outputs",
                "readiness reports",
                "certification reports",
                "release reports",
            ],
            forbidden_now=[
                "live broker access",
                "login",
                "credentials",
                "browser automation",
                "trade execution",
                "order placement",
                "money movement",
                "real account monitoring",
                "account modification",
                "external execution adapters",
                "real trading operations",
            ],
            future_only_not_current=[
                "broker adapter design",
                "execution gateway design",
                "operational risk design",
                "monitoring infrastructure design",
                "compliance review",
                "human approval workflows",
                "incident response playbooks",
            ],
        )
