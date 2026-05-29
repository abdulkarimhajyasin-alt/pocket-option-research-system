"""Chart dataset builders for the local dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChartDataset:
    """Framework-neutral chart data for Jinja and JSON APIs."""

    chart_type: str
    title: str
    labels: list[str]
    series: list[dict[str, Any]]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable chart payload."""
        return {
            "chart_type": self.chart_type,
            "title": self.title,
            "labels": self.labels,
            "series": self.series,
            "summary": self.summary,
        }


def line_chart(
    title: str,
    labels: list[str],
    values: list[float],
    *,
    label: str,
    color: str = "accent",
) -> ChartDataset:
    """Build a line chart payload."""
    return ChartDataset(
        chart_type="line",
        title=title,
        labels=labels,
        series=[{"label": label, "values": values, "color": color}],
        summary=_numeric_summary(values),
    )


def bar_chart(
    title: str,
    labels: list[str],
    values: list[float],
    *,
    label: str,
    color: str = "accent",
) -> ChartDataset:
    """Build a bar chart payload."""
    return ChartDataset(
        chart_type="bar",
        title=title,
        labels=labels,
        series=[{"label": label, "values": values, "color": color}],
        summary=_numeric_summary(values),
    )


def multi_line_chart(
    title: str,
    labels: list[str],
    series: list[dict[str, Any]],
) -> ChartDataset:
    """Build a multi-series line chart payload."""
    all_values: list[float] = []
    normalized = []
    for item in series:
        values = [_to_float(value) for value in item.get("values", [])]
        all_values.extend(values)
        normalized.append({**item, "values": values})
    return ChartDataset(
        chart_type="line",
        title=title,
        labels=labels,
        series=normalized,
        summary=_numeric_summary(all_values),
    )


def empty_chart(title: str, chart_type: str = "line") -> ChartDataset:
    """Return a harmless empty chart."""
    return ChartDataset(chart_type=chart_type, title=title, labels=[], series=[], summary={})


def _numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {}
    return {
        "minimum": min(values),
        "maximum": max(values),
        "latest": values[-1],
        "count": len(values),
    }


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
