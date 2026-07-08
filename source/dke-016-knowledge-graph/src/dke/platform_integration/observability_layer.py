from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .api_gateway import EnterpriseApiGateway
from .health_registry import HealthRegistry
from .metrics_registry import MetricDefinition, MetricRecord, MetricsRegistry
from .observability_errors import InvalidLogLevelError, ObservabilityEventError
from .persistence_layer import PersistenceIntegrationLayer
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry
from .trace_manager import DETERMINISTIC_TRACE_TIMESTAMP, TraceManager, TraceRecord


VALID_LOG_LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass(frozen=True)
class ObservabilityEvent:
    event_id: str
    event_type: str
    level: str
    message: str
    context: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = DETERMINISTIC_TRACE_TIMESTAMP

    def snapshot(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "level": self.level,
            "message": self.message,
            "context": dict(sorted(self.context.items())),
            "timestamp": self.timestamp,
        }


class ObservabilityIntegrationLayer:
    MODULE = "PI-007"

    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
        api_gateway: EnterpriseApiGateway | None = None,
        persistence_layer: PersistenceIntegrationLayer | None = None,
        dhmf_monitoring_component: Any | None = None,
    ) -> None:
        self.platform_layer = platform_layer
        self.runtime_registry = runtime_registry
        self.api_gateway = api_gateway
        self.persistence_layer = persistence_layer
        self.dhmf_monitoring_component = dhmf_monitoring_component
        self.metrics = MetricsRegistry()
        self.traces = TraceManager()
        self.health = HealthRegistry()
        self._events: list[ObservabilityEvent] = []
        self._event_counter = 0
        self._register_default_health_checks()

    def log_event(self, level: str, message: str, context: Mapping[str, Any] | None = None) -> ObservabilityEvent:
        normalized_level = self._validate_level(level)
        if not isinstance(message, str) or not message.strip():
            raise ObservabilityEventError("observability message is required")
        if context is not None and not isinstance(context, Mapping):
            raise ObservabilityEventError("observability context must be a mapping")
        return self._record_event("log", normalized_level, message.strip(), context or {})

    def forward_audit_event(self, message: str, context: Mapping[str, Any] | None = None) -> ObservabilityEvent:
        return self._record_event("audit", "INFO", message, context or {})

    def register_metric(self, name: str, definition: MetricDefinition | Mapping[str, Any]) -> MetricRecord:
        return self.metrics.register_metric(name, definition)

    def record_metric(self, name: str, value: int | float) -> MetricRecord:
        return self.metrics.record_metric(name, value)

    def get_metric(self, name: str) -> MetricRecord:
        return self.metrics.get_metric(name)

    def start_trace(self, context: Mapping[str, Any] | None = None) -> TraceRecord:
        trace = self.traces.start_trace(context)
        self._record_event("trace", "DEBUG", "trace started", {"trace_id": trace.trace_id})
        return trace

    def end_trace(self, trace_id: str) -> TraceRecord:
        trace = self.traces.end_trace(trace_id)
        self._record_event("trace", "DEBUG", "trace ended", {"trace_id": trace.trace_id})
        return trace

    def register_health_check(self, component: str, callback) -> None:
        self.health.register_health_check(component, callback)

    def run_health_checks(self, component: str | None = None) -> dict[str, Any]:
        return self.health.run_health_checks(component)

    def export_observability_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "event_count": len(self._events),
            "events": tuple(event.snapshot() for event in self._events),
            "metrics": self.metrics.snapshot(),
            "traces": self.traces.snapshot(),
            "health": self.health.snapshot(),
            "integrations": {
                "platform_layer": self.platform_layer is not None,
                "runtime_registry": self.runtime_registry is not None,
                "api_gateway": self.api_gateway is not None,
                "persistence_layer": self.persistence_layer is not None,
                "dhmf_monitoring_component": self.dhmf_monitoring_component is not None,
            },
        }

    def _record_event(self, event_type: str, level: str, message: str, context: Mapping[str, Any]) -> ObservabilityEvent:
        if not isinstance(context, Mapping):
            raise ObservabilityEventError("observability context must be a mapping")
        self._event_counter += 1
        event = ObservabilityEvent(
            event_id=f"event-{self._event_counter:06d}",
            event_type=event_type,
            level=level,
            message=message,
            context=dict(context),
        )
        self._events.append(event)
        return event

    def _validate_level(self, level: str) -> str:
        if not isinstance(level, str) or not level.strip():
            raise InvalidLogLevelError("log level is required")
        normalized = level.strip().upper()
        if normalized not in VALID_LOG_LEVELS:
            raise InvalidLogLevelError(f"invalid log level: {normalized}")
        return normalized

    def _register_default_health_checks(self) -> None:
        if self.platform_layer is not None:
            self.register_health_check("PI-001", lambda: {"status": "healthy", "components": len(self.platform_layer.list_components())})
        if self.runtime_registry is not None:
            self.register_health_check("PI-002", lambda: {"status": "healthy", "components": len(self.runtime_registry.list_runtime_components())})
        if self.api_gateway is not None:
            self.register_health_check("PI-004", lambda: {"status": "healthy", "routes": len(self.api_gateway.list_routes())})
        if self.persistence_layer is not None:
            self.register_health_check("PI-006", lambda: {"status": "healthy", "records": len(self.persistence_layer.list_records())})
        if self.dhmf_monitoring_component is not None:
            self.register_health_check("DHMF", lambda: {"status": "healthy", "component": self.dhmf_monitoring_component.__class__.__name__})


def create_observability_layer(
    platform_layer: PlatformIntegrationLayer | None = None,
    runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    api_gateway: EnterpriseApiGateway | None = None,
    persistence_layer: PersistenceIntegrationLayer | None = None,
    dhmf_monitoring_component: Any | None = None,
) -> ObservabilityIntegrationLayer:
    return ObservabilityIntegrationLayer(
        platform_layer=platform_layer,
        runtime_registry=runtime_registry,
        api_gateway=api_gateway,
        persistence_layer=persistence_layer,
        dhmf_monitoring_component=dhmf_monitoring_component,
    )
