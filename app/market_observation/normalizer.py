"""Normalize passive local outputs into canonical market observations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.market_observation.models import MarketObservationRecord
from app.market_observation.scoring import average
from app.market_observation.scoring import clamp


class MarketObservationNormalizer:
    """Read passive observation artifacts without broker or browser control."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def normalize(self) -> tuple[MarketObservationRecord, ...]:
        candidates = (
            self._from_market_data(),
            self._from_observation_layer(),
            self._from_observation_intelligence(),
            self._from_browser_observation(),
            self._from_external_observation(),
            self._from_snapshot_import(),
            self._from_broker_readiness(),
        )
        return tuple(item for item in candidates if item is not None)

    def _from_market_data(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/market_data/market_summary.json")
        if not payload:
            return None
        return self._record(
            "market_data",
            "market_data",
            "بيانات السوق",
            str(payload.get("timestamp") or ""),
            payload.get("asset_count"),
            payload.get("active_assets"),
            payload.get("active_sessions"),
            payload.get("asset_count"),
            payload.get("readiness_score"),
            payload.get("feed_quality_score"),
            payload.get("readiness_score"),
            payload.get("readiness_score"),
            100.0,
            payload,
        )

    def _from_observation_layer(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/observation/observation_summary.json")
        if not payload:
            return None
        score = average(
            [
                self._float(payload.get("observation_score")),
                self._float(payload.get("quality_score")),
                self._float(payload.get("coverage_score")),
            ]
        )
        return self._record(
            "observation_layer",
            "observation_layer",
            "مراقبة السوق",
            str(payload.get("timestamp") or ""),
            payload.get("active_assets") or payload.get("asset_count"),
            payload.get("payout_count") or payload.get("payouts"),
            payload.get("session_count") or payload.get("sessions"),
            payload.get("symbol_count") or payload.get("active_assets"),
            score,
            score,
            score,
            score,
            95.0,
            payload,
        )

    def _from_observation_intelligence(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/observation_intelligence/observation_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        aggregate = latest.get("aggregation", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return self._record(
            "observation_intelligence",
            "observation_intelligence",
            "ذكاء المراقبة",
            str(latest.get("timestamp") or ""),
            summary.get("observation_count"),
            summary.get("observation_count"),
            summary.get("observation_count"),
            summary.get("observation_count"),
            aggregate.get("score") or summary.get("readiness_score"),
            aggregate.get("visibility") or summary.get("coverage_score"),
            summary.get("quality_score"),
            summary.get("confidence_score"),
            100.0,
            payload,
        )

    def _from_browser_observation(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/browser_observation/observation_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        parse = latest.get("parse", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return self._record(
            "browser_observation",
            "browser_observation",
            "مراقبة المتصفح",
            str(latest.get("timestamp") or ""),
            parse.get("visible_assets"),
            parse.get("visible_payouts"),
            parse.get("visible_sessions"),
            parse.get("visible_symbols"),
            parse.get("visible_market_data"),
            summary.get("visibility_score"),
            summary.get("validation_score"),
            summary.get("adapter_score"),
            90.0,
            payload,
        )

    def _from_external_observation(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/external_observation/sandbox_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            return None
        return self._record(
            "external_observation",
            "external_observation",
            "المراقبة الخارجية",
            str(latest.get("timestamp") or ""),
            summary.get("source_count"),
            summary.get("source_count"),
            summary.get("source_count"),
            summary.get("source_count"),
            summary.get("monitoring_score"),
            summary.get("monitoring_score"),
            summary.get("health_score"),
            summary.get("sandbox_score"),
            85.0,
            payload,
        )

    def _from_snapshot_import(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/snapshot_import/import_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        parse = latest.get("parse", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return self._record(
            "snapshot_import",
            "snapshot_import",
            "استيراد اللقطات",
            str(summary.get("last_import") or latest.get("timestamp") or ""),
            parse.get("assets"),
            parse.get("payouts"),
            parse.get("sessions"),
            parse.get("symbols"),
            parse.get("market_information"),
            summary.get("quality_score"),
            summary.get("quality_score"),
            summary.get("workflow_score"),
            80.0,
            payload,
        )

    def _from_broker_readiness(self) -> MarketObservationRecord | None:
        payload = self._read_json("reports/broker_readiness/readiness_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        capability = latest.get("capability", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return self._record(
            "broker_readiness",
            "broker_readiness",
            "جاهزية المراقبة",
            str(latest.get("timestamp") or ""),
            capability.get("asset_visibility"),
            capability.get("payout_visibility"),
            capability.get("session_visibility"),
            capability.get("signal_visibility"),
            capability.get("market_visibility"),
            summary.get("coverage_level"),
            summary.get("capability_score"),
            summary.get("readiness_score"),
            85.0,
            payload,
        )

    def _record(
        self,
        observation_id: str,
        source_type: str,
        source_name: str,
        timestamp: str,
        assets: Any,
        payouts: Any,
        sessions: Any,
        symbols: Any,
        market_data: Any,
        visibility: Any,
        quality: Any,
        confidence: Any,
        freshness: Any,
        payload: dict[str, Any],
    ) -> MarketObservationRecord:
        return MarketObservationRecord(
            observation_id=observation_id,
            source_type=source_type,
            source_name=source_name,
            timestamp=timestamp,
            asset_count=self._float(assets),
            payout_count=self._float(payouts),
            session_count=self._float(sessions),
            symbol_count=self._float(symbols),
            market_data_score=clamp(self._float(market_data)),
            visibility_score=clamp(self._float(visibility)),
            quality_score=clamp(self._float(quality)),
            confidence_score=clamp(self._float(confidence)),
            freshness_score=clamp(self._float(freshness)),
            payload=payload,
        )

    def _read_json(self, relative: str) -> dict[str, Any]:
        path = self.project_root / relative
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0
