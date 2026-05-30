"""Multi-timeframe score engine and conflict detection."""

from __future__ import annotations

from dataclasses import dataclass

from app.multi_timeframe.models import ConflictReport, MultiTimeframeScore, TimeframeState


@dataclass(frozen=True)
class TimeframeWeights:
    M1: float = 15.0
    M5: float = 25.0
    M15: float = 30.0
    H1: float = 30.0

    def to_dict(self) -> dict[str, float]:
        return {"M1": self.M1, "M5": self.M5, "M15": self.M15, "H1": self.H1}


class ConflictDetectionEngine:
    """Detect bullish/bearish, structure, trend, and confidence conflicts."""

    def detect(self, states: list[TimeframeState]) -> ConflictReport:
        labels = {state.state for state in states}
        conflicts = []
        if "صاعد" in labels and "هابط" in labels:
            conflicts.append("تعارض صاعد وهابط")
        low_confidence = [state.timeframe for state in states if state.confidence < 45]
        if low_confidence:
            conflicts.append("تعارض في الثقة")
        has_conflict = bool(conflicts)
        severity = "مرتفع" if "تعارض صاعد وهابط" in conflicts else "متوسط" if conflicts else "منخفض"
        penalty = 25.0 if severity == "مرتفع" else 12.0 if conflicts else 0.0
        return ConflictReport(
            has_conflict=has_conflict,
            severity=severity,
            conflicts=conflicts,
            score_penalty=penalty,
        )


class MultiTimeframeScoreEngine:
    """Score supported timeframe alignment with configurable weights."""

    def __init__(self, weights: TimeframeWeights | None = None) -> None:
        self.weights = weights or TimeframeWeights()

    def score(
        self,
        states: list[TimeframeState],
        conflict: ConflictReport,
    ) -> MultiTimeframeScore:
        weights = self.weights.to_dict()
        total_weight = sum(weights.values())
        raw = sum(state.confidence * weights[state.timeframe] for state in states)
        score = round(max(0.0, min(100.0, raw / total_weight - conflict.score_penalty)), 2)
        strengths = [
            f"{state.timeframe} {state.state}"
            for state in states
            if state.confidence >= 70
        ]
        weaknesses = list(conflict.conflicts)
        return MultiTimeframeScore(
            score=score,
            reasoning=f"درجة توافق الأطر الزمنية {score:.2f}.",
            strengths=strengths,
            weaknesses=weaknesses,
        )
