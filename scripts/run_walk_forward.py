"""Run walk-forward validation for the configured research strategy."""

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
    """Run walk-forward validation and print aggregate metrics."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    config = ValidationConfigLoader().load(
        PROJECT_ROOT / "configs" / "validation" / "research_quality.yaml"
    )
    result = StrategyValidationService(PROJECT_ROOT, config).run_walk_forward()
    print(
        {
            "strategy": result.strategy_name,
            "mode": result.mode.value,
            "windows": len(result.windows),
            "aggregate_metrics": result.aggregate_metrics,
            "stability_metrics": result.stability_metrics,
        }
    )


if __name__ == "__main__":
    main()
