"""Diagnostics for unified research API aggregation."""

from __future__ import annotations

from typing import Any


class ResearchAPIDiagnostics:
    """Build deterministic diagnostics for missing or sparse local research reports."""

    def evaluate(self, sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
        missing = sorted(key for key, payload in sources.items() if not payload)
        available = sorted(key for key, payload in sources.items() if bool(payload))
        warnings = {
            "missing_source_count": len(missing),
            "available_source_count": len(available),
        }
        return {
            "summary": warnings,
            "missing_sources": missing,
            "available_sources": available,
            "severity": "متوسط" if missing else "منخفض",
            "research_only": True,
        }

    def recommendations(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        """Return deterministic Arabic recommendations."""
        missing = diagnostics.get("missing_sources", [])
        if missing:
            return {
                "تحسين اكتمال التقارير": len(missing),
                "إعادة تشغيل المسارات البحثية المحلية": len(missing),
            }
        return {"الحفاظ على اتساق واجهة البحث الموحدة": 1}
