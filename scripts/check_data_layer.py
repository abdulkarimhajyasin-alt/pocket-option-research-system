"""End-to-end diagnostics for the research dataset layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.datasets.config import DatasetConfigLoader  # noqa: E402
from app.datasets.normalization import DatasetNormalizer  # noqa: E402
from app.datasets.service import DatasetQualityService  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402


def main() -> None:
    """Verify registry, versioning, quality, normalization, integrity, and statistics."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    service = DatasetQualityService(PROJECT_ROOT, config)
    metadata, version, quality, integrity, statistics = service.inspect()
    synthetic = service.generate_synthetic()
    normalized = DatasetNormalizer().from_rows(
        [
            {
                "time": "2026-01-01T00:00:00+00:00",
                "o": "1.1",
                "h": "1.1002",
                "l": "1.0998",
                "c": "1.1001",
                "vol": "100",
            }
        ],
        config.symbol,
        config.timeframe,
    )
    comparison = service.compare([statistics])
    result = {
        "registry": len(service.registry.list()) >= 1,
        "versioning": version.version == metadata.version,
        "quality": quality.passed,
        "normalization": len(normalized) == 1 and normalized.symbol == config.symbol,
        "integrity": integrity.passed,
        "synthetic_generation": [len(series) for series in synthetic],
        "statistics": statistics.row_count == metadata.row_count,
        "comparison": comparison.datasets == [metadata.dataset_name],
        "quality_score": quality.quality_score,
    }
    print(result)


if __name__ == "__main__":
    main()
