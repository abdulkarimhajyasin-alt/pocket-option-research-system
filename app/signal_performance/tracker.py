"""Tracking for signal intelligence outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.signal_performance.models import TrackedSignal


class SignalTracker:
    """Normalize Signal Intelligence JSON into tracked records."""

    def track(self, signal_payloads: list[dict[str, Any]]) -> list[TrackedSignal]:
        tracked = []
        for index, payload in enumerate(signal_payloads):
            timestamp = datetime.fromisoformat(str(payload["timestamp"]))
            tracked.append(
                TrackedSignal(
                    signal_id=f"{payload.get('asset', 'ASSET')}:{timestamp.isoformat()}:{index}",
                    asset=str(payload.get("asset", "")),
                    classification=str(payload.get("classification_ar", "")),
                    confidence=float(payload.get("confidence", {}).get("score", 0.0)),
                    timestamp=timestamp,
                    structure_state=str(payload.get("structure", {}).get("state", "")),
                    cisd_state=str(payload.get("cisd", {}).get("direction", "")),
                    fvg_state=str(
                        (payload.get("fvg") or {}).get("direction", "لا يوجد")
                    ),
                    ifvg_state="مؤكد"
                    if (payload.get("ifvg") or {}).get("confirmed")
                    else "غير مؤكد",
                    liquidity_state=str(
                        payload.get("liquidity", {}).get("sweep_direction", "")
                    ),
                    session_state=str(payload.get("session", {}).get("session_name", "")),
                    metadata={"research_only": True, "not_execution": True},
                )
            )
        return tracked
