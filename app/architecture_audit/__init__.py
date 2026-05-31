"""Production research hardening and architecture audit package.

This package audits local architecture only. It does not connect to brokers,
open browsers, authenticate, execute trades, place orders, or handle money.
"""

from app.architecture_audit.service import ArchitectureAuditService

__all__ = ["ArchitectureAuditService"]
