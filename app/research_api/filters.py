"""Deterministic filtering helpers for research API payloads."""

from __future__ import annotations

from typing import Any


class ResearchDataFilter:
    """Normalize report payloads into stable JSON-safe dictionaries."""

    def normalize(self, payload: Any) -> dict[str, Any]:
        """Return a deterministic dictionary shape for arbitrary local JSON."""
        if isinstance(payload, dict):
            summary = payload.get("summary", payload)
            latest = payload.get("latest", {})
            return {
                "summary": summary if isinstance(summary, dict) else {},
                "latest_available": isinstance(latest, dict) and bool(latest),
                "raw_available": bool(payload),
            }
        if isinstance(payload, list):
            return {
                "summary": {"item_count": len(payload)},
                "latest_available": bool(payload),
                "raw_available": bool(payload),
            }
        return {"summary": {}, "latest_available": False, "raw_available": False}
