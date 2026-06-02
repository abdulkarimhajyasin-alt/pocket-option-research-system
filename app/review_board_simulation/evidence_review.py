"""Evidence review engine for local review-board simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import EvidenceReviewResult
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewEvidenceEngine:
    """Review available local artifacts and classify evidence readiness."""

    def review(self, sources: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
        expected = sorted(
            {
                source
                for board in registry.get("boards", [])
                for criterion in board.get("criteria", [])
                for source in criterion.get("required_sources", [])
            }
        )
        items = []
        for index, group in enumerate(expected, start=1):
            source = sources.get("sources", {}).get(group, {})
            count = int(source.get("file_count", 0))
            missing = [] if count else [group]
            weak = []
            if 0 < count < 3:
                weak.append("Limited local JSON evidence volume")
            readiness = self._readiness(count)
            items.append(
                EvidenceReviewResult(
                    evidence_id=f"EVID-{index:02d}",
                    source_group=group,
                    available_files=count,
                    readiness_state=readiness,
                    missing_evidence=missing,
                    weak_evidence=weak,
                    linkage_score=min(100.0, float(count) * 12.5),
                ).to_dict()
            )
        return {"items": items, **SIMULATION_ONLY_FLAGS}

    def _readiness(self, count: int) -> str:
        if count >= 5:
            return "Simulated Pass"
        if count >= 3:
            return "Simulated Conditional Pass"
        if count > 0:
            return "Requires Human Review"
        return "Simulated Not Ready"
