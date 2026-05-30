"""Research certification analytics."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.research_certification.models import ResearchCertificationResult


class ResearchCertificationAnalytics:
    """Build distributions for certification reports and dashboard."""

    def summarize(self, result: ResearchCertificationResult) -> dict[str, Any]:
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        requirements = Counter(item.status_ar for item in result.requirements.checks)
        return {
            "summary": {
                "certification_score": result.certification.score,
                "certification_state": result.certification.state,
                "maturity_score": result.maturity.score,
                "stability_score": result.stability.score,
                "consistency_score": result.consistency.score,
                "robustness_score": result.robustness.score,
                "warning_count": result.requirements.warnings,
                "failure_count": result.requirements.failures,
                "recommendation_count": len(result.recommendations),
                "sample_size": result.sample_size,
                "research_only": True,
            },
            "certification_distribution": {
                result.certification.state: result.certification.score
            },
            "maturity_distribution": result.maturity.to_dict(),
            "robustness_distribution": result.robustness.to_dict(),
            "consistency_distribution": result.consistency.to_dict(),
            "stability_distribution": result.stability.to_dict(),
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "requirements_distribution": dict(requirements),
            "failure_distribution": {
                item.name: 1
                for item in result.requirements.checks
                if item.status == "FAIL"
            },
            "certification_timeline": {
                result.timestamp.strftime("%H:%M"): result.certification.score
            },
            "maturity_timeline": {
                result.timestamp.strftime("%H:%M"): result.maturity.score
            },
            "latest": result.to_dict(),
        }
