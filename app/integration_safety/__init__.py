"""External integration safety boundary package.

This package defines local safety policies only. It does not connect to brokers,
open browsers, authenticate, place orders, execute trades, or handle money.
"""

from app.integration_safety.service import IntegrationSafetyService

__all__ = ["IntegrationSafetyService"]
