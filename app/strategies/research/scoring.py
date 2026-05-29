"""Evidence scoring for explainable research strategies."""

from dataclasses import dataclass, field

from app.signals.signal import SignalDirection
from app.strategies.research.models import EvidenceDirection, SignalEvidence


@dataclass(frozen=True)
class EvidenceScore:
    """Directional evidence score output."""

    bullish_score: float
    bearish_score: float
    confidence: float
    direction: SignalDirection | None
    evidence_count: int
    passed_minimum_evidence: bool

    def to_dict(self) -> dict[str, float | int | bool | str | None]:
        """Return serializable score details."""
        return {
            "bullish_score": round(self.bullish_score, 4),
            "bearish_score": round(self.bearish_score, 4),
            "confidence": round(self.confidence, 4),
            "direction": self.direction.value if self.direction else None,
            "evidence_count": self.evidence_count,
            "passed_minimum_evidence": self.passed_minimum_evidence,
        }


@dataclass(frozen=True)
class EvidenceScoringConfig:
    """Configurable evidence scoring settings."""

    weights: dict[str, float] = field(default_factory=dict)
    minimum_evidence: int = 3
    confidence_threshold: float = 0.60


class EvidenceScorer:
    """Score weighted bullish and bearish evidence independently."""

    DEFAULT_WEIGHTS = {
        "trend_alignment": 1.0,
        "fvg_presence": 1.0,
        "cisd_displacement": 1.2,
        "liquidity_sweep": 1.1,
        "session_allowed": 0.7,
        "volatility_acceptable": 0.8,
        "candle_confirmation": 1.0,
    }

    def __init__(self, config: EvidenceScoringConfig | None = None) -> None:
        self.config = config or EvidenceScoringConfig()
        self.weights = {**self.DEFAULT_WEIGHTS, **self.config.weights}

    def score(self, evidence: tuple[SignalEvidence, ...]) -> EvidenceScore:
        """Return normalized confidence and dominant direction."""
        directional = [item for item in evidence if item.direction != EvidenceDirection.NEUTRAL]
        passed = len(directional) >= self.config.minimum_evidence
        bullish = self._directional_score(evidence, EvidenceDirection.BULLISH)
        bearish = self._directional_score(evidence, EvidenceDirection.BEARISH)
        total_weight = self._total_weight(evidence)
        bullish_norm = bullish / total_weight if total_weight else 0.0
        bearish_norm = bearish / total_weight if total_weight else 0.0
        direction = None
        confidence = max(bullish_norm, bearish_norm)
        if passed and confidence >= self.config.confidence_threshold:
            direction = (
                SignalDirection.CALL if bullish_norm >= bearish_norm else SignalDirection.PUT
            )
        return EvidenceScore(
            bullish_score=bullish_norm,
            bearish_score=bearish_norm,
            confidence=confidence if passed else 0.0,
            direction=direction,
            evidence_count=len(directional),
            passed_minimum_evidence=passed,
        )

    def _directional_score(
        self,
        evidence: tuple[SignalEvidence, ...],
        direction: EvidenceDirection,
    ) -> float:
        score = 0.0
        for item in evidence:
            if item.direction != direction:
                continue
            score += item.strength * self.weights.get(item.name, item.weight)
        return score

    def _total_weight(self, evidence: tuple[SignalEvidence, ...]) -> float:
        total = 0.0
        for item in evidence:
            if item.direction == EvidenceDirection.NEUTRAL:
                continue
            total += self.weights.get(item.name, item.weight)
        return total
