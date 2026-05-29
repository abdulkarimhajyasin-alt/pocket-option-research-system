"""Dataset integrity verification."""

from __future__ import annotations

import hashlib

from app.data.models import Candle
from app.datasets.models import DatasetMetadata, IntegrityReport
from app.datasets.utils import stable_datetime


class DatasetIntegrityVerifier:
    """Build deterministic checksums and integrity reports."""

    def checksum(self, candles: list[Candle] | tuple[Candle, ...]) -> str:
        """Return SHA-256 checksum for normalized candle content."""
        digest = hashlib.sha256()
        for candle in sorted(candles, key=lambda item: item.timestamp):
            line = (
                f"{candle.symbol}|{candle.timeframe}|{stable_datetime(candle.timestamp)}|"
                f"{candle.open:.10f}|{candle.high:.10f}|{candle.low:.10f}|"
                f"{candle.close:.10f}|{candle.volume if candle.volume is not None else ''}\n"
            )
            digest.update(line.encode("utf-8"))
        return digest.hexdigest()

    def fingerprint(self, metadata: DatasetMetadata) -> str:
        """Return stable metadata fingerprint."""
        payload = (
            f"{metadata.dataset_id}|{metadata.dataset_name}|{metadata.source}|"
            f"{metadata.symbol}|{metadata.timeframe}|{metadata.row_count}|"
            f"{metadata.checksum}|{metadata.version}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def verify(
        self,
        candles: list[Candle] | tuple[Candle, ...],
        metadata: DatasetMetadata,
    ) -> IntegrityReport:
        """Verify row count, schema shape, and checksum."""
        checksum = self.checksum(candles)
        issues: list[str] = []
        schema_valid = all(
            candle.symbol and candle.timeframe and candle.timestamp for candle in candles
        )
        row_count_valid = len(candles) == metadata.row_count
        checksum_valid = checksum == metadata.checksum
        if not schema_valid:
            issues.append("schema validation failed")
        if not row_count_valid:
            issues.append("row count mismatch")
        if not checksum_valid:
            issues.append("checksum mismatch")
        return IntegrityReport(
            dataset_id=metadata.dataset_id,
            checksum=checksum,
            fingerprint=self.fingerprint(metadata),
            row_count=len(candles),
            schema_valid=schema_valid,
            row_count_valid=row_count_valid,
            checksum_valid=checksum_valid,
            issues=issues,
        )
