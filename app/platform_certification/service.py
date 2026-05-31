"""Service layer for final research platform certification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.platform_certification.certification import PlatformCertificationEngine
from app.platform_certification.models import PlatformCertificationResult
from app.platform_certification.reports import PlatformCertificationReportWriter
from app.platform_certification.storage import PlatformCertificationStorage


@dataclass(frozen=True)
class PlatformCertificationRunResult:
    """Result of one platform certification run."""

    certification: PlatformCertificationResult
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PlatformCertificationService:
    """Run and expose final research platform certification."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = PlatformCertificationEngine(self.project_root)
        self.storage = PlatformCertificationStorage(
            self.project_root / "storage" / "platform_certification"
        )
        self.reports = PlatformCertificationReportWriter(
            self.project_root / "reports" / "platform_certification"
        )

    def certify(self) -> PlatformCertificationResult:
        return self.engine.certify()

    def run(self) -> PlatformCertificationRunResult:
        certification = self.certify()
        storage_paths = self.storage.save(certification)
        report_paths = self.reports.export(certification)
        return PlatformCertificationRunResult(certification, storage_paths, report_paths)

    def summary(self) -> dict[str, object]:
        result = self.certify().to_dict()
        return {
            "final_platform_score": result["final_platform_score"],
            "certification_state": result["certification_state"],
            "research_maturity_level": result["research_maturity_level"],
            "maturity_score": result["maturity_score"],
            "research_only": True,
            "local_only": True,
        }

    def domains(self) -> list[dict[str, object]]:
        return self.certify().to_dict()["domain_scores"]

    def diagnostics_view(self) -> list[dict[str, object]]:
        return self.certify().to_dict()["diagnostics"]

    def recommendations_view(self) -> list[str]:
        return self.certify().to_dict()["recommendations"]
