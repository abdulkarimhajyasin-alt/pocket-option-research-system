"""Adaptive learning engine."""

from __future__ import annotations

from collections import defaultdict

from app.pattern_memory.models import DiscoveredPattern, LearningInsight, PatternMemoryRecord


class AdaptiveLearningEngine:
    """Identify improving, degrading, stable, and emerging patterns."""

    def learn(
        self,
        records: tuple[PatternMemoryRecord, ...],
        patterns: tuple[DiscoveredPattern, ...],
    ) -> tuple[LearningInsight, ...]:
        by_key = defaultdict(list)
        for record in records:
            by_key[" | ".join(record.signature)].append(record)
        insights = []
        for pattern in patterns:
            rows = by_key.get(pattern.pattern_key, [])
            category = self._category(rows)
            insights.append(
                LearningInsight(
                    pattern.pattern_key,
                    category,
                    self._title(category),
                    self._detail(category, pattern),
                    self._suggestion(category),
                    self._opportunity(category),
                )
            )
        return tuple(insights)

    def _category(self, rows: list[PatternMemoryRecord]) -> str:
        if len(rows) < 3:
            return "ناشئ"
        midpoint = len(rows) // 2
        early = self._success_ratio(rows[:midpoint])
        late = self._success_ratio(rows[midpoint:])
        if late - early >= 15:
            return "يتحسن"
        if early - late >= 15:
            return "يتراجع"
        return "مستقر"

    def _success_ratio(self, rows: list[PatternMemoryRecord]) -> float:
        if not rows:
            return 0.0
        return sum(1 for row in rows if row.outcome_bucket == "successful") / len(rows) * 100

    def _title(self, category: str) -> str:
        return {
            "يتحسن": "نمط يتحسن",
            "يتراجع": "نمط يتراجع",
            "مستقر": "نمط مستقر",
            "ناشئ": "نمط ناشئ",
        }.get(category, "رؤية تعلم")

    def _detail(self, category: str, pattern: DiscoveredPattern) -> str:
        return (
            f"{pattern.description} مصنف كـ {category} بعد "
            f"{pattern.occurrences} تكرارات بحثية."
        )

    def _suggestion(self, category: str) -> str:
        return {
            "يتحسن": "زيادة وزن هذا النمط في المقارنة البحثية فقط.",
            "يتراجع": "مراجعة شروط النمط قبل اعتباره عالي الجودة.",
            "مستقر": "الاحتفاظ بالنمط كمرجع تاريخي مستقر.",
            "ناشئ": "جمع بيانات إضافية قبل إصدار حكم بحثي.",
        }.get(category, "متابعة النمط بحثيا.")

    def _opportunity(self, category: str) -> str:
        return {
            "يتحسن": "فرصة لتحسين ذاكرة الأنماط عالية الجودة.",
            "يتراجع": "فرصة لاكتشاف أسباب ضعف التكرارية.",
            "مستقر": "فرصة لتثبيت معايير المقارنة.",
            "ناشئ": "فرصة لتوسيع العينة التاريخية.",
        }.get(category, "فرصة تحسين بحثية.")
