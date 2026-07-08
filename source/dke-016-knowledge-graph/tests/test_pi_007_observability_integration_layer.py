import pytest

from platform_integration import (
    EnterpriseApiGateway,
    HealthCheckError,
    InvalidLogLevelError,
    MetricRegistrationError,
    ObservabilityEventError,
    ObservabilityIntegrationLayer,
    PersistenceIntegrationLayer,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeComponentMetadata,
    TraceValidationError,
    UnifiedPlatformRuntimeRegistry,
)


class EchoComponent:
    def execute(self, payload):
        return payload


class FakeDHMF:
    pass


def test_logging_validation():
    layer = ObservabilityIntegrationLayer()
    event = layer.log_event("info", "platform started", {"component": "PI"})
    assert event.level == "INFO"
    assert event.event_id == "event-000001"
    assert event.context == {"component": "PI"}


def test_invalid_level_rejected():
    layer = ObservabilityIntegrationLayer()
    with pytest.raises(InvalidLogLevelError, match="invalid log level"):
        layer.log_event("verbose", "bad")


def test_malformed_event_rejected():
    layer = ObservabilityIntegrationLayer()
    with pytest.raises(ObservabilityEventError, match="message is required"):
        layer.log_event("INFO", "")
    with pytest.raises(ObservabilityEventError, match="context must be a mapping"):
        layer.log_event("INFO", "bad", ["not", "mapping"])


def test_metric_registration():
    layer = ObservabilityIntegrationLayer()
    metric = layer.register_metric("requests", {"metric_type": "counter", "description": "Request count"})
    assert metric.definition.name == "requests"
    assert metric.definition.metric_type == "counter"


def test_duplicate_metric_rejected():
    layer = ObservabilityIntegrationLayer()
    layer.register_metric("requests", {"metric_type": "counter"})
    with pytest.raises(MetricRegistrationError, match="already registered"):
        layer.register_metric("requests", {"metric_type": "counter"})


def test_metric_recording():
    layer = ObservabilityIntegrationLayer()
    layer.register_metric("latency", {"metric_type": "gauge", "unit": "ms"})
    metric = layer.record_metric("latency", 12.5)
    assert metric.values == (12.5,)
    assert layer.get_metric("latency").snapshot()["latest"] == 12.5


def test_trace_lifecycle():
    layer = ObservabilityIntegrationLayer()
    trace = layer.start_trace({"request": "r1"})
    assert trace.trace_id == "trace-000001"
    ended = layer.end_trace(trace.trace_id)
    assert ended.status == "ended"
    assert ended.ended_at == "1970-01-01T00:00:00Z"


def test_malformed_trace_rejected():
    layer = ObservabilityIntegrationLayer()
    with pytest.raises(TraceValidationError, match="invalid trace id"):
        layer.end_trace("bad")
    trace = layer.start_trace()
    layer.end_trace(trace.trace_id)
    with pytest.raises(TraceValidationError, match="already ended"):
        layer.end_trace(trace.trace_id)


def test_health_check_registration():
    layer = ObservabilityIntegrationLayer()
    layer.register_health_check("DKE", lambda: {"status": "healthy", "details": "ok"})
    result = layer.run_health_checks("DKE")
    assert result["status"] == "healthy"
    assert result["components"]["DKE"]["details"] == "ok"


def test_unknown_health_check_rejected():
    layer = ObservabilityIntegrationLayer()
    with pytest.raises(HealthCheckError, match="unknown health check component"):
        layer.run_health_checks("DIE")


def test_health_execution_detects_degraded():
    layer = ObservabilityIntegrationLayer()
    layer.register_health_check("DKE", lambda: {"status": "healthy"})
    layer.register_health_check("DIE", lambda: {"status": "degraded"})
    result = layer.run_health_checks()
    assert result["status"] == "degraded"
    assert result["component_count"] == 2


def test_audit_event_forwarding():
    layer = ObservabilityIntegrationLayer()
    event = layer.forward_audit_event("decision approved", {"decision_id": "d1"})
    assert event.event_type == "audit"
    assert event.level == "INFO"


def test_snapshot_export_is_deterministic():
    layer = ObservabilityIntegrationLayer()
    layer.log_event("INFO", "ready")
    layer.register_metric("requests", {"metric_type": "counter"})
    layer.record_metric("requests", 1)
    trace = layer.start_trace()
    layer.end_trace(trace.trace_id)
    first = layer.export_observability_snapshot()
    second = layer.export_observability_snapshot()
    assert first == second
    assert first["module"] == "PI-007"
    assert first["metrics"]["metric_count"] == 1
    assert first["traces"]["trace_count"] == 1


def test_integration_with_pi_001_pi_002_pi_004_pi_006_and_dhmf():
    platform = PlatformIntegrationLayer()
    platform.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))

    runtime = UnifiedPlatformRuntimeRegistry()
    runtime.register_runtime_component(RuntimeComponentMetadata("PI-007", "Observability", "platform_integration"))

    gateway = EnterpriseApiGateway(platform_layer=platform)
    persistence = PersistenceIntegrationLayer()
    layer = ObservabilityIntegrationLayer(
        platform_layer=platform,
        runtime_registry=runtime,
        api_gateway=gateway,
        persistence_layer=persistence,
        dhmf_monitoring_component=FakeDHMF(),
    )
    health = layer.run_health_checks()
    assert health["status"] == "healthy"
    assert set(health["components"]) == {"DHMF", "PI-001", "PI-002", "PI-004", "PI-006"}
    snapshot = layer.export_observability_snapshot()
    assert snapshot["integrations"] == {
        "api_gateway": True,
        "dhmf_monitoring_component": True,
        "persistence_layer": True,
        "platform_layer": True,
        "runtime_registry": True,
    }
