"""Run dataset statistics diagnostics."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.analytics.dataset_quality import DatasetQualityAnalyzer  # noqa: E402
from app.datasets.config import DatasetConfigLoader  # noqa: E402
from app.datasets.service import DatasetQualityService  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402


def main() -> None:
    """Print configured dataset statistics."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    service = DatasetQualityService(PROJECT_ROOT, config)
    metadata, version, quality, integrity, statistics = service.inspect()
    service.export(metadata, version, quality, integrity, statistics)
    analytics = DatasetQualityAnalyzer().analyze(statistics, quality)
    print({"statistics": statistics.to_dict(), "analytics": analytics.to_dict()})


if __name__ == "__main__":
    main()
