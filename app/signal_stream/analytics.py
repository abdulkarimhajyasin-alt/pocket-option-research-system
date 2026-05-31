"""Analytics for signal stream reports and dashboard."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.signal_stream.models import SignalStreamRun


class SignalStreamAnalytics:
    """Generate signal stream distributions."""

    def summarize(self, result: SignalStreamRun) -> dict[str, Any]:
        events = result.stream.events
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        directions = Counter(item.direction.value for item in events)
        sessions = Counter(item.session for item in events)
        assets = Counter(item.asset for item in events)
        confidence = {
            item.signal_id: item.confidence for item in events[:20]
        }
        quality = {
            item.signal_id: item.quality for item in events[:20]
        }
        return {
            "summary": {
                "signal_count": len(events),
                "call_count": directions.get("CALL", 0),
                "put_count": directions.get("PUT", 0),
                "no_trade_count": directions.get("NO_TRADE", 0),
                "average_confidence": result.scoring.confidence_quality,
                "quality_score": result.scoring.signal_quality,
                "readiness_score": result.scoring.score,
                "validation_score": result.validation.score,
                "warning_count": len(result.diagnostics),
                "state": result.scoring.state,
                "research_only": True,
                "signal_generation_only": True,
            },
            "signal_distribution": dict(directions),
            "confidence_distribution": confidence,
            "quality_distribution": quality,
            "readiness_distribution": result.scoring.to_dict(),
            "session_distribution": dict(sessions),
            "asset_distribution": dict(assets),
            "timeline_activity": result.timeline.activity,
            "signal_density": {
                "الكثافة": result.timeline.density,
                "التكرار": result.timeline.frequency,
                "التسلسل": result.timeline.sequence_count,
            },
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
