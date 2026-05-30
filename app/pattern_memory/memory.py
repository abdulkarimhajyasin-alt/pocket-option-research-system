"""Pattern memory builder from local research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.pattern_memory.models import PatternMemoryRecord


class PatternMemoryBuilder:
    """Build research-only pattern memory records from storage JSON files."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def build(self) -> tuple[PatternMemoryRecord, ...]:
        signals = self._load_list("storage/signals/signal_history.json")
        opportunities = self._load_list("storage/opportunities/qualified_opportunities.json")
        confluence = self._load_list("storage/confluence/confluence_results.json")
        lifecycles = self._load_list("storage/trade_lifecycle/lifecycle_records.json")
        signal_by_id = {self._opportunity_id(item): item for item in signals}
        opportunity_by_id = {str(item.get("opportunity_id")): item for item in opportunities}
        confluence_by_id = {str(item.get("opportunity_id")): item for item in confluence}
        rows = lifecycles or opportunities or signals
        records = []
        for index, row in enumerate(rows, start=1):
            opportunity_id = str(row.get("opportunity_id") or self._opportunity_id(row))
            signal = signal_by_id.get(opportunity_id, {})
            opportunity = opportunity_by_id.get(opportunity_id, {})
            confluence_row = confluence_by_id.get(opportunity_id, {})
            records.append(
                self._record_from_sources(
                    index,
                    opportunity_id,
                    row,
                    signal,
                    opportunity,
                    confluence_row,
                )
            )
        return tuple(records)

    def _record_from_sources(
        self,
        index: int,
        opportunity_id: str,
        row: dict[str, Any],
        signal: dict[str, Any],
        opportunity: dict[str, Any],
        confluence: dict[str, Any],
    ) -> PatternMemoryRecord:
        session = self._session(signal, confluence)
        direction = self._direction(signal, row, opportunity)
        structure = signal.get("structure", {}) if isinstance(signal, dict) else {}
        cisd = signal.get("cisd", {}) if isinstance(signal, dict) else {}
        fvg = signal.get("fvg") if isinstance(signal, dict) else None
        ifvg = signal.get("ifvg") if isinstance(signal, dict) else None
        liquidity = signal.get("liquidity", {}) if isinstance(signal, dict) else {}
        outcome = row.get("outcome", {}) if isinstance(row.get("outcome"), dict) else {}
        return PatternMemoryRecord(
            pattern_id=f"pattern-memory-{index:04d}",
            asset=str(row.get("asset") or signal.get("asset") or "غير متاح"),
            session=session,
            direction=direction,
            structure_state=str(structure.get("state") or "هيكل غير محدد"),
            cisd_state=self._cisd_state(cisd),
            fvg_state=self._gap_state(fvg, "FVG غير موجود"),
            ifvg_state=self._gap_state(ifvg, "IFVG غير موجود"),
            liquidity_state=str(
                liquidity.get("sweep_direction")
                or self._factor_state(opportunity, "liquidity")
            ),
            confluence_score=self._score(
                row.get("confluence_score"),
                confluence.get("confluence_score"),
            ),
            timeframe_alignment=self._score(
                row.get("timeframe_score"),
                confluence.get("timeframe_score"),
            ),
            opportunity_score=self._score(
                row.get("qualification_score"),
                opportunity.get("qualification_score"),
            ),
            confidence_score=self._score(
                row.get("confidence"),
                self._nested_score(signal.get("confidence")),
                opportunity.get("confidence"),
            ),
            lifecycle_result=str(
                outcome.get("outcome")
                or row.get("state", {}).get("current")
                or "محايد"
            ),
            performance_result=str(outcome.get("evaluation_reason") or "نتيجة بحثية محايدة"),
            timestamp=str(row.get("created_at") or row.get("timestamp") or signal.get("timestamp")),
            metadata={
                "opportunity_id": opportunity_id,
                "research_only": True,
                "not_execution": True,
            },
        )

    def _load_list(self, relative_path: str) -> list[dict[str, Any]]:
        path = self.project_root / relative_path
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]

    def _opportunity_id(self, row: dict[str, Any]) -> str:
        return f"{row.get('asset', 'UNKNOWN')}:{row.get('timestamp', '')}"

    def _session(self, signal: dict[str, Any], confluence: dict[str, Any]) -> str:
        session = signal.get("session", {}) if isinstance(signal, dict) else {}
        return str(
            session.get("session_name")
            or confluence.get("confluence", {}).get("session")
            or "جلسة غير محددة"
        )

    def _direction(
        self,
        signal: dict[str, Any],
        row: dict[str, Any],
        opportunity: dict[str, Any],
    ) -> str:
        cisd = signal.get("cisd", {}) if isinstance(signal, dict) else {}
        return str(
            cisd.get("direction")
            or signal.get("classification_ar")
            or row.get("classification")
            or opportunity.get("classification")
            or "اتجاه غير محدد"
        )

    def _cisd_state(self, cisd: Any) -> str:
        if not isinstance(cisd, dict):
            return "CISD غير موجود"
        state = "مؤكد" if cisd.get("validated") else "غير مؤكد"
        return f"CISD {cisd.get('direction', '')} {state}".strip()

    def _gap_state(self, value: Any, missing: str) -> str:
        if not isinstance(value, dict):
            return missing
        direction = value.get("direction") or value.get("gap_direction") or "موجود"
        return f"{direction}"

    def _factor_state(self, row: dict[str, Any], name: str) -> str:
        factors = row.get("supporting_factors", []) + row.get("rejection_factors", [])
        match = next((item for item in factors if name.upper() in str(item).upper()), None)
        return str(match or "حالة غير محددة")

    def _nested_score(self, value: Any) -> float:
        if isinstance(value, dict):
            return self._score(value.get("score"))
        return self._score(value)

    def _score(self, *values: Any) -> float:
        for value in values:
            try:
                return round(max(0.0, min(100.0, float(value))), 2)
            except (TypeError, ValueError):
                continue
        return 0.0
