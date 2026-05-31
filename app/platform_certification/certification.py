"""Final platform certification engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.platform_certification.diagnostics import PlatformCertificationDiagnostics
from app.platform_certification.models import (
    GENERATED_AT,
    CertificationDomainResult,
    PlatformCertificationResult,
)
from app.platform_certification.recommendations import PlatformCertificationRecommendations
from app.platform_certification.scoring import PlatformCertificationScoringEngine


class PlatformCertificationEngine:
    """Evaluate the local research platform across certification domains."""

    DOMAIN_PATHS: dict[str, tuple[str, tuple[tuple[str, ...], ...]]] = {
        "architecture": (
            "المعمارية",
            (("reports", "architecture_audit", "architecture_summary.json"),),
        ),
        "safety": (
            "السلامة",
            (("reports", "integration_safety", "safety_summary.json"),),
        ),
        "research_quality": (
            "جودة البحث",
            (("reports", "research_ops", "operations_summary.json"),),
        ),
        "knowledge_graph": (
            "خريطة المعرفة",
            (("reports", "knowledge_graph", "knowledge_summary.json"),),
        ),
        "research_api": (
            "واجهة البحث الموحدة",
            (("reports", "research_api", "research_summary.json"),),
        ),
        "research_archive": (
            "أرشيف البحث",
            (("reports", "research_archive", "archive_summary.json"),),
        ),
        "dashboard": (
            "لوحة التحكم",
            (("app", "templates", "dashboard", "base.html"),),
        ),
        "observation": (
            "المراقبة",
            (("reports", "market_observation", "observation_summary.json"),),
        ),
        "paper_trading": (
            "الورقي",
            (
                ("reports", "paper_execution", "paper_execution_summary.json"),
                ("reports", "paper_portfolio", "portfolio_summary.json"),
            ),
        ),
        "readiness": (
            "الجاهزية",
            (("reports", "paper_live_readiness", "readiness_summary.json"),),
        ),
    }

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.scoring = PlatformCertificationScoringEngine()
        self.diagnostics = PlatformCertificationDiagnostics()
        self.recommendations = PlatformCertificationRecommendations()

    def certify(self) -> PlatformCertificationResult:
        domains = [self._evaluate_domain(domain_id) for domain_id in self.DOMAIN_PATHS]
        domain_payloads = [domain.to_dict() for domain in domains]
        diagnostics = self.diagnostics.aggregate(domain_payloads)
        high_risk = sum(1 for item in diagnostics if item.get("severity") == "مرتفع")
        final_score = self.scoring.platform_score([domain.score for domain in domains])
        state = self.scoring.certification_state(final_score, high_risk)
        return PlatformCertificationResult(
            certification_id="final-research-platform-certification",
            generated_at=GENERATED_AT,
            final_platform_score=final_score,
            certification_state=state,
            research_maturity_level=self.scoring.maturity_level(final_score),
            maturity_score=final_score,
            domain_scores=domains,
            diagnostics=diagnostics,
            recommendations=self.recommendations.aggregate(diagnostics),
            safety_boundary=self.safety_boundary(),
        )

    def safety_boundary(self) -> dict[str, bool]:
        return {
            "research_only": True,
            "local_only": True,
            "no_broker_access": True,
            "no_broker_api": True,
            "no_pocket_option_login": True,
            "no_browser_automation": True,
            "no_selenium": True,
            "no_playwright": True,
            "no_authentication": True,
            "no_credentials": True,
            "no_order_placement": True,
            "no_live_trading": True,
            "no_money_handling": True,
            "no_broker_control": True,
            "no_external_execution_adapters": True,
        }

    def _evaluate_domain(self, domain_id: str) -> CertificationDomainResult:
        label, paths = self.DOMAIN_PATHS[domain_id]
        available, missing = self.diagnostics.existing_count(self.project_root, paths)
        payload = self._domain_payload(paths)
        unsafe = self.diagnostics.unsafe_metadata(payload)
        diagnostics = self.diagnostics.domain_diagnostics(domain_id, missing, unsafe)
        penalty = 30 if unsafe else 0
        score = self.scoring.score_domain(available, len(paths), penalty)
        return CertificationDomainResult(
            domain_id=domain_id,
            label_ar=label,
            score=score,
            status=self.scoring.domain_status(score),
            diagnostics=diagnostics,
            recommendations=self.recommendations.for_domain(domain_id, diagnostics),
        )

    def _domain_payload(self, paths: tuple[tuple[str, ...], ...]) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for parts in paths:
            path = self.project_root.joinpath(*parts)
            if not path.exists() or path.suffix != ".json":
                continue
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            payload["/".join(parts)] = loaded
        return payload
