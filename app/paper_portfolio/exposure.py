"""Paper-only exposure analysis."""

from __future__ import annotations

from collections import Counter
from typing import Any


class PaperExposureEngine:
    """Track paper exposure by local attributes."""

    def evaluate(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        assets = Counter(str(item.get("asset", "غير محدد")) for item in orders)
        sessions = Counter(self._session(item) for item in orders)
        directions = Counter(str(item.get("direction", "NO_TRADE")) for item in orders)
        confidence = Counter(self._confidence_band(item.get("confidence")) for item in orders)
        max_count = max(assets.values(), default=0)
        total = len(orders) or 1
        concentration = max_count / total
        score = max(0.0, min(100.0, 100.0 - (concentration * 50.0)))
        return {
            "asset_exposure": dict(assets),
            "session_exposure": dict(sessions),
            "direction_exposure": dict(directions),
            "confidence_exposure": dict(confidence),
            "concentration": round(concentration, 4),
            "exposure_score": round(score, 2),
            "paper_only": True,
        }

    def _session(self, order: dict[str, Any]) -> str:
        metadata = order.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get("session"):
            return str(metadata["session"])
        return "paper"

    def _confidence_band(self, value: Any) -> str:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            confidence = 0.0
        if confidence >= 85:
            return "ثقة مرتفعة"
        if confidence >= 65:
            return "ثقة متوسطة"
        return "ثقة منخفضة"
