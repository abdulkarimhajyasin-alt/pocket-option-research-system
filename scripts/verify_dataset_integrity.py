"""Verify configured dataset integrity."""

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
    """Print dataset integrity verification."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    service = DatasetQualityService(PROJECT_ROOT, config)
    metadata, _, _, integrity, _ = service.inspect()
    print(
        {
            "dataset_id": metadata.dataset_id,
            "checksum": integrity.checksum,
            "fingerprint": integrity.fingerprint,
            "passed": integrity.passed,
            "issues": integrity.issues,
        }
    )


if __name__ == "__main__":
    main()
