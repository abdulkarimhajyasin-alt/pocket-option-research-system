"""Multi-timeframe confirmation engine."""

from __future__ import annotations

from datetime import datetime

from app.multi_timeframe.models import ConfirmationResult, TimeframeState
from app.multi_timeframe.scoring import ConflictDetectionEngine, MultiTimeframeScoreEngine
from app.multi_timeframe.structure_alignment import StructureAlignmentEngine
from app.multi_timeframe.trend_alignment import TrendAlignmentEngine


class TimeframeStateEngine:
    """Derive deterministic timeframe states from one qualified opportunity."""

    supported_timeframes = ("M1", "M5", "M15", "H1")

    def states_for(self, opportunity: dict) -> list[TimeframeState]:
        base = self._base_state(opportunity.get("classification", ""))
        score = float(opportunity.get("qualification_score", 0.0) or 0.0)
        timestamp = datetime.fromisoformat(str(opportunity.get("timestamp")))
        offsets = {"M1": 0.0, "M5": 6.0, "M15": 10.0, "H1": -4.0}
        states = []
        for timeframe in self.supported_timeframes:
            confidence = max(0.0, min(100.0, score + offsets[timeframe]))
            state = base
            if confidence < 45:
                state = "محايد"
            elif 45 <= confidence < 60:
                state = "انتقالي"
            states.append(TimeframeState(timeframe, state, round(confidence, 2), timestamp))
        return states

    def _base_state(self, classification: str) -> str:
        if "صعودي" in classification:
            return "صاعد"
        if "هبوطي" in classification:
            return "هابط"
        return "محايد"


class MultiTimeframeConfirmationEngine:
    """Confirm qualified opportunities across multiple timeframes."""

    def __init__(self) -> None:
        self.state_engine = TimeframeStateEngine()
        self.structure = StructureAlignmentEngine()
        self.trend = TrendAlignmentEngine()
        self.conflict = ConflictDetectionEngine()
        self.scoring = MultiTimeframeScoreEngine()

    def confirm(self, ranking: dict) -> ConfirmationResult:
        opportunity = ranking.get("opportunity", {})
        states = self.state_engine.states_for(opportunity)
        alignment = self.structure.evaluate(states)
        trend = self.trend.evaluate(states)
        conflict = self.conflict.detect(states)
        score = self.scoring.score(states, conflict)
        confirmation_score = round(
            max(
                0.0,
                min(
                    100.0,
                    score.score * 0.55
                    + trend.score * 0.25
                    + alignment.full_alignment_score * 0.2,
                ),
            ),
            2,
        )
        state = self._state(confirmation_score, conflict.has_conflict)
        supporting = score.strengths + [alignment.state_ar]
        conflicting = score.weaknesses + conflict.conflicts
        return ConfirmationResult(
            opportunity_id=str(opportunity.get("opportunity_id", "")),
            asset=str(opportunity.get("asset", "")),
            classification=str(opportunity.get("classification", "")),
            timestamp=datetime.fromisoformat(str(opportunity.get("timestamp"))),
            timeframe_states=tuple(states),
            alignment=alignment,
            trend=trend,
            conflict=conflict,
            score=score,
            confirmation_score=confirmation_score,
            confirmation_state=state,
            supporting_factors=supporting,
            conflicting_factors=conflicting,
            alignment_explanation=alignment.explanation,
            session=self._session(opportunity),
            metadata={"research_only": True, "not_recommendation": True, "not_execution": True},
        )

    def _state(self, score: float, has_conflict: bool) -> str:
        if has_conflict and score < 70:
            return "متضارب"
        if score >= 90:
            return "مؤكد بقوة"
        if score >= 75:
            return "مؤكد"
        if score >= 55:
            return "جزئي"
        return "مرفوض"

    def _session(self, opportunity: dict) -> str:
        for value in opportunity.get("supporting_factors", []):
            if "جلسة" in str(value) or "الجلسة" in str(value):
                return str(value)
        return "غير متاح"
