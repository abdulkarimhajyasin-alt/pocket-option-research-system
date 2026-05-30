"""Weighted confidence model for signal intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.signal_intelligence.models import (
    CISDState,
    FVGState,
    IFVGState,
    LiquidityState,
    SessionState,
    SignalConfidence,
    StructureState,
)


@dataclass(frozen=True)
class ConfidenceWeights:
    market_structure: float = 20.0
    cisd: float = 20.0
    fvg: float = 20.0
    ifvg: float = 10.0
    liquidity: float = 15.0
    session_quality: float = 15.0
    extra: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        payload = {
            "market_structure": self.market_structure,
            "cisd": self.cisd,
            "fvg": self.fvg,
            "ifvg": self.ifvg,
            "liquidity": self.liquidity,
            "session_quality": self.session_quality,
        }
        payload.update(self.extra)
        return payload


class ConfidenceEngine:
    """Compute 0-100 confidence from weighted research components."""

    def __init__(self, weights: ConfidenceWeights | None = None) -> None:
        self.weights = weights or ConfidenceWeights()

    def score(
        self,
        structure: StructureState,
        cisd: CISDState,
        fvg: FVGState | None,
        ifvg: IFVGState | None,
        liquidity: LiquidityState,
        session: SessionState,
    ) -> SignalConfidence:
        weights = self.weights.to_dict()
        contributions = {
            "market_structure": weights["market_structure"] * structure.confidence_contribution,
            "cisd": weights["cisd"] * cisd.confidence_contribution,
            "fvg": weights["fvg"] * (fvg.freshness_score if fvg else 0.0),
            "ifvg": weights["ifvg"] * (ifvg.confidence_contribution if ifvg else 0.0),
            "liquidity": weights["liquidity"] * liquidity.confidence_contribution,
            "session_quality": weights["session_quality"] * (session.quality_score / 100),
        }
        total = round(max(0.0, min(100.0, sum(contributions.values()))), 2)
        return SignalConfidence(
            score=total,
            classification=self._classification(total),
            weights=weights,
            contributions={key: round(value, 4) for key, value in contributions.items()},
        )

    def _classification(self, score: float) -> str:
        if score < 40:
            return "ضعيفة"
        if score < 60:
            return "متوسطة"
        if score < 80:
            return "قوية"
        return "عالية الاقتناع"
