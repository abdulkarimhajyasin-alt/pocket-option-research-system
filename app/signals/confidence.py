"""Signal confidence scoring utilities."""

from dataclasses import dataclass

from loguru import logger


@dataclass(frozen=True)
class WeightedScore:
    """One named weighted confidence component."""

    name: str
    score: float
    weight: float = 1.0


class ConfidenceScorer:
    """Normalizes and thresholds signal confidence scores."""

    def __init__(self, threshold: float = 0.60) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0 and 1")
        self.threshold = threshold

    def normalize(self, value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        """Normalize a value into the 0..1 range."""
        if maximum <= minimum:
            raise ValueError("maximum must be greater than minimum")
        normalized = (value - minimum) / (maximum - minimum)
        return min(1.0, max(0.0, normalized))

    def weighted(self, scores: list[WeightedScore]) -> float:
        """Calculate a weighted normalized confidence score."""
        if not scores:
            return 0.0

        total_weight = sum(score.weight for score in scores)
        if total_weight <= 0:
            raise ValueError("Total confidence weight must be positive")

        confidence = sum(self.normalize(item.score) * item.weight for item in scores) / total_weight
        confidence = round(confidence, 4)
        logger.info("Calculated confidence {} from {}", confidence, scores)
        return confidence

    def passes(self, confidence: float) -> bool:
        """Return True if confidence is at or above threshold."""
        passed = confidence >= self.threshold
        if not passed:
            logger.info(
                "Signal confidence rejected: confidence={} threshold={}",
                confidence,
                self.threshold,
            )
        return passed
