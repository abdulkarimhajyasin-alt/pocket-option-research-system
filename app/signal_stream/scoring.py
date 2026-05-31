"""Scoring helpers and signal stream scoring engine."""

from __future__ import annotations

from app.signal_stream.models import SignalEvent
from app.signal_stream.models import SignalScoreResult


def clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return clamp(sum(clamp(value) for value in values) / len(values))


def readiness_state(score: float) -> tuple[str, str]:
    if score >= 95:
        return "ممتاز", "تدفق الإشارات مستقر وعالي الجودة للبحث."
    if score >= 85:
        return "قوي", "تدفق الإشارات قوي مع فجوات محدودة."
    if score >= 70:
        return "مقبول", "تدفق الإشارات قابل للتحليل مع حاجة للمراجعة."
    if score >= 50:
        return "ضعيف", "تدفق الإشارات يحتاج تحسين الجودة والثقة."
    return "مرفوض", "تدفق الإشارات غير كاف للاعتماد البحثي."


class SignalStreamScoringEngine:
    """Evaluate confidence quality, signal quality, stability, and consistency."""

    def evaluate(self, events: tuple[SignalEvent, ...]) -> SignalScoreResult:
        confidence_quality = average([item.confidence for item in events])
        signal_quality = average([item.quality for item in events])
        stream_stability = clamp(min(100.0, len(events) * 8.0))
        directional = [item.direction.value for item in events]
        duplicates = len(directional) - len(set(zip(directional, [e.asset for e in events])))
        signal_consistency = clamp(100.0 - max(0, duplicates) * 5.0)
        score = average(
            [
                confidence_quality,
                signal_quality,
                stream_stability,
                signal_consistency,
            ]
        )
        state, explanation = readiness_state(score)
        return SignalScoreResult(
            score=score,
            state=state,
            explanation=explanation,
            confidence_quality=confidence_quality,
            signal_quality=signal_quality,
            stream_stability=stream_stability,
            signal_consistency=signal_consistency,
        )
