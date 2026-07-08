import pytest

from platform_integration import (
    ApiRequestValidationError,
    ApiRouteNotFoundError,
    ApiRouteRegistrationError,
    ApiUnauthorizedActionError,
    ContractAdapterRegistry,
    CrossEngineContractAdapter,
    EnterpriseApiGateway,
    PayloadContract,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeComponentMetadata,
    UnifiedPlatformRuntimeRegistry,
)


class EchoComponent:
    def execute(self, payload):
        return {"echo": payload}


def test_route_registration():
    gateway = EnterpriseApiGateway()
    route = gateway.register_route("/custom/status", "GET", lambda request: {"ok": True})
    assert route.path == "/custom/status"
    assert route.method == "GET"
    assert any(item["path"] == "/custom/status" for item in gateway.list_routes())


def test_duplicate_route_rejected():
    gateway = EnterpriseApiGateway()
    with pytest.raises(ApiRouteRegistrationError, match="already registered"):
        gateway.register_route("/platform/components", "GET", lambda request: {})


def test_missing_route_rejected():
    gateway = EnterpriseApiGateway()
    with pytest.raises(ApiRouteNotFoundError, match="not registered"):
        gateway.handle_request("/missing", "GET")


def test_invalid_method_rejected():
    gateway = EnterpriseApiGateway()
    with pytest.raises(ApiRequestValidationError, match="invalid gateway method"):
        gateway.handle_request("/platform/components", "PATCH")


def test_malformed_payload_rejected():
    gateway = EnterpriseApiGateway()
    with pytest.raises(ApiRequestValidationError, match="payload must be a mapping"):
        gateway.handle_request("/platform/components", "GET", ["bad"])
    with pytest.raises(ApiRequestValidationError, match="missing required field"):
        gateway.handle_request("/platform/execute", "POST", {"component": "DKE"})


def test_unauthorized_internal_action_placeholder_rejected():
    gateway = EnterpriseApiGateway()
    with pytest.raises(ApiUnauthorizedActionError, match="unauthorized internal action"):
        gateway.validate_request("/platform/components", "GET", {}, action="external_network")


def test_response_normalization_and_deterministic_output():
    gateway = EnterpriseApiGateway()
    gateway.register_route("/custom/sort", "GET", lambda request: {"z": 2, "a": 1})
    first = gateway.handle_request("/custom/sort", "GET").to_dict()
    second = gateway.handle_request("/custom/sort", "GET").to_dict()
    assert first == second
    assert first["payload"] == {"a": 1, "z": 2}
    assert first["validation_metadata"]["module"] == "PI-004"


def test_deterministic_error_envelope_for_handler_failure():
    gateway = EnterpriseApiGateway()
    gateway.register_route("/custom/fail", "GET", lambda request: (_ for _ in ()).throw(ValueError("boom")))
    response = gateway.handle_request("/custom/fail", "GET")
    assert response.status == "error"
    assert response.payload is None
    assert response.errors == ("boom",)


def test_route_request_into_pi_001_platform_layer():
    gateway = EnterpriseApiGateway(platform_layer=_platform_layer())
    response = gateway.handle_request("/platform/components", "GET")
    assert response.status == "success"
    assert response.payload == {"components": ("DKE",)}

    executed = gateway.handle_request("/platform/execute", "POST", {"component": "DKE", "payload": {"query": "q"}})
    assert executed.status == "success"
    assert executed.payload["output_payload"] == {"echo": {"query": "q"}}


def test_route_request_into_pi_002_runtime_registry():
    gateway = EnterpriseApiGateway(runtime_registry=_runtime_registry())
    response = gateway.handle_request("/runtime/snapshot", "GET")
    assert response.status == "success"
    assert response.payload["module"] == "PI-002"
    assert response.payload["component_count"] == 1


def test_route_request_into_pi_003_adapter_registry():
    gateway = EnterpriseApiGateway(adapter_registry=_adapter_registry())
    snapshot = gateway.handle_request("/adapters", "GET")
    assert snapshot.status == "success"
    assert snapshot.payload["adapter_count"] == 1

    adapted = gateway.handle_request(
        "/adapters/adapt",
        "POST",
        {"source": "DKE", "target": "DIE", "payload": {"query": "q", "evidence": ("e1",)}},
    )
    assert adapted.status == "success"
    assert adapted.payload["adapted_payload"] == {
        "metadata": {"source": "DKE"},
        "query": "q",
        "semantic_results": ("e1",),
    }


def test_gateway_snapshot_is_deterministic():
    gateway = EnterpriseApiGateway(
        platform_layer=_platform_layer(),
        runtime_registry=_runtime_registry(),
        adapter_registry=_adapter_registry(),
    )
    first = gateway.export_gateway_snapshot()
    second = gateway.export_gateway_snapshot()
    assert first == second
    assert first["module"] == "PI-004"
    assert first["route_count"] == 5
    assert first["integrations"] == {
        "adapter_registry": True,
        "platform_layer": True,
        "runtime_registry": True,
    }


def _platform_layer():
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))
    return layer


def _runtime_registry():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(
        RuntimeComponentMetadata(
            module_id="PI-004",
            name="Enterprise API Gateway",
            phase="platform_integration",
            capabilities=("gateway",),
        )
    )
    return registry


def _adapter_registry():
    registry = ContractAdapterRegistry()
    registry.register_adapter(
        "DKE",
        "DIE",
        CrossEngineContractAdapter(
            "DKE",
            "DIE",
            input_contract=PayloadContract(required_fields=("query",), optional_fields=("evidence",)),
            output_contract=PayloadContract(required_fields=("query", "semantic_results", "metadata")),
            transform=lambda payload: {
                "query": payload["query"],
                "semantic_results": payload.get("evidence", ()),
                "metadata": {"source": "DKE"},
            },
        ),
    )
    return registry
