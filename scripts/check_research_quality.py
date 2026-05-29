"""Diagnostics for the strategy validation and research quality layer."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.analytics.validation_quality import ValidationQualityAnalyzer  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.validation.config import ValidationConfigLoader  # noqa: E402
from app.validation.overfitting import OverfittingDetector  # noqa: E402
from app.validation.robustness import RobustnessScorer  # noqa: E402
from app.validation.service import StrategyValidationService  # noqa: E402


def main() -> None:
    """Verify validation engines, scoring, diagnostics, and reporting."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    config = ValidationConfigLoader().load(
        PROJECT_ROOT / "configs" / "validation" / "research_quality.yaml"
    )
    service = StrategyValidationService(PROJECT_ROOT, config)
    walk_forward = service.run_walk_forward()
    sweep = service.run_parameter_sweep()
    out_of_sample = service.run_out_of_sample()
    robustness = RobustnessScorer().score(walk_forward, out_of_sample, sweep)
    warnings = OverfittingDetector().detect(walk_forward, out_of_sample, sweep)
    report, paths = service.run_report()
    analytics = ValidationQualityAnalyzer().analyze(report)
    diagnostics = {
        "validation_engine": True,
        "walk_forward_engine": len(walk_forward.windows) > 0,
        "parameter_sweep_engine": len(sweep.results) > 0,
        "robustness_scoring": robustness.score >= 0,
        "overfitting_detection": isinstance(warnings, list),
        "report_generation": all(path.exists() for path in paths.values()),
        "analytics": analytics.to_dict(),
    }
    print(diagnostics)


if __name__ == "__main__":
    main()
