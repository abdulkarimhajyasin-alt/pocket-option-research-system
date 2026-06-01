"""Storage writer for trading architecture program outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TradingArchitectureProgramStorage:
    """Persist program foundation artifacts."""

    def __init__(self, output_dir: Path | str = "storage/trading_architecture_program") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "registry": "program_registry.json",
            "domains": "domains.json",
            "gates": "gates.json",
            "workstreams": "workstreams.json",
            "diagnostics": "diagnostics.json",
            "recommendations": "recommendations.json",
        }
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
