"""Scoring logic for final research platform certification."""

from __future__ import annotations

from app.platform_certification.schemas import CERTIFICATION_STATES


class PlatformCertificationScoringEngine:
    """Score certification domains and final research maturity."""

    def score_domain(self, available: int, expected: int, penalty: int = 0) -> float:
        if expected <= 0:
            return 0.0
        score = (available / expected) * 100.0
        return round(max(0.0, min(100.0, score - penalty)), 2)

    def domain_status(self, score: float) -> str:
        if score >= 90:
            return "ممتاز"
        if score >= 75:
            return "جيد"
        if score >= 60:
            return "مقبول"
        if score >= 40:
            return "يحتاج تحسين"
        return "غير مؤهل"

    def platform_score(self, domain_scores: list[float]) -> float:
        if not domain_scores:
            return 0.0
        return round(sum(domain_scores) / len(domain_scores), 2)

    def maturity_level(self, score: float) -> str:
        if score >= 90:
            return "نضج بحثي متقدم"
        if score >= 75:
            return "نضج بحثي جيد"
        if score >= 60:
            return "نضج بحثي مقبول"
        return "نضج بحثي يحتاج تحسين"

    def certification_state(self, score: float, high_risk_count: int) -> str:
        if high_risk_count > 0 or score < 60:
            return CERTIFICATION_STATES[0]
        if score < 85:
            return CERTIFICATION_STATES[1]
        return CERTIFICATION_STATES[2]
