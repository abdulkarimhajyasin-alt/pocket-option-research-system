"""Generate deterministic synthetic research datasets."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.datasets.config import DatasetConfigLoader  # noqa: E402
from app.datasets.models import DatasetProfile  # noqa: E402
from app.datasets.synthetic import SyntheticDatasetGenerator  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402


def write_csv(path: Path, series: object) -> None:
    """Write candle series to CSV."""
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "open", "high", "low", "close", "volume"],
        )
        writer.writeheader()
        for candle in series:
            writer.writerow(
                {
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume,
                }
            )


def main() -> None:
    """Generate configured synthetic datasets."""
    configure_logging()
    config = DatasetConfigLoader().load(PROJECT_ROOT / "configs/datasets/research_datasets.yaml")
    output_dir = PROJECT_ROOT / "data"
    generator = SyntheticDatasetGenerator()
    generated = {}
    for index, profile in enumerate(config.synthetic_profiles):
        series = generator.generate(
            DatasetProfile(profile),
            symbol=config.symbol,
            timeframe=config.timeframe,
            rows=config.synthetic_rows,
            seed=config.synthetic_seed + index,
        )
        path = output_dir / f"synthetic_{profile}_{config.symbol.lower()}_{config.timeframe}.csv"
        write_csv(path, series)
        generated[profile] = {"path": str(path), "rows": len(series)}
    print({"generated": generated})


if __name__ == "__main__":
    main()
