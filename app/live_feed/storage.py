"""Local storage and reports for live feed research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.live_feed.models import FeedSnapshot


class LiveFeedStorage:
    """Store latest feed state under storage/live_feed."""

    def __init__(self, output_dir: Path | str = "storage/live_feed") -> None:
        self.output_dir = Path(output_dir)

    def save(self, snapshot: FeedSnapshot, analytics: dict[str, Any]) -> dict[str, str]:
        """Write latest snapshot, health, and metrics."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "snapshot": self.output_dir / "latest_feed_snapshot.json",
            "health": self.output_dir / "feed_health.json",
            "metrics": self.output_dir / "feed_metrics.json",
        }
        self._write(paths["snapshot"], snapshot.to_dict())
        self._write(paths["health"], analytics.get("health", {}))
        self._write(paths["metrics"], analytics.get("summary", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


class LiveFeedReportWriter:
    """Write dashboard-consumable live feed reports."""

    def __init__(self, output_dir: Path | str = "reports/live_feed") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        """Export feed summary, health, latency, and activity reports."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "feed_summary.json",
            "health": self.output_dir / "feed_health.json",
            "latency": self.output_dir / "feed_latency.json",
            "activity": self.output_dir / "feed_activity.json",
        }
        self._write(paths["summary"], analytics.get("summary", {}))
        self._write(paths["health"], analytics.get("health", {}))
        self._write(paths["latency"], analytics.get("latency", []))
        self._write(
            paths["activity"],
            {
                "activity": analytics.get("activity", {}),
                "frequency": analytics.get("frequency", {}),
                "session_activity": analytics.get("session_activity", {}),
                "health_timeline": analytics.get("health_timeline", {}),
            },
        )
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
