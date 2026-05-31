"""Normalize passive observation layer outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.observation_intelligence.models import NormalizationResult
from app.observation_intelligence.models import UnifiedObservation
from app.observation_intelligence.scoring import average
from app.observation_intelligence.scoring import clamp


class ObservationNormalizer:
    """Convert existing passive observation outputs into unified observations."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def normalize(self) -> tuple[tuple[UnifiedObservation, ...], NormalizationResult]:
        candidates = (
            self._from_snapshot_import(),
            self._from_browser_observation(),
            self._from_external_observation(),
            self._from_broker_readiness(),
            self._from_observation_sandbox(),
        )
        observations = tuple(item for item in candidates if item is not None)
        score = 100.0 if len(observations) == len(candidates) else len(observations) * 20.0
        return (
            observations,
            NormalizationResult(
                score=clamp(score),
                source_count=len(candidates),
                normalized_count=len(observations),
            ),
        )

    def _from_snapshot_import(self) -> UnifiedObservation | None:
        payload = self._read_json("reports/snapshot_import/import_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        parse = latest.get("parse", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return UnifiedObservation(
            "snapshot_import",
            "snapshot_import",
            "استيراد اللقطات",
            str(summary.get("last_import") or latest.get("timestamp") or ""),
            self._float(parse.get("assets")),
            self._float(parse.get("payouts")),
            self._float(parse.get("sessions")),
            self._float(parse.get("symbols")),
            self._float(parse.get("market_information")),
            self._float(summary.get("quality_score")),
            self._float(summary.get("quality_score")),
            self._float(summary.get("workflow_score")),
        )

    def _from_browser_observation(self) -> UnifiedObservation | None:
        payload = self._read_json("reports/browser_observation/observation_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        parse = latest.get("parse", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return UnifiedObservation(
            "browser_observation",
            "browser_observation",
            "مراقبة المتصفح",
            str(latest.get("timestamp") or ""),
            self._float(parse.get("visible_assets")),
            self._float(parse.get("visible_payouts")),
            self._float(parse.get("visible_sessions")),
            self._float(parse.get("visible_symbols")),
            self._float(parse.get("visible_market_data")),
            self._float(summary.get("visibility_score")),
            self._float(summary.get("validation_score")),
            self._float(summary.get("adapter_score")),
        )

    def _from_external_observation(self) -> UnifiedObservation | None:
        payload = self._read_json("reports/external_observation/sandbox_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            return None
        score = self._float(summary.get("sandbox_score"))
        return UnifiedObservation(
            "external_observation",
            "external_observation",
            "المراقبة الخارجية",
            str(latest.get("timestamp") or ""),
            self._float(summary.get("source_count")),
            self._float(summary.get("source_count")),
            self._float(summary.get("source_count")),
            self._float(summary.get("source_count")),
            self._float(summary.get("monitoring_score")),
            self._float(summary.get("monitoring_score")),
            self._float(summary.get("health_score")),
            score,
        )

    def _from_broker_readiness(self) -> UnifiedObservation | None:
        payload = self._read_json("reports/broker_readiness/readiness_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        capability = latest.get("capability", {}) if isinstance(latest, dict) else {}
        if not summary:
            return None
        return UnifiedObservation(
            "broker_readiness",
            "broker_readiness",
            "جاهزية المراقبة",
            str(latest.get("timestamp") or ""),
            self._float(capability.get("asset_visibility")),
            self._float(capability.get("payout_visibility")),
            self._float(capability.get("session_visibility")),
            self._float(capability.get("signal_visibility")),
            self._float(capability.get("market_visibility")),
            self._float(summary.get("coverage_level")),
            self._float(summary.get("capability_score")),
            self._float(summary.get("readiness_score")),
        )

    def _from_observation_sandbox(self) -> UnifiedObservation | None:
        payload = self._read_json("reports/observation/observation_summary.json")
        if not isinstance(payload, dict):
            return None
        score = average(
            [
                self._float(payload.get("observation_score")),
                self._float(payload.get("quality_score")),
                self._float(payload.get("coverage_score")),
            ]
        )
        if score == 0:
            return None
        return UnifiedObservation(
            "observation_sandbox",
            "observation_sandbox",
            "صندوق المراقبة",
            str(payload.get("timestamp") or ""),
            self._float(payload.get("assets") or payload.get("asset_count")),
            self._float(payload.get("payouts") or payload.get("payout_count")),
            self._float(payload.get("sessions") or payload.get("session_count")),
            self._float(payload.get("symbols") or payload.get("symbol_count")),
            self._float(payload.get("market_data") or payload.get("market_score")),
            score,
            score,
            score,
        )

    def _read_json(self, relative: str) -> Any:
        path = self.project_root / relative
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0
