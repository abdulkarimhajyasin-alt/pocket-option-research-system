"""Backward-compatible dashboard report loader wrapper.

Phase 18 moves report discovery and parsing to :mod:`app.reports.repository`.
"""

from app.reports.repository import ReportRepository


class DashboardReportLoader(ReportRepository):
    """Compatibility alias for existing dashboard code and tests."""
