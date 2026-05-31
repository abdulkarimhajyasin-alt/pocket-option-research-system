"""Research archive diff engine."""

from __future__ import annotations

from typing import Any

from app.research_archive.models import ResearchDiff


class ResearchDiffEngine:
    """Compare two local research snapshots."""

    def compare(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> ResearchDiff:
        if not previous or not current:
            return ResearchDiff(
                from_version=previous.get("version") if previous else None,
                to_version=current.get("version") if current else None,
                added_keys=[],
                removed_keys=[],
                changed_values=[],
                improved_metrics=[],
                degraded_metrics=[],
                stable_metrics=[],
                missing_comparison_areas=["insufficient_history"],
                summary_ar=["لا توجد بيانات كافية للمقارنة البحثية."],
            )
        old_flat = self._flatten(previous)
        new_flat = self._flatten(current)
        old_keys = set(old_flat)
        new_keys = set(new_flat)
        added = sorted(new_keys - old_keys)
        removed = sorted(old_keys - new_keys)
        changed = []
        improved = []
        degraded = []
        stable = []
        for key in sorted(old_keys & new_keys):
            old_value = old_flat[key]
            new_value = new_flat[key]
            if old_value == new_value:
                if isinstance(new_value, (int, float)):
                    stable.append(key)
                continue
            changed.append({"key": key, "previous": old_value, "current": new_value})
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                metric = {"key": key, "previous": old_value, "current": new_value}
                if new_value > old_value:
                    improved.append(metric)
                elif new_value < old_value:
                    degraded.append(metric)
                else:
                    stable.append(key)
        return ResearchDiff(
            from_version=previous.get("version"),
            to_version=current.get("version"),
            added_keys=added,
            removed_keys=removed,
            changed_values=changed[:100],
            improved_metrics=improved[:100],
            degraded_metrics=degraded[:100],
            stable_metrics=stable[:100],
            missing_comparison_areas=[],
            summary_ar=self._summary(added, removed, changed, improved, degraded),
        )

    def _summary(
        self,
        added: list[str],
        removed: list[str],
        changed: list[dict[str, Any]],
        improved: list[dict[str, Any]],
        degraded: list[dict[str, Any]],
    ) -> list[str]:
        return [
            f"المفاتيح المضافة: {len(added)}",
            f"المفاتيح المحذوفة: {len(removed)}",
            f"القيم المتغيرة: {len(changed)}",
            f"المقاييس المحسنة: {len(improved)}",
            f"المقاييس المتراجعة: {len(degraded)}",
        ]

    def _flatten(self, payload: Any, prefix: str = "") -> dict[str, Any]:
        if isinstance(payload, dict):
            flattened: dict[str, Any] = {}
            for key, value in payload.items():
                next_key = f"{prefix}.{key}" if prefix else str(key)
                flattened.update(self._flatten(value, next_key))
            return flattened
        if isinstance(payload, list):
            return {f"{prefix}.__len__": len(payload)}
        return {prefix: payload}
