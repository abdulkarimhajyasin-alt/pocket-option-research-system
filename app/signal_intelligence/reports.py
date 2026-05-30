"""Report generation for signal intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SignalReportWriter:
    """Write deterministic signal intelligence reports."""

    def __init__(self, output_dir: Path | str = "reports/signals") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "signal_summary.json",
            "quality": self.output_dir / "signal_quality.json",
            "confidence": self.output_dir / "signal_confidence.json",
            "distribution": self.output_dir / "signal_distribution.json",
            "structure": self.output_dir / "structure_analysis.json",
            "fvg": self.output_dir / "fvg_analysis.json",
            "cisd": self.output_dir / "cisd_analysis.json",
            "liquidity": self.output_dir / "liquidity_analysis.json",
        }
        self._write(
            paths["summary"],
            {
                **analytics.get("summary", {}),
                "best_signal": analytics.get("best_signal", {}),
            },
        )
        self._write(
            paths["quality"],
            {"session_performance": analytics.get("session_performance", {})},
        )
        self._write(paths["confidence"], analytics.get("confidence_distribution", {}))
        self._write(paths["distribution"], analytics.get("distribution", {}))
        self._write(paths["structure"], analytics.get("structure_distribution", {}))
        self._write(paths["fvg"], analytics.get("fvg_statistics", {}))
        self._write(paths["cisd"], analytics.get("cisd_statistics", {}))
        self._write(paths["liquidity"], analytics.get("liquidity_statistics", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
