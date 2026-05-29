"""Run parameter sensitivity analysis for the configured research strategy."""

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
    """Run parameter sweep and print best/worst/stable summaries."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    config = ValidationConfigLoader().load(
        PROJECT_ROOT / "configs" / "validation" / "research_quality.yaml"
    )
    summary = StrategyValidationService(PROJECT_ROOT, config).run_parameter_sweep()
    print(
        {
            "strategy": summary.strategy_name,
            "runs": len(summary.results),
            "best_parameter_sets": summary.best_parameter_sets,
            "worst_parameter_sets": summary.worst_parameter_sets,
            "stable_parameter_regions": summary.stable_parameter_regions,
        }
    )


if __name__ == "__main__":
    main()
