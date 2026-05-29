"""Run deterministic dataset comparison diagnostics."""

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
    """Compare configured sample data with deterministic synthetic datasets."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    service = DatasetQualityService(PROJECT_ROOT, config)
    _, _, _, _, sample_stats = service.inspect()
    all_stats = [sample_stats]
    for series in service.generate_synthetic():
        name = f"synthetic_{series.symbol.lower()}_{series.timeframe}_{len(all_stats)}"
        _, _, _, _, stats = service.inspect(
            candles=series,
            dataset_name=name,
            source=f"synthetic://{name}",
            version="v1",
        )
        all_stats.append(stats)
    report = service.compare(all_stats)
    paths = service.exporter.export_comparison(report)
    analytics = DatasetQualityAnalyzer().compare(report)
    print(
        {
            "datasets": report.datasets,
            "rankings": report.rankings,
            "analytics": analytics,
            "reports": {key: str(path) for key, path in paths.items()},
        }
    )


if __name__ == "__main__":
    main()
