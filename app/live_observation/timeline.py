"""Timeline construction for live observation replay."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from typing import Any

from app.live_observation.models import LiveObservation
from app.live_observation.models import TimelineResult
from app.live_observation.scoring import average
from app.live_observation.scoring import clamp


class ObservationTimelineSource:
    """Load passive observation outputs from local report files."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def load(self) -> tuple[LiveObservation, ...]:
        observations: list[LiveObservation] = []
        observations.extend(self._from_market_observation())
        observations.extend(self._from_observation_intelligence())
        item = self._from_snapshot_import()
        if item:
            observations.append(item)
        item = self._from_browser_observation()
        if item:
            observations.append(item)
        item = self._from_external_observation()
        if item:
            observations.append(item)
        return tuple(sorted(observations, key=lambda item: item.timestamp or item.observation_id))

    def _from_market_observation(self) -> list[LiveObservation]:
        payload = self._read_json("reports/market_observation/observation_summary.json")
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        rows = latest.get("observations", []) if isinstance(latest, dict) else []
        return [
            self._observation(
                f"market_observation_{index}",
                row,
                source="market_observation",
                default_timestamp=latest.get("timestamp"),
            )
            for index, row in enumerate(rows, start=1)
            if isinstance(row, dict)
        ]

    def _from_observation_intelligence(self) -> list[LiveObservation]:
        payload = self._read_json("reports/observation_intelligence/observation_summary.json")
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        rows = latest.get("observations", []) if isinstance(latest, dict) else []
        return [
            self._observation(
                f"observation_intelligence_{index}",
                row,
                source="observation_intelligence",
                default_timestamp=latest.get("timestamp"),
            )
            for index, row in enumerate(rows, start=1)
            if isinstance(row, dict)
        ]

    def _from_snapshot_import(self) -> LiveObservation | None:
        payload = self._read_json("reports/snapshot_import/import_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            return None
        return LiveObservation(
            observation_id="snapshot_import",
            timestamp=str(summary.get("last_import") or latest.get("timestamp") or ""),
            source="snapshot_import",
            asset="snapshot",
            session="manual",
            market_state=str(summary.get("workflow_state") or "imported"),
            confidence=self._float(summary.get("workflow_score")),
            quality=self._float(summary.get("quality_score")),
            readiness=self._float(summary.get("validation_score")),
            metadata={"source_payload": summary, "research_only": True},
        )

    def _from_browser_observation(self) -> LiveObservation | None:
        payload = self._read_json("reports/browser_observation/observation_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            return None
        return LiveObservation(
            observation_id="browser_observation",
            timestamp=str(latest.get("timestamp") or ""),
            source="browser_observation",
            asset="browser_snapshot",
            session="passive",
            market_state="observed",
            confidence=self._float(summary.get("adapter_score")),
            quality=self._float(summary.get("validation_score")),
            readiness=self._float(summary.get("visibility_score")),
            metadata={"source_payload": summary, "research_only": True},
        )

    def _from_external_observation(self) -> LiveObservation | None:
        payload = self._read_json("reports/external_observation/sandbox_summary.json")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        if not summary:
            return None
        return LiveObservation(
            observation_id="external_observation",
            timestamp=str(latest.get("timestamp") or ""),
            source="external_observation",
            asset="external_source",
            session="passive",
            market_state="sandboxed",
            confidence=self._float(summary.get("sandbox_score")),
            quality=self._float(summary.get("health_score")),
            readiness=self._float(summary.get("monitoring_score")),
            metadata={"source_payload": summary, "research_only": True},
        )

    def _observation(
        self,
        fallback_id: str,
        row: dict[str, Any],
        *,
        source: str,
        default_timestamp: Any,
    ) -> LiveObservation:
        return LiveObservation(
            observation_id=str(row.get("observation_id") or fallback_id),
            timestamp=str(row.get("timestamp") or default_timestamp or ""),
            source=str(row.get("source_type") or row.get("source") or source),
            asset=str(row.get("asset") or row.get("source_name") or source),
            session=str(row.get("session") or "passive"),
            market_state=str(row.get("market_state") or "observed"),
            confidence=clamp(self._float(row.get("confidence_score") or row.get("confidence"))),
            quality=clamp(self._float(row.get("quality_score") or row.get("quality"))),
            readiness=clamp(self._float(row.get("readiness") or row.get("readiness_score"))),
            metadata={"source_payload": row, "research_only": True},
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


class ObservationTimelineEngine:
    """Generate observation sequence, timeline, progression, and coverage."""

    def build(self, observations: tuple[LiveObservation, ...]) -> TimelineResult:
        base_time = datetime(2026, 1, 1, tzinfo=UTC)
        rows = []
        for index, item in enumerate(observations, start=1):
            timestamp = item.timestamp or (base_time + timedelta(minutes=index)).isoformat()
            rows.append(
                {
                    "sequence": index,
                    "observation_id": item.observation_id,
                    "timestamp": timestamp,
                    "source": item.source,
                    "asset": item.asset,
                    "quality": item.quality,
                    "readiness": item.readiness,
                }
            )
        coverage = clamp(min(100.0, len(observations) * 12.5))
        progression = {
            str(row["sequence"]): round(row["sequence"] / max(len(rows), 1) * 100.0, 2)
            for row in rows
        }
        score = average(
            [
                coverage,
                100.0 if rows == sorted(rows, key=lambda row: row["sequence"]) else 0.0,
                average([item.quality for item in observations]),
                average([item.readiness for item in observations]),
            ]
        )
        return TimelineResult(
            score=score,
            sequence_count=len(rows),
            coverage=coverage,
            progression=progression,
            timeline=tuple(rows),
        )
