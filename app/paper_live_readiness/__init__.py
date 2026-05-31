"""Paper-to-live readiness gate package.

This package is readiness-only and does not execute trades, connect to brokers,
open browsers, authenticate, place orders, or handle real money.
"""

from app.paper_live_readiness.service import PaperToLiveReadinessService

__all__ = ["PaperToLiveReadinessService"]
