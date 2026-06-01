"""Transition plan from research release to a separate future program."""

from __future__ import annotations

from app.post_research_architecture.models import TransitionPlan
from app.post_research_architecture.schemas import (
    FIRST_SAFE_NEXT_STEP,
    NEXT_PROGRAM_NAME,
)


class PostResearchTransitionPlanner:
    """Create a safe transition plan without implementing future capabilities."""

    def build(self) -> TransitionPlan:
        return TransitionPlan(
            recommended_next_program=NEXT_PROGRAM_NAME,
            required_decisions=[
                "Approve Research Platform v1.0 freeze",
                "Decide whether a separate architecture program should exist",
                "Define governance ownership",
                "Define compliance review owner",
            ],
            required_documentation=[
                "Final phase history",
                "Release manifest reconciliation",
                "Safety boundary document",
                "Future-program charter",
                "Risk governance requirements",
            ],
            required_validation=[
                "Full test suite",
                "Release packaging checks",
                "Certification checks",
                "Architecture audit checks",
                "Dashboard route checks",
            ],
            stop_conditions=[
                "Any request to add real broker access to this repository",
                "Any request to add credentials or login flows",
                "Any unresolved compliance concern",
                "Any missing human approval gate",
            ],
            forbidden_transitions=[
                "Research platform directly becomes an operational trading system",
                "Paper outputs are treated as real account instructions",
                "Dashboard actions are expanded into external actions",
                "Broker connectivity is added without a separate program",
            ],
            safe_transition_sequence=[
                "Freeze Research Platform v1.0",
                "Reconcile documentation and release metadata",
                "Write a separate program charter",
                "Review legal, compliance, and risk boundaries",
                "Decide go/no-go for architecture-only future work",
            ],
            first_safe_next_step=FIRST_SAFE_NEXT_STEP,
        )
