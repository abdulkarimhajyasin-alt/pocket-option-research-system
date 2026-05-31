"""Unified local research API package.

This package exposes canonical local research outputs only. It does not connect
to brokers, automate browsers, authenticate, place orders, execute trades, or
handle money.
"""

from app.research_api.service import UnifiedResearchAPIService

__all__ = ["UnifiedResearchAPIService"]
