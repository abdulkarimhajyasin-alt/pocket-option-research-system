"""Tests for research dataset management and quality tooling."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.analytics.dataset_quality import DatasetQualityAnalyzer
from app.data.models import Candle, CandleSeries
from app.datasets.comparison import DatasetComparisonEngine
from app.datasets.gaps import GapDetector
from app.datasets.integrity import DatasetIntegrityVerifier
from app.datasets.models import DatasetProfile, GapSeverity
from app.datasets.normalization import DatasetNormalizer
from app.datasets.quality import DataQualityEngine
from app.datasets.registry import DatasetRegistry
from app.datasets.reporting import DatasetReportExporter
from app.datasets.service import DatasetQualityService
from app.datasets.statistics import DatasetStatisticsEngine
from app.datasets.synthetic import SyntheticDatasetGenerator
from app.datasets.versioning import DatasetVersionManager
from app.datasets.config import DatasetLayerConfig
from app.storage.persistence import PersistenceService


def make_series(count: int = 20, gap_at: int | None = None) -> CandleSeries:
    """Build deterministic candle data."""
    base = datetime(2026, 1, 1, tzinfo=UTC)
    candles = []
    price = 1.1
    offset = 0
    for index in range(count):
        if gap_at is not None and index == gap_at:
            offset += 2
        timestamp = base + timedelta(minutes=index + offset)
        close = price + (0.0001 if index % 2 == 0 else -0.00005)
        candles.append(
            Candle(
                symbol="EURUSD",
                timeframe="1m",
                timestamp=timestamp,
                open=price,
                high=max(price, close) + 0.0001,
                low=min(price, close) - 0.0001,
                close=close,
                volume=100.0,
            )
        )
        price = close
    return CandleSeries("EURUSD", "1m", candles)


def test_registry_versioning_and_integrity() -> None:
    series = make_series()
    registry = DatasetRegistry()
    metadata = registry.register("unit", "memory.csv", series, tags=("unit",))
    duplicate = registry.register("unit", "memory.csv", series, tags=("unit",))
    version = DatasetVersionManager().add_version(metadata, 100.0)
    integrity = DatasetIntegrityVerifier().verify(list(series), metadata)
    assert metadata.dataset_id == duplicate.dataset_id
    assert version.dataset_id == metadata.dataset_id
    assert integrity.passed
    assert registry.get(metadata.dataset_id).checksum == metadata.checksum


def test_quality_engine_and_gap_detection() -> None:
    series = make_series(gap_at=5)
    report = DataQualityEngine().analyze(list(series), "unit", "unit", "EURUSD", "1m")
    gaps = GapDetector().detect(list(series), "1m")
    assert report.quality_score < 100
    assert report.warnings
    assert gaps
    assert gaps[0].severity in {GapSeverity.SUSPICIOUS, GapSeverity.SEVERE}


def test_normalization_and_synthetic_generation() -> None:
    normalized = DatasetNormalizer().from_rows(
        [
            {
                "time": "2026-01-01T00:00:00Z",
                "o": "1.1",
                "h": "1.1002",
                "l": "1.0999",
                "c": "1.1001",
                "vol": "10",
            }
        ],
        "eur/usd",
        "m1",
    )
    first = SyntheticDatasetGenerator().generate(DatasetProfile.TRENDING, rows=10, seed=7)
    second = SyntheticDatasetGenerator().generate(DatasetProfile.TRENDING, rows=10, seed=7)
    assert normalized.symbol == "EURUSD"
    assert normalized.timeframe == "1m"
    assert [candle.close for candle in first] == [candle.close for candle in second]


def test_statistics_comparison_reporting_and_analytics(tmp_path: Path) -> None:
    series = make_series()
    metadata = DatasetRegistry().register("unit", "memory.csv", series)
    quality = DataQualityEngine().analyze(list(series), metadata.dataset_id, "unit", "EURUSD", "1m")
    integrity = DatasetIntegrityVerifier().verify(list(series), metadata)
    stats = DatasetStatisticsEngine().calculate(list(series), metadata, quality)
    version = DatasetVersionManager().add_version(metadata, quality.quality_score)
    comparison = DatasetComparisonEngine().compare([stats])
    paths = DatasetReportExporter(tmp_path).export_dataset_report(
        metadata,
        version,
        quality,
        integrity,
        stats,
    )
    comparison_paths = DatasetReportExporter(tmp_path).export_comparison(comparison)
    analytics = DatasetQualityAnalyzer().analyze(stats, quality)
    assert paths["json"].exists()
    assert comparison_paths["text"].exists()
    assert analytics.row_count == len(series)
    assert comparison.rankings[0]["dataset_name"] == "unit"


def test_dataset_service_persistence(tmp_path: Path) -> None:
    config = DatasetLayerConfig(
        dataset_name="unit",
        dataset_path="unused.csv",
        reports_dir=str(tmp_path / "reports"),
    )
    service = DatasetQualityService(tmp_path, config)
    metadata, version, quality, integrity, statistics = service.inspect(
        candles=make_series(),
        dataset_name="unit",
        source="memory.csv",
    )
    assert metadata.row_count == 20
    assert version.quality_score == quality.quality_score
    assert integrity.passed
    assert statistics.quality_score == quality.quality_score


def test_dataset_persistence_events(tmp_path: Path) -> None:
    persistence = PersistenceService(tmp_path / "dataset.db", session_id="dataset_unit")
    persistence.persist_dataset_quality_report("dataset", {"quality_score": 99.0})
    events = persistence.events.replay(session_id="dataset_unit", event_type="dataset.quality")
    persistence.close()
    assert len(events) == 1
    assert events[0].payload["quality_score"] == 99.0


def test_cli_data_layer_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/check_data_layer.py"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert "quality_score" in completed.stdout
