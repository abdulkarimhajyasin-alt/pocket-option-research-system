"""Risk validation skeleton for research signals."""

from loguru import logger

from app.signals.signal import TradeSignal


class RiskEngine:
    """Validates trade signals before simulated execution."""

    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence

    def validate_signal(self, signal: TradeSignal) -> bool:
        """Validate a signal against placeholder Phase 1 risk rules."""
        if not signal.symbol.strip():
            logger.warning("Risk rejected signal: missing symbol")
            return False

        if not 0.0 <= signal.confidence <= 1.0:
            logger.warning("Risk rejected signal: confidence outside 0..1")
            return False

        if signal.confidence < self.min_confidence:
            logger.warning(
                "Risk rejected signal: confidence {} below minimum {}",
                signal.confidence,
                self.min_confidence,
            )
            return False

        logger.info("Risk accepted signal for {}", signal.symbol)
        return True
