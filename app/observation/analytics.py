"""Deterministic analytics for market observation snapshots."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from app.observation.models import BrokerSnapshot


class ObservationAnalytics:
    """Build market visibility metrics without trading recommendations."""

    def summarize(self, snapshot: BrokerSnapshot) -> dict[str, Any]:
        """Return deterministic observation metrics."""
        active_assets = [asset for asset in snapshot.assets if asset.is_active]
        payouts = [payout.payout_percent for payout in snapshot.payouts]
        activity_scores = [asset.activity_score for asset in snapshot.assets]
        session_activity = {
            session.session_name: round(session.activity_score, 2)
            for session in snapshot.sessions
        }
        asset_activity = {
            asset.asset: round(asset.activity_score, 2)
            for asset in sorted(
                snapshot.assets,
                key=lambda item: (-item.activity_score, item.asset),
            )
        }
        market_activity_score = round(mean(activity_scores), 2) if activity_scores else 0.0
        observation_count = (
            len(snapshot.assets)
            + len(snapshot.markets)
            + len(snapshot.payouts)
            + len(snapshot.sessions)
            + len(snapshot.candles)
        )
        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "source": snapshot.source,
            "research_only": True,
            "observation_only": True,
            "active_assets": len(active_assets),
            "average_payout": round(mean(payouts), 2) if payouts else 0.0,
            "payout_distribution": self._payout_distribution(payouts),
            "market_activity_score": market_activity_score,
            "observation_count": observation_count,
            "session_activity": session_activity,
            "asset_activity": asset_activity,
            "assessment": self.assess(market_activity_score, observation_count),
        }

    def assess(
        self,
        market_activity_score: float,
        observation_count: int,
    ) -> dict[str, str]:
        """Assess observation readiness without predicting profitability."""
        if observation_count < 10:
            return {
                "activity": "نشاط منخفض",
                "readiness": "بيانات غير كافية",
                "severity": "warning",
            }
        if market_activity_score >= 70:
            return {
                "activity": "نشاط مرتفع",
                "readiness": "فرص مراقبة جيدة",
                "severity": "healthy",
            }
        if market_activity_score >= 45:
            return {
                "activity": "نشاط متوسط",
                "readiness": "مراقبة إضافية مطلوبة",
                "severity": "warning",
            }
        return {
            "activity": "نشاط منخفض",
            "readiness": "مراقبة إضافية مطلوبة",
            "severity": "warning",
        }

    def _payout_distribution(self, payouts: list[float]) -> dict[str, int]:
        buckets = Counter({"أقل من 70%": 0, "70% إلى 79%": 0, "80% فأعلى": 0})
        for payout in payouts:
            if payout < 70:
                buckets["أقل من 70%"] += 1
            elif payout < 80:
                buckets["70% إلى 79%"] += 1
            else:
                buckets["80% فأعلى"] += 1
        return dict(buckets)
