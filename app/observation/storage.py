"""Local JSON storage for read-only observation research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.observation.models import BrokerSnapshot


class ObservationStorage:
    """Write local observation snapshots for research review."""

    def __init__(self, output_dir: Path | str = "storage/observations") -> None:
        self.output_dir = Path(output_dir)

    def save_snapshot(self, snapshot: BrokerSnapshot) -> dict[str, str]:
        """Store normalized observation JSON files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "broker_snapshot": self.output_dir / "broker_snapshot.json",
            "asset_observations": self.output_dir / "asset_observations.json",
            "payout_observations": self.output_dir / "payout_observations.json",
            "session_observations": self.output_dir / "session_observations.json",
        }
        self._write(paths["broker_snapshot"], snapshot.to_dict())
        self._write(
            paths["asset_observations"],
            [item.to_dict() for item in snapshot.assets],
        )
        self._write(
            paths["payout_observations"],
            [item.to_dict() for item in snapshot.payouts],
        )
        self._write(
            paths["session_observations"],
            [item.to_dict() for item in snapshot.sessions],
        )
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


class ObservationReportWriter:
    """Write dashboard-consumable reports under reports/observation."""

    def __init__(self, output_dir: Path | str = "reports/observation") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        """Export summary and chart source reports."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "observation_summary.json",
            "asset_activity": self.output_dir / "asset_activity.json",
            "payout_distribution": self.output_dir / "payout_distribution.json",
            "session_activity": self.output_dir / "session_activity.json",
        }
        self._write(paths["summary"], analytics)
        self._write(paths["asset_activity"], analytics.get("asset_activity", {}))
        self._write(paths["payout_distribution"], analytics.get("payout_distribution", {}))
        self._write(paths["session_activity"], analytics.get("session_activity", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
