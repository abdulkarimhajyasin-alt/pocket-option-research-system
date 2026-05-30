"""Post-trade intelligence for research lifecycle simulation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.trade_lifecycle.models import FailureAnalysisReport, OutcomeEvaluation
from app.trade_lifecycle.models import PostTradeInsights, SuccessAnalysisReport


class PostTradeIntelligenceEngine:
    """Explain why a simulated research lifecycle succeeded or failed."""

    def analyze(
        self,
        decision: dict[str, Any],
        outcome: OutcomeEvaluation,
    ) -> PostTradeInsights:
        factors = self._factors(decision)
        ordered = sorted(factors, key=lambda item: item[1], reverse=True)
        strongest = [name for name, score in ordered if score >= 65][:4]
        weakest = [name for name, score in ordered if score < 55][:4]
        success = []
        failure = []
        if outcome.outcome == "WIN":
            success.append("توافق العوامل البحثية كان داعما")
            success.extend(strongest[:3])
        elif outcome.outcome == "LOSS":
            failure.append("ضعف واضح في بعض عوامل الجودة")
            failure.extend(weakest[:3])
        elif outcome.outcome == "BREAKEVEN":
            success.append("توازن جزئي بين عوامل الجودة")
            failure.append("لم تظهر أفضلية بحثية واضحة")
        else:
            failure.append("البيانات غير كافية للحسم")
        return PostTradeInsights(
            success_reasons=success,
            failure_reasons=failure,
            strongest_factors=strongest,
            weakest_factors=weakest,
            recurring_patterns=self._patterns(decision, strongest, weakest),
        )

    def _factors(self, decision: dict[str, Any]) -> list[tuple[str, float]]:
        confluence = decision.get("confluence", {})
        factors = confluence.get("factors", []) if isinstance(confluence, dict) else []
        rows = []
        for factor in factors:
            if isinstance(factor, dict):
                rows.append((str(factor.get("name")), self._float(factor.get("score"))))
        return rows

    def _patterns(
        self,
        decision: dict[str, Any],
        strongest: list[str],
        weakest: list[str],
    ) -> list[str]:
        patterns = []
        if strongest:
            patterns.append(f"العامل الأقوى: {strongest[0]}")
        if weakest:
            patterns.append(f"العامل الأضعف: {weakest[0]}")
        readiness = str(decision.get("readiness", ""))
        if readiness:
            patterns.append(readiness)
        return patterns[:4]

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


class FailureAnalysisEngine:
    """Track recurring failure causes for simulated research lifecycles."""

    def analyze(
        self,
        decision: dict[str, Any],
        outcome: OutcomeEvaluation,
    ) -> FailureAnalysisReport:
        rejection = list(decision.get("rejection_reasons", []) or [])
        risk = list(decision.get("risk_factors", []) or [])
        factors = self._factor_map(decision)
        return FailureAnalysisReport(
            rejection_reasons=rejection[:4],
            weak_confirmations=self._weak_factor(factors, "عامل الأطر الزمنية"),
            weak_confluence=risk[:4] if outcome.outcome in {"LOSS", "UNRESOLVED"} else [],
            timeframe_conflicts=[
                item for item in risk if "تعارض" in str(item) or "الأطر" in str(item)
            ][:4],
            liquidity_issues=self._weak_factor(factors, "عامل السيولة"),
            session_issues=self._weak_factor(factors, "عامل الجلسة"),
        )

    def _factor_map(self, decision: dict[str, Any]) -> dict[str, float]:
        confluence = decision.get("confluence", {})
        factors = confluence.get("factors", []) if isinstance(confluence, dict) else []
        return {
            str(factor.get("name")): self._float(factor.get("score"))
            for factor in factors
            if isinstance(factor, dict)
        }

    def _weak_factor(self, factors: dict[str, float], name: str) -> list[str]:
        score = factors.get(name, 0.0)
        return [f"{name} منخفض"] if score < 55 else []

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


class SuccessAnalysisEngine:
    """Track strongest factors for successful simulated research lifecycles."""

    def analyze(self, decision: dict[str, Any]) -> SuccessAnalysisReport:
        factors = self._factor_rows(decision)
        strong = [name for name, score in factors if score >= 65]
        return SuccessAnalysisReport(
            strongest_confluence_factors=strong[:4],
            strongest_timeframe_alignment=[
                name for name, score in factors if name == "عامل الأطر الزمنية" and score >= 65
            ],
            strongest_session_alignment=[
                name for name, score in factors if name == "عامل الجلسة" and score >= 65
            ],
            strongest_liquidity_conditions=[
                name for name, score in factors if name == "عامل السيولة" and score >= 65
            ],
        )

    def aggregate_success(self, records: list[Any]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for record in records:
            for item in record.success_analysis.strongest_confluence_factors:
                counter[item] += 1
        return dict(counter)

    def _factor_rows(self, decision: dict[str, Any]) -> list[tuple[str, float]]:
        confluence = decision.get("confluence", {})
        factors = confluence.get("factors", []) if isinstance(confluence, dict) else []
        return [
            (str(factor.get("name")), self._float(factor.get("score")))
            for factor in factors
            if isinstance(factor, dict)
        ]

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
