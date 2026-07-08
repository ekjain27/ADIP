from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from .observability_errors import MetricNotFoundError, MetricRegistrationError


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    metric_type: str = "gauge"
    description: str = ""
    unit: str = "count"

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise MetricRegistrationError("metric name is required")
        if self.metric_type not in {"counter", "gauge", "histogram"}:
            raise MetricRegistrationError(f"invalid metric type: {self.metric_type}")
        object.__setattr__(self, "name", self.name.strip())

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "metric_type": self.metric_type,
            "description": self.description,
            "unit": self.unit,
        }


@dataclass(frozen=True)
class MetricRecord:
    definition: MetricDefinition
    values: tuple[float, ...] = field(default_factory=tuple)

    def record(self, value: int | float) -> "MetricRecord":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise MetricRegistrationError("metric value must be numeric")
        return replace(self, values=(*self.values, float(value)))

    def snapshot(self) -> dict[str, Any]:
        return {
            "definition": self.definition.metadata(),
            "values": self.values,
            "count": len(self.values),
            "latest": self.values[-1] if self.values else None,
        }


class MetricsRegistry:
    def __init__(self) -> None:
        self._metrics: dict[str, MetricRecord] = {}

    def register_metric(self, name: str, definition: MetricDefinition | Mapping[str, Any]) -> MetricRecord:
        metric_definition = definition if isinstance(definition, MetricDefinition) else MetricDefinition(name=name, **dict(definition))
        if metric_definition.name != name:
            raise MetricRegistrationError("metric definition name must match registration name")
        if name in self._metrics:
            raise MetricRegistrationError(f"metric already registered: {name}")
        record = MetricRecord(metric_definition)
        self._metrics[name] = record
        return record

    def record_metric(self, name: str, value: int | float) -> MetricRecord:
        record = self.get_metric(name)
        updated = record.record(value)
        self._metrics[name] = updated
        return updated

    def get_metric(self, name: str) -> MetricRecord:
        try:
            return self._metrics[name]
        except KeyError as exc:
            raise MetricNotFoundError(f"metric is not registered: {name}") from exc

    def snapshot(self) -> dict[str, Any]:
        return {
            "metric_count": len(self._metrics),
            "metrics": tuple(self._metrics[name].snapshot() for name in sorted(self._metrics)),
        }
