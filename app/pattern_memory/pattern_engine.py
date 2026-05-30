"""Pattern discovery engine."""

from __future__ import annotations

from collections import defaultdict

from app.pattern_memory.models import DiscoveredPattern, PatternMemoryRecord


class PatternDiscoveryEngine:
    """Detect recurring pattern combinations from memory records."""

    def discover(
        self,
        records: tuple[PatternMemoryRecord, ...],
    ) -> tuple[DiscoveredPattern, ...]:
        grouped: dict[tuple[str, ...], list[PatternMemoryRecord]] = defaultdict(list)
        for record in records:
            grouped[record.signature].append(record)
        patterns = [self._pattern(key, rows) for key, rows in grouped.items()]
        return tuple(sorted(patterns, key=lambda item: item.pattern_score, reverse=True))

    def _pattern(
        self,
        key: tuple[str, ...],
        rows: list[PatternMemoryRecord],
    ) -> DiscoveredPattern:
        success = sum(1 for row in rows if row.outcome_bucket == "successful")
        failure = sum(1 for row in rows if row.outcome_bucket == "failed")
        neutral = len(rows) - success - failure
        success_ratio = success / len(rows) if rows else 0.0
        failure_ratio = failure / len(rows) if rows else 0.0
        stability = self._clamp(100 - abs(success_ratio - failure_ratio) * 35)
        confluence = self._average(row.confluence_score for row in rows)
        opportunity = self._average(row.opportunity_score for row in rows)
        confidence = self._average(row.confidence_score for row in rows)
        recurrence = min(len(rows) * 12.5, 100.0)
        score = self._clamp(
            success_ratio * 35
            + stability * 0.2
            + confluence * 0.15
            + opportunity * 0.15
            + confidence * 0.1
            + recurrence * 0.05
        )
        attributes = {
            "asset": key[0],
            "session": key[1],
            "direction": key[2],
            "structure": key[3],
            "cisd": key[4],
            "fvg": key[5],
            "ifvg": key[6],
            "liquidity": key[7],
        }
        return DiscoveredPattern(
            pattern_key=" | ".join(key),
            description=" + ".join(key),
            occurrences=len(rows),
            success_count=success,
            failure_count=failure,
            neutral_count=neutral,
            stability=stability,
            pattern_score=score,
            average_confluence=confluence,
            average_opportunity=opportunity,
            average_confidence=confidence,
            attributes=attributes,
        )

    def _average(self, values: object) -> float:
        numbers = [float(value) for value in values]
        return round(sum(numbers) / len(numbers), 2) if numbers else 0.0

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, value)), 2)
