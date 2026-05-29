"""Research-grade CISD/FVG strategy candidate."""

from __future__ import annotations

from typing import Any

from loguru import logger

from app.signals.signal import TradeSignal
from app.strategies.base_strategy import BaseStrategy, StrategyMetadata, StrategyParameters
from app.strategies.price_action.cisd import detect_cisd_displacement
from app.strategies.price_action.fvg import latest_fvg
from app.strategies.price_action.liquidity import detect_liquidity_sweep
from app.strategies.price_action.structure import (
    StructureDirection,
    market_structure_direction,
)
from app.strategies.research.context import MarketContextBuilder
from app.strategies.research.filters import FilterResult, ResearchFilters
from app.strategies.research.models import (
    EvidenceDirection,
    SignalEvidence,
    StrategyDecision,
    StrategyRejection,
)
from app.strategies.research.reporting import StrategyResearchReporter
from app.strategies.research.scoring import EvidenceScorer, EvidenceScoringConfig


class ResearchCisdFvgStrategy(BaseStrategy):
    """Explainable research candidate combining structure, sweeps, CISD, and FVG."""

    metadata = StrategyMetadata(
        name="research_cisd_fvg_strategy",
        description="Research candidate using CISD-like displacement and fair value gaps.",
        version="0.1.0",
        required_indicators=("atr",),
        supports_multi_timeframe=True,
    )

    def __init__(self, parameters: StrategyParameters | None = None) -> None:
        super().__init__(parameters=parameters)
        values = self.parameters.values
        self.minimum_history = int(values.get("minimum_history", 20))
        self.structure_lookback = int(values.get("structure_lookback", 2))
        self.atr_minimum = self._optional_float(values.get("atr_minimum"))
        self.atr_maximum = self._optional_float(values.get("atr_maximum"))
        self.minimum_body_ratio = float(values.get("minimum_body_ratio", 0.45))
        self.minimum_range = float(values.get("minimum_range", 0.00005))
        self.maximum_wick_ratio = float(values.get("maximum_wick_ratio", 0.75))
        self.fvg_minimum_size = float(values.get("fvg_minimum_size", 0.00003))
        self.cisd_lookback = int(values.get("cisd_lookback", 5))
        self.cisd_body_ratio = float(values.get("cisd_body_ratio", 0.55))
        self.cisd_range_multiple = float(values.get("cisd_range_multiple", 1.15))
        self.sweep_lookback = int(values.get("sweep_lookback", 5))
        self.sweep_tolerance = float(values.get("sweep_tolerance", 0.0))
        self.allowed_sessions = tuple(
            str(item).lower()
            for item in values.get(
                "sessions",
                self.parameters.session_restriction.sessions,
            )
        )
        self.context_builder = MarketContextBuilder()
        self.filters = ResearchFilters(atr_period=int(values.get("atr_period", 14)))
        self.scorer = EvidenceScorer(
            EvidenceScoringConfig(
                weights=dict(values.get("scoring_weights", {})),
                minimum_evidence=int(values.get("minimum_evidence", 3)),
                confidence_threshold=self.parameters.confidence_threshold,
            )
        )
        self.reporter = StrategyResearchReporter()
        self.decisions: list[StrategyDecision] = []

    def validate_environment(self) -> bool:
        """Validate research strategy settings."""
        super().validate_environment()
        if self.minimum_history < 5:
            raise ValueError("minimum_history must be at least 5")
        if self.minimum_body_ratio < 0 or self.maximum_wick_ratio > 1:
            raise ValueError("candle ratio thresholds must be between 0 and 1")
        logger.bind(component="strategy_research").info(
            "{} initialized parameters={}",
            self.name,
            self.parameters.values,
        )
        return True

    def generate_signal(self, market_data: Any) -> TradeSignal | None:
        """Generate an explainable research signal or a structured rejection."""
        context = self.context_builder.from_market_data(market_data)
        candles = context.market.candles
        current = context.market.latest_candle
        evidence: list[SignalEvidence] = []
        rejections: list[StrategyRejection] = []

        if not self._is_symbol_timeframe_allowed(current.symbol, current.timeframe):
            rejections.append(StrategyRejection("symbol_or_timeframe_not_enabled"))
            return self._reject(context, evidence, rejections)
        if len(candles) < self.minimum_history:
            rejections.append(StrategyRejection("insufficient_history", str(len(candles))))
            return self._reject(context, evidence, rejections)

        filter_results = self._run_filters(context.market.session, candles)
        for result in filter_results:
            if result.passed:
                evidence.extend(self._evidence_from_filter(result))
            else:
                rejections.append(StrategyRejection(result.reason, str(result.value)))
        if rejections:
            return self._reject(context, evidence, rejections)

        structure = market_structure_direction(candles, self.structure_lookback)
        if structure == StructureDirection.BULLISH:
            evidence.append(self._evidence("trend_alignment", EvidenceDirection.BULLISH, 0.75))
        elif structure == StructureDirection.BEARISH:
            evidence.append(self._evidence("trend_alignment", EvidenceDirection.BEARISH, 0.75))

        sweep = detect_liquidity_sweep(candles, self.sweep_lookback, self.sweep_tolerance)
        if sweep:
            evidence.append(
                self._evidence(
                    "liquidity_sweep",
                    sweep.direction,
                    max(0.45, sweep.strength),
                    {"level": sweep.swept_level},
                )
            )

        displacement = detect_cisd_displacement(
            candles,
            self.cisd_lookback,
            self.cisd_body_ratio,
            self.cisd_range_multiple,
        )
        if displacement:
            evidence.append(
                self._evidence(
                    "cisd_displacement",
                    displacement.direction,
                    min(1.0, displacement.body_ratio * displacement.range_multiple),
                    {
                        "body_ratio": round(displacement.body_ratio, 4),
                        "range_multiple": round(displacement.range_multiple, 4),
                    },
                )
            )

        gap = latest_fvg(candles, self.fvg_minimum_size)
        if gap:
            evidence.append(
                self._evidence(
                    "fvg_presence",
                    gap.direction,
                    min(1.0, gap.size / max(current.close * 0.001, 0.00001)),
                    {"lower": gap.lower, "upper": gap.upper},
                )
            )

        if current.close > current.open:
            evidence.append(self._evidence("candle_confirmation", EvidenceDirection.BULLISH, 0.7))
        elif current.close < current.open:
            evidence.append(self._evidence("candle_confirmation", EvidenceDirection.BEARISH, 0.7))

        score = self.scorer.score(tuple(evidence))
        if score.direction is None:
            rejections.append(
                StrategyRejection(
                    "score_below_threshold",
                    f"confidence={score.confidence:.4f}",
                )
            )
            return self._reject(
                context,
                evidence,
                rejections,
                score.bullish_score,
                score.bearish_score,
            )

        decision = StrategyDecision(
            strategy_name=self.name,
            symbol=current.symbol,
            timeframe=current.timeframe,
            timestamp=current.timestamp,
            direction=score.direction,
            confidence=score.confidence,
            generated_signal=True,
            evidence=tuple(evidence),
            rejections=(),
            bullish_score=score.bullish_score,
            bearish_score=score.bearish_score,
        )
        self.decisions.append(decision)
        logger.bind(component="strategy_research").info(
            "Signal generated {}",
            self.reporter.decision_summary(decision),
        )
        return TradeSignal(
            symbol=current.symbol,
            timeframe=current.timeframe,
            direction=score.direction,
            confidence=round(score.confidence, 4),
            timestamp=current.timestamp,
            strategy_name=self.name,
        )

    def _run_filters(self, session: str, candles: tuple[Any, ...]) -> tuple[FilterResult, ...]:
        current = candles[-1]
        return (
            self.filters.session_allowed(session, self.allowed_sessions),
            self.filters.atr_between(candles, self.atr_minimum, self.atr_maximum),
            self.filters.candle_body_strength(current, self.minimum_body_ratio),
            self.filters.avoid_low_range(current, self.minimum_range),
            self.filters.avoid_excessive_wick(current, self.maximum_wick_ratio),
        )

    def _evidence_from_filter(self, result: FilterResult) -> tuple[SignalEvidence, ...]:
        if result.name == "session_allowed":
            return (
                self._evidence(
                    "session_allowed",
                    EvidenceDirection.NEUTRAL,
                    1.0,
                    {"session": str(result.value)},
                ),
            )
        if result.name == "atr_between":
            return (self._evidence("volatility_acceptable", EvidenceDirection.NEUTRAL, 1.0),)
        return ()

    def _is_symbol_timeframe_allowed(self, symbol: str, timeframe: str) -> bool:
        return (not self.parameters.symbols or symbol in self.parameters.symbols) and (
            not self.parameters.timeframes or timeframe in self.parameters.timeframes
        )

    def _reject(
        self,
        context: Any,
        evidence: list[SignalEvidence],
        rejections: list[StrategyRejection],
        bullish_score: float = 0.0,
        bearish_score: float = 0.0,
    ) -> None:
        current = context.market.latest_candle
        decision = StrategyDecision(
            strategy_name=self.name,
            symbol=current.symbol,
            timeframe=current.timeframe,
            timestamp=current.timestamp,
            direction=None,
            confidence=0.0,
            generated_signal=False,
            evidence=tuple(evidence),
            rejections=tuple(rejections),
            bullish_score=bullish_score,
            bearish_score=bearish_score,
        )
        self.decisions.append(decision)
        logger.bind(component="strategy_research").info(
            "Signal rejected {}",
            self.reporter.decision_summary(decision),
        )
        return None

    def _evidence(
        self,
        name: str,
        direction: EvidenceDirection,
        strength: float,
        metadata: dict[str, object] | None = None,
    ) -> SignalEvidence:
        return SignalEvidence(
            name=name,
            direction=direction,
            strength=max(0.0, min(1.0, strength)),
            description=name.replace("_", " "),
            metadata=metadata or {},
        )

    def _optional_float(self, value: object) -> float | None:
        return None if value in (None, "") else float(value)
