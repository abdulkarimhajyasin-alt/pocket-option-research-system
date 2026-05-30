"""Pattern quality and ranking engines."""

from __future__ import annotations

from collections import defaultdict

from app.pattern_memory.models import (
    DiscoveredPattern,
    PatternMemoryRecord,
    PatternQualityScore,
    PatternRanking,
)


class PatternQualityEngine:
    """Evaluate consistency, stability, reliability, recurrence, and sample size."""

    def evaluate(
        self,
        patterns: tuple[DiscoveredPattern, ...],
    ) -> tuple[PatternQualityScore, ...]:
        quality = []
        for pattern in patterns:
            total = max(pattern.occurrences, 1)
            reliability = round(pattern.success_count / total * 100, 2)
            recurrence = min(pattern.occurrences * 12.5, 100.0)
            sample_size = min(pattern.occurrences * 10.0, 100.0)
            consistency = self._clamp(100 - abs(reliability - 50) * 0.6)
            score = self._clamp(
                consistency * 0.2
                + pattern.stability * 0.25
                + reliability * 0.25
                + recurrence * 0.15
                + sample_size * 0.15
            )
            quality.append(
                PatternQualityScore(
                    pattern.pattern_key,
                    score,
                    consistency,
                    pattern.stability,
                    reliability,
                    recurrence,
                    sample_size,
                )
            )
        return tuple(sorted(quality, key=lambda item: item.score, reverse=True))

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, value)), 2)


class PatternRankingEngine:
    """Rank sessions, assets, structures, FVG, CISD, liquidity, and confluence."""

    RANKING_FIELDS = {
        "أفضل الجلسات": "session",
        "أفضل الأصول": "asset",
        "أفضل الهياكل": "structure_state",
        "أفضل أنواع FVG": "fvg_state",
        "أفضل أنواع CISD": "cisd_state",
        "أفضل حالات السيولة": "liquidity_state",
        "أفضل ملفات التوافق": "confluence_profile",
    }

    def rank(self, records: tuple[PatternMemoryRecord, ...]) -> tuple[PatternRanking, ...]:
        rankings = []
        for category, field_name in self.RANKING_FIELDS.items():
            rows = self._rank_field(category, field_name, records)
            rankings.extend(rows)
        return tuple(rankings)

    def _rank_field(
        self,
        category: str,
        field_name: str,
        records: tuple[PatternMemoryRecord, ...],
    ) -> list[PatternRanking]:
        grouped: dict[str, list[PatternMemoryRecord]] = defaultdict(list)
        for record in records:
            value = self._field_value(record, field_name)
            grouped[value].append(record)
        scored = []
        for name, rows in grouped.items():
            success = sum(1 for row in rows if row.outcome_bucket == "successful")
            ratio = round(success / len(rows) * 100, 2) if rows else 0.0
            score = round(ratio * 0.65 + min(len(rows) * 10, 100) * 0.35, 2)
            scored.append((name, score, len(rows), ratio))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            PatternRanking(
                category,
                name,
                index,
                score,
                occurrences,
                ratio,
                "ترتيب بحثي مبني على التكرار ونسبة النجاح التاريخية.",
            )
            for index, (name, score, occurrences, ratio) in enumerate(scored[:5], start=1)
        ]

    def _field_value(self, record: PatternMemoryRecord, field_name: str) -> str:
        if field_name == "confluence_profile":
            if record.confluence_score >= 75:
                return "توافق قوي"
            if record.confluence_score >= 60:
                return "توافق متوسط"
            return "توافق ضعيف"
        return str(getattr(record, field_name))
