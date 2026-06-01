"""Strategic gap analysis for future architecture discussions."""

from __future__ import annotations

from app.post_research_architecture.models import StrategicGapAnalysis


class PostResearchGapAnalysisEngine:
    """Compare Research Platform v1.0 with a hypothetical future program."""

    def build(self) -> StrategicGapAnalysis:
        categories = [
            self._gap(
                "Data readiness",
                "Strong local research datasets, normalization, quality checks, and reports.",
                ["Production feed contracts", "Data licensing review", "Data retention policy"],
                "متوسط",
                "مرتفع",
                "Create production-grade data governance before external use.",
            ),
            self._gap(
                "Signal readiness",
                "Research classifications and explainable analytics exist.",
                ["Independent validation", "Human approval gates", "Forward-test governance"],
                "مرتفع",
                "مرتفع",
                "Keep signal outputs as research until independently governed.",
            ),
            self._gap(
                "Observation readiness",
                "Passive local observation and replay pipelines exist.",
                ["Operational source contracts", "Monitoring SLAs", "Incident review"],
                "متوسط",
                "مرتفع",
                "Separate observation operations from research artifacts.",
            ),
            self._gap(
                "Paper readiness",
                "Paper-only execution and portfolio governance exist.",
                ["External sandbox boundary", "Human review", "Independent risk signoff"],
                "متوسط",
                "مرتفع",
                "Use paper outputs only as evidence for future design.",
            ),
            self._gap(
                "Risk readiness",
                "Research and paper risk checks exist.",
                ["Real-world hard limits", "Independent kill switch", "Incident playbooks"],
                "حرج",
                "مرتفع",
                "Design risk governance before any implementation discussion.",
            ),
            self._gap(
                "Execution readiness",
                "Offline and paper simulation exist only.",
                ["Isolated gateway design", "Audit trail", "Failure containment"],
                "حرج",
                "مرتفع",
                "Do not implement execution in the current repository.",
            ),
            self._gap(
                "Broker readiness",
                "Broker-readiness research exists with forbidden live access.",
                ["Broker isolation", "Credential vault design", "Legal review"],
                "حرج",
                "مرتفع",
                "Keep broker work in a separate future architecture program.",
            ),
            self._gap(
                "Monitoring readiness",
                "Local diagnostics and reports exist.",
                ["Operational observability", "Alerting", "On-call response"],
                "مرتفع",
                "مرتفع",
                "Define monitoring architecture before external systems are considered.",
            ),
            self._gap(
                "Governance readiness",
                "Certification and release packaging exist.",
                ["Approval gates", "Change control", "Rollback governance"],
                "مرتفع",
                "مرتفع",
                "Create human governance before any future build plan.",
            ),
            self._gap(
                "Compliance readiness",
                "No compliance approval exists in the repository.",
                ["Legal review", "Jurisdiction review", "User/account policy"],
                "حرج",
                "مرتفع",
                "Require legal and regulatory review outside this repository.",
            ),
            self._gap(
                "Production readiness",
                "The platform is local research software.",
                ["Deployment design", "Access control", "Backup and recovery"],
                "حرج",
                "مرتفع",
                "Do not treat the research release as production software.",
            ),
        ]
        return StrategicGapAnalysis(
            current_capabilities=[
                "Research reports",
                "Local dashboard and APIs",
                "Validation and certification",
                "Paper-only simulation",
                "Research archive and knowledge graph",
                "Release packaging",
            ],
            missing_capabilities=[
                "Production governance",
                "Compliance approval",
                "Operational monitoring",
                "Isolated future-system design",
                "Human approval workflows",
                "Incident response process",
            ],
            technical_gaps=categories,
            operational_gaps=[
                "No production runbook",
                "No on-call model",
                "No incident response ownership",
            ],
            safety_gaps=[
                "Future risk controls are not designed for real-world operations.",
                "Future account and credential policies are intentionally absent.",
            ],
            production_gaps=[
                "No production deployment model",
                "No production database architecture",
                "No multi-user access model",
            ],
            compliance_gaps=[
                "No legal review",
                "No jurisdictional assessment",
                "No broker terms review",
            ],
            severity="حرج",
            recommendations=[
                "Freeze Research Platform v1.0 before any separate program.",
                "Resolve documentation and metadata drift.",
                "Open a separate architecture program only after governance approval.",
            ],
        )

    def _gap(
        self,
        category: str,
        current_state: str,
        missing: list[str],
        gap_level: str,
        risk_level: str,
        recommendation: str,
    ) -> dict[str, object]:
        return {
            "category": category,
            "current_state": current_state,
            "missing_requirements": missing,
            "gap_level": gap_level,
            "risk_level": risk_level,
            "recommendation": recommendation,
        }
