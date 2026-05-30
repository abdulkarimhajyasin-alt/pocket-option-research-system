"""Outcome evaluation for research lifecycle simulation."""

from __future__ import annotations

from app.trade_lifecycle.models import EntryAnalysis, ExpiryAnalysis
from app.trade_lifecycle.models import OutcomeEvaluation


class OutcomeEvaluationEngine:
    """Generate deterministic research outcomes from quality metrics."""

    def evaluate(
        self,
        confluence_score: float,
        qualification_score: float,
        entry: EntryAnalysis,
        expiry: ExpiryAnalysis,
    ) -> OutcomeEvaluation:
        aggregate = round(
            confluence_score * 0.35
            + qualification_score * 0.20
            + entry.readiness_score * 0.25
            + expiry.expiry_quality * 0.20,
            2,
        )
        if aggregate >= 70:
            outcome = "WIN"
            reason = "اكتملت عوامل الجودة البحثية بدرجة مرتفعة"
        elif aggregate >= 58:
            outcome = "BREAKEVEN"
            reason = "العوامل البحثية متوازنة دون تفوق واضح"
        elif aggregate >= 35:
            outcome = "LOSS"
            reason = "ضعفت بعض عوامل التأكيد والجودة"
        else:
            outcome = "UNRESOLVED"
            reason = "البيانات البحثية غير كافية للحسم"
        return OutcomeEvaluation(
            outcome=outcome,
            evaluation_reason=reason,
            confidence_accuracy=self._accuracy(entry.readiness_score),
            confluence_accuracy=self._accuracy(confluence_score),
            qualification_accuracy=self._accuracy(qualification_score),
        )

    def _accuracy(self, score: float) -> float:
        return round(max(0.0, min(100.0, score)), 2)
