"""Research health and readiness monitor."""

from __future__ import annotations

from app.research_ops.models import ResearchHealth


class ResearchHealthEngine:
    """Generate a research health score from readiness and stability."""

    def evaluate(
        self,
        readiness_score: float,
        stability_score: float,
        alerts: int,
    ) -> ResearchHealth:
        score = max(
            0.0,
            min(100.0, readiness_score * 0.55 + stability_score * 0.35 - alerts * 2),
        )
        score = round(score, 2)
        return ResearchHealth(
            score=score,
            classification=self._classification(score),
            explanation="مؤشر جودة بحثية عام وليس توصية تداول أو تنفيذ.",
        )

    def _classification(self, score: float) -> str:
        if score >= 95:
            return "ممتاز"
        if score >= 85:
            return "جيد جدا"
        if score >= 70:
            return "جيد"
        if score >= 50:
            return "متوسط"
        return "ضعيف"
