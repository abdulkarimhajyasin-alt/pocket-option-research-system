"""Pattern similarity engine."""

from __future__ import annotations

from app.pattern_memory.models import (
    DiscoveredPattern,
    PatternMemoryRecord,
    SimilarityResult,
)


class PatternSimilarityEngine:
    """Compare new records against historical pattern memory."""

    def compare(
        self,
        records: tuple[PatternMemoryRecord, ...],
        patterns: tuple[DiscoveredPattern, ...],
    ) -> tuple[SimilarityResult, ...]:
        if not patterns:
            return ()
        return tuple(self._compare_record(record, patterns) for record in records)

    def _compare_record(
        self,
        record: PatternMemoryRecord,
        patterns: tuple[DiscoveredPattern, ...],
    ) -> SimilarityResult:
        scored = [(self._score(record, pattern), pattern) for pattern in patterns]
        score, nearest = max(scored, key=lambda item: item[0])
        total = max(nearest.success_count + nearest.failure_count + nearest.neutral_count, 1)
        success_ratio = round(nearest.success_count / total * 100, 2)
        adjustment = round((success_ratio - 50) * (score / 100), 2)
        return SimilarityResult(
            record.pattern_id,
            score,
            self._category(score),
            nearest.pattern_key,
            success_ratio,
            adjustment,
        )

    def _score(self, record: PatternMemoryRecord, pattern: DiscoveredPattern) -> float:
        fields = {
            "asset": 15,
            "session": 15,
            "direction": 15,
            "structure": 15,
            "cisd": 12,
            "fvg": 10,
            "ifvg": 8,
            "liquidity": 10,
        }
        score = 0.0
        attrs = pattern.attributes
        for field_name, weight in fields.items():
            record_value = self._record_value(record, field_name)
            if attrs.get(field_name) == record_value:
                score += weight
        return round(score, 2)

    def _record_value(self, record: PatternMemoryRecord, field_name: str) -> str:
        if field_name == "structure":
            return record.structure_state
        state_name = f"{field_name}_state"
        if hasattr(record, state_name):
            return str(getattr(record, state_name))
        return str(getattr(record, field_name))

    def _category(self, score: float) -> str:
        if score >= 85:
            return "متشابه جدا"
        if score >= 70:
            return "متشابه"
        if score >= 50:
            return "متوسط"
        if score >= 25:
            return "ضعيف"
        return "غير مرتبط"
