"""Check configured research dataset quality."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.datasets.config import DatasetConfigLoader  # noqa: E402
from app.datasets.service import DatasetQualityService  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402


def main() -> None:
    """Run dataset quality diagnostics."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    service = DatasetQualityService(PROJECT_ROOT, config)
    metadata, version, quality, integrity, statistics = service.inspect()
    paths = service.export(metadata, version, quality, integrity, statistics)
    result = {
        "dataset_id": metadata.dataset_id,
        "dataset_name": metadata.dataset_name,
        "version": metadata.version,
        "quality_score": quality.quality_score,
        "passed": quality.passed and integrity.passed,
        "warnings": len(quality.warnings),
        "errors": len(quality.errors),
        "reports": {key: str(path) for key, path in paths.items()},
    }
    print(result)


if __name__ == "__main__":
    main()
