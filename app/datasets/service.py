"""High-level dataset quality orchestration."""

from __future__ import annotations

from pathlib import Path

from app.data.csv_loader import CsvCandleLoader
from app.data.models import CandleSeries
from app.datasets.config import DatasetLayerConfig
from app.datasets.comparison import DatasetComparisonEngine
from app.datasets.integrity import DatasetIntegrityVerifier
from app.datasets.models import (
    DatasetComparisonReport,
    DatasetMetadata,
    DatasetProfile,
    DatasetStatistics,
    DatasetVersion,
    IntegrityReport,
    QualityReport,
)
from app.datasets.quality import DataQualityEngine
from app.datasets.registry import DatasetRegistry
from app.datasets.reporting import DatasetReportExporter
from app.datasets.statistics import DatasetStatisticsEngine
from app.datasets.synthetic import SyntheticDatasetGenerator
from app.datasets.versioning import DatasetVersionManager
from app.storage.persistence import PersistenceService


class DatasetInspector:
    """Pure dataset inspection without file export or persistence side effects."""

    def __init__(self, project_root: Path, config: DatasetLayerConfig) -> None:
        self.project_root = project_root
        self.config = config
        self.registry = DatasetRegistry()
        self.versions = DatasetVersionManager()
        self.quality_engine = DataQualityEngine()
        self.integrity = DatasetIntegrityVerifier()
        self.statistics_engine = DatasetStatisticsEngine()
        self.synthetic = SyntheticDatasetGenerator()

    def load_configured_dataset(self) -> CandleSeries:
        """Load configured CSV dataset using existing data loader."""
        return CsvCandleLoader().load(
            self.project_root / self.config.dataset_path,
            self.config.symbol,
            self.config.timeframe,
        )

    def inspect(
        self,
        candles: CandleSeries | None = None,
        dataset_name: str | None = None,
        source: str | None = None,
        version: str | None = None,
    ) -> tuple[DatasetMetadata, DatasetVersion, QualityReport, IntegrityReport, DatasetStatistics]:
        """Run full dataset inspection without storing raw candles or writing side effects."""
        series = candles or self.load_configured_dataset()
        name = dataset_name or self.config.dataset_name
        source_path = source or str(self.project_root / self.config.dataset_path)
        metadata = self.registry.register(
            name,
            source_path,
            series,
            version or self.config.version,
            self.config.tags,
        )
        candle_rows = list(series)
        quality = self.quality_engine.analyze(
            candle_rows,
            metadata.dataset_id,
            metadata.dataset_name,
            metadata.symbol,
            metadata.timeframe,
        )
        integrity = self.integrity.verify(candle_rows, metadata)
        statistics = self.statistics_engine.calculate(candle_rows, metadata, quality)
        version_record = self.versions.add_version(metadata, quality.quality_score)
        return metadata, version_record, quality, integrity, statistics

    def generate_synthetic(self) -> list[CandleSeries]:
        """Generate configured synthetic datasets."""
        return [
            self.synthetic.generate(
                DatasetProfile(profile),
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
                rows=self.config.synthetic_rows,
                seed=self.config.synthetic_seed + index,
            )
            for index, profile in enumerate(self.config.synthetic_profiles)
        ]

    def compare(self, statistics: list[DatasetStatistics]) -> DatasetComparisonReport:
        """Compare statistics across datasets."""
        return DatasetComparisonEngine().compare(statistics)


class DatasetExporter:
    """Exports dataset reports explicitly."""

    def __init__(self, project_root: Path, config: DatasetLayerConfig) -> None:
        self.exporter = DatasetReportExporter(project_root / config.reports_dir)

    def export(
        self,
        metadata: DatasetMetadata,
        version: DatasetVersion,
        quality: QualityReport,
        integrity: IntegrityReport,
        statistics: DatasetStatistics,
    ) -> dict[str, Path]:
        """Export dataset report files."""
        return self.exporter.export_dataset_report(
            metadata, version, quality, integrity, statistics
        )


class DatasetPersistenceAdapter:
    """Persists dataset inspection artifacts explicitly."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def persist(
        self,
        metadata: DatasetMetadata,
        version: DatasetVersion,
        quality: QualityReport,
        integrity: IntegrityReport,
        statistics: DatasetStatistics,
    ) -> None:
        """Persist dataset artifacts through the existing event store."""
        persistence = PersistenceService(
            self.project_root / "storage" / "trading_system.db",
            session_id="dataset_quality",
        )
        persistence.persist_dataset_registry_metadata(metadata.dataset_id, metadata.to_dict())
        persistence.persist_dataset_version(metadata.dataset_id, version.to_dict())
        persistence.persist_dataset_quality_report(metadata.dataset_id, quality.to_dict())
        persistence.persist_dataset_integrity_report(metadata.dataset_id, integrity.to_dict())
        persistence.persist_dataset_statistics(metadata.dataset_id, statistics.to_dict())
        persistence.close()


class DatasetQualityService:
    """Coordinate dataset inspection, export, and persistence through explicit adapters."""

    def __init__(self, project_root: Path, config: DatasetLayerConfig) -> None:
        self.project_root = project_root
        self.config = config
        self.inspector = DatasetInspector(project_root, config)
        self.exporter = DatasetExporter(project_root, config)
        self.persistence = DatasetPersistenceAdapter(project_root)
        self.registry = self.inspector.registry
        self.versions = self.inspector.versions
        self.quality_engine = self.inspector.quality_engine
        self.integrity = self.inspector.integrity
        self.statistics_engine = self.inspector.statistics_engine
        self.synthetic = self.inspector.synthetic

    def load_configured_dataset(self) -> CandleSeries:
        """Load configured CSV dataset using existing data loader."""
        return self.inspector.load_configured_dataset()

    def inspect(
        self,
        candles: CandleSeries | None = None,
        dataset_name: str | None = None,
        source: str | None = None,
        version: str | None = None,
        persist: bool = True,
    ) -> tuple[DatasetMetadata, DatasetVersion, QualityReport, IntegrityReport, DatasetStatistics]:
        """Run dataset inspection and optionally persist for backward compatibility."""
        result = self.inspector.inspect(candles, dataset_name, source, version)
        if persist:
            self.persist(*result)
        return result

    def generate_synthetic(self) -> list[CandleSeries]:
        """Generate configured synthetic datasets."""
        return self.inspector.generate_synthetic()

    def compare(self, statistics: list[DatasetStatistics]) -> DatasetComparisonReport:
        """Compare statistics across datasets."""
        return self.inspector.compare(statistics)

    def export(
        self,
        metadata: DatasetMetadata,
        version: DatasetVersion,
        quality: QualityReport,
        integrity: IntegrityReport,
        statistics: DatasetStatistics,
    ) -> dict[str, Path]:
        """Export dataset report files."""
        return self.exporter.export(metadata, version, quality, integrity, statistics)

    def persist(
        self,
        metadata: DatasetMetadata,
        version: DatasetVersion,
        quality: QualityReport,
        integrity: IntegrityReport,
        statistics: DatasetStatistics,
    ) -> None:
        """Persist dataset artifacts through the existing event store."""
        self.persistence.persist(metadata, version, quality, integrity, statistics)
