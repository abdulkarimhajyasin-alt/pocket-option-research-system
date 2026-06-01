"""Go/no-go criteria and decision readiness engine."""

from __future__ import annotations

from typing import Any

from app.trading_requirements.models import GoNoGoCriterion
from app.trading_requirements.schemas import SAFE_DECISION_STATES


class TradingGoNoGoEngine:
    """Build and evaluate requirements-only go/no-go criteria."""

    def build_criteria(self) -> list[dict[str, Any]]:
        topics = [
            "Research platform frozen",
            "Documentation complete",
            "Risk architecture approved",
            "Compliance review complete",
            "Broker terms reviewed",
            "Monitoring architecture approved",
            "Human approval process defined",
            "Kill switch architecture defined",
            "External integration feasibility reviewed",
        ]
        return [
            GoNoGoCriterion(
                criterion_id=f"GNG-{index:02d}",
                title=title,
                current_status="missing",
                blocks_progress=True,
                may_approve_live_trading=False,
            ).to_dict()
            for index, title in enumerate(topics, 1)
        ]

    def evaluate(self, criteria: list[dict[str, Any]]) -> dict[str, Any]:
        blockers = [item for item in criteria if item.get("blocks_progress")]
        missing = [item for item in criteria if item.get("current_status") != "complete"]
        state = "Ready For Architecture Review" if not missing else "Requirements Incomplete"
        if blockers:
            state = "Not Ready"
        if state not in SAFE_DECISION_STATES:
            state = "Not Ready"
        return {
            "decision_state": state,
            "criteria": criteria,
            "blocker_count": len(blockers),
            "missing_approval_count": len(missing),
            "decision_recommendation": (
                "Complete requirements and approvals before architecture review."
            ),
            "requirements_only": True,
            "architecture_only": True,
            "research_only": True,
            "local_only": True,
        }


class TradingConstraintEngine:
    """Classify constraints for coverage summaries."""

    def summarize(self, constraints: dict[str, dict[str, Any]]) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        for category in constraints.values():
            category_items = category.get("items", []) if isinstance(category, dict) else []
            items.extend(item for item in category_items if isinstance(item, dict))
        by_type: dict[str, int] = {}
        for item in items:
            constraint_type = str(item.get("constraint_type", "hard"))
            by_type[constraint_type] = by_type.get(constraint_type, 0) + 1
        return {
            "total_constraints": len(items),
            "by_type": by_type,
            "hard_constraints": by_type.get("hard", 0),
            "soft_constraints": by_type.get("soft", 0),
            "future_only_constraints": by_type.get("future-only", 0),
            "forbidden_now_constraints": by_type.get("forbidden-now", 0),
        }
