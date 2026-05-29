"""Run complete strategy validation research workflow."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.validation.config import ValidationConfigLoader  # noqa: E402
from app.validation.service import StrategyValidationService  # noqa: E402


def main() -> None:
    """Run full validation and print a compact summary."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    config = ValidationConfigLoader().load(
        PROJECT_ROOT / "configs" / "validation" / "research_quality.yaml"
    )
    report, paths = StrategyValidationService(PROJECT_ROOT, config).run_report()
    print(
        {
            "strategy": report.strategy_name,
            "robustness_score": report.robustness.score,
            "category": report.robustness.category.value,
            "warnings": len(report.overfitting_warnings),
            "reports": {name: str(path) for name, path in paths.items()},
        }
    )


if __name__ == "__main__":
    main()
