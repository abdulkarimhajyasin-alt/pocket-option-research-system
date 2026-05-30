"""Session scoring for opportunity qualification."""

from __future__ import annotations

from app.opportunity_engine.models import ScoreBreakdown


class SessionScoreEngine:
    """Score Asian, London, New York, and overlap session quality."""

    def score(self, signal: dict) -> ScoreBreakdown:
        session = signal.get("session", {}) or {}
        name = str(session.get("session_name", "غير متاح"))
        quality = float(session.get("quality_score", 0.0) or 0.0)
        activity = float(session.get("activity_score", 0.0) or 0.0)
        score = round(quality * 0.6 + activity * 0.4, 2)
        strengths = [name] if score >= 70 else []
        weaknesses = [] if score >= 70 else ["جودة الجلسة محدودة"]
        return ScoreBreakdown(
            score=score,
            explanation=f"تقييم الجلسة: {name}",
            strengths=strengths,
            weaknesses=weaknesses,
        )
