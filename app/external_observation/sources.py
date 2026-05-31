"""Source registry for the external observation sandbox."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.external_observation.models import ObservationSource
from app.external_observation.models import SUPPORTED_SOURCE_TYPES


class ObservationSourceRegistry:
    """Build passive source models from local project artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def discover(self) -> tuple[ObservationSource, ...]:
        sources = [
            self._source(
                "simulated-research",
                "مصدر محاكاة بحثي",
                "simulated",
                self.project_root / "reports" / "research_ops" / "operations_summary.json",
                "نتائج بحث محلية",
            ),
            self._source(
                "local-sample-file",
                "ملف عينة محلي",
                "local_file",
                self.project_root / "data" / "sample_eurusd_m1.csv",
                "شموع محفوظة محليا",
            ),
            self._source(
                "historical-dataset",
                "بيانات تاريخية",
                "historical_dataset",
                self.project_root / "reports" / "market_data" / "market_summary.json",
                "تحليلات بيانات تاريخية",
            ),
            self._source(
                "sandbox-feed",
                "تغذية صندوقية",
                "sandbox_feed",
                self.project_root / "reports" / "observation" / "observation_summary.json",
                "مخرجات مراقبة محلية",
            ),
        ]
        return tuple(sources)

    def _source(
        self,
        source_id: str,
        name: str,
        source_type: str,
        path: Path,
        scope: str,
    ) -> ObservationSource:
        exists = path.exists()
        compatible = source_type in SUPPORTED_SOURCE_TYPES
        readable = self._is_readable(path) if exists else False
        validation_status = "ناجح" if exists and readable and compatible else "تحذير"
        observation_status = "نشط" if exists else "غير مكتمل"
        return ObservationSource(
            source_id=source_id,
            source_name=name,
            source_type=source_type,
            observation_status=observation_status,
            visibility_scope=scope,
            validation_status=validation_status,
            isolation_status="معزول",
        )

    def _is_readable(self, path: Path) -> bool:
        try:
            if path.suffix.lower() == ".json":
                payload: Any = json.loads(path.read_text(encoding="utf-8"))
                return isinstance(payload, (dict, list))
            return path.stat().st_size > 0
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return False
