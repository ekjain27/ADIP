import pytest

from platform_integration import (
    ContractAdapterCompatibilityError,
    ContractAdapterNotFoundError,
    ContractAdapterRegistrationError,
    ContractAdapterRegistry,
    ContractAdapterValidationError,
    CrossEngineContractAdapter,
    PayloadContract,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeComponentMetadata,
    UnifiedPlatformRuntimeRegistry,
)


class EchoComponent:
    def execute(self, payload):
        return payload


def test_adapter_registration():
    registry = ContractAdapterRegistry()
    adapter = _dke_to_die_adapter()
    result = registry.register_adapter("DKE", "DIE", adapter)
    assert result == adapter
    assert registry.list_adapters() == (("DKE", "DIE"),)


def test_duplicate_adapter_rejected():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    with pytest.raises(ContractAdapterRegistrationError, match="already registered"):
        registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())


def test_missing_adapter_rejected():
    registry = ContractAdapterRegistry()
    with pytest.raises(ContractAdapterNotFoundError, match="not registered"):
        registry.get_adapter("DKE", "DIE")


def test_invalid_source_engine_rejected():
    registry = ContractAdapterRegistry()
    with pytest.raises(ContractAdapterValidationError, match="invalid engine id"):
        registry.register_adapter("UNKNOWN", "DIE", _dke_to_die_adapter())


def test_invalid_target_engine_rejected():
    registry = ContractAdapterRegistry()
    with pytest.raises(ContractAdapterValidationError, match="invalid engine id"):
        registry.register_adapter("DKE", "UNKNOWN", _dke_to_die_adapter())


def test_incompatible_adapter_contract_rejected():
    registry = ContractAdapterRegistry()
    with pytest.raises(ContractAdapterCompatibilityError, match="must match registration"):
        registry.register_adapter("DKE", "DIE", CrossEngineContractAdapter("DIE", "DKE"))


def test_deterministic_adaptation():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    payload = {"evidence": [{"id": "e1"}], "query": "Approve vendor"}
    first = registry.adapt_payload("DKE", "DIE", payload).to_dict()
    second = registry.adapt_payload("DKE", "DIE", payload).to_dict()
    assert first == second
    assert first["adapted_payload"] == {
        "metadata": {"source": "DKE"},
        "query": "Approve vendor",
        "semantic_results": [{"id": "e1"}],
    }


def test_adaptation_does_not_mutate_original_payload():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    payload = {"query": "Assess", "evidence": [{"id": "e1", "score": 0.8}]}
    original = {"query": "Assess", "evidence": [{"id": "e1", "score": 0.8}]}
    registry.adapt_payload("DKE", "DIE", payload)
    assert payload == original


def test_invalid_payload_rejected():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    with pytest.raises(ContractAdapterValidationError, match="missing required field"):
        registry.adapt_payload("DKE", "DIE", {"evidence": []})
    with pytest.raises(ContractAdapterValidationError, match="payload must be a mapping"):
        registry.adapt_payload("DKE", "DIE", ["not", "a", "mapping"])


def test_validate_adapter():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    validation = registry.validate_adapter("DKE", "DIE")
    assert validation["module"] == "PI-003"
    assert validation["status"] == "valid"


def test_integration_with_pi_001_platform_layer():
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))
    layer.register_component("DIE", EchoComponent(), PlatformContract("DIE", "decision_intelligence", "execute"))
    registry = ContractAdapterRegistry(platform_layer=layer)
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    assert registry.adapt_payload("DKE", "DIE", {"query": "q", "evidence": ()}).status == "success"
    with pytest.raises(ContractAdapterCompatibilityError, match="PI-001"):
        registry.register_adapter("DKE", "DPG", CrossEngineContractAdapter("DKE", "DPG"))


def test_integration_with_pi_002_runtime_registry():
    runtime_registry = UnifiedPlatformRuntimeRegistry()
    runtime_registry.register_runtime_component(_runtime_component("DKE", "dke"))
    runtime_registry.register_runtime_component(_runtime_component("DIE", "die"))
    registry = ContractAdapterRegistry(runtime_registry=runtime_registry)
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    assert registry.validate_adapter("DKE", "DIE")["status"] == "valid"
    with pytest.raises(ContractAdapterCompatibilityError, match="PI-002"):
        registry.register_adapter("DKE", "DPG", CrossEngineContractAdapter("DKE", "DPG"))


def test_snapshot_export_is_deterministic():
    registry = ContractAdapterRegistry()
    registry.register_adapter("DKE", "DIE", _dke_to_die_adapter())
    first = registry.export_adapter_snapshot()
    second = registry.export_adapter_snapshot()
    assert first == second
    assert first["module"] == "PI-003"
    assert first["adapter_count"] == 1


def _dke_to_die_adapter():
    return CrossEngineContractAdapter(
        "DKE",
        "DIE",
        input_contract=PayloadContract(required_fields=("query",), optional_fields=("evidence",), contract_name="dke_context"),
        output_contract=PayloadContract(
            required_fields=("query", "semantic_results", "metadata"),
            contract_name="die_context",
        ),
        transform=lambda payload: {
            "query": payload["query"],
            "semantic_results": payload.get("evidence", ()),
            "metadata": {"source": "DKE"},
        },
    )


def _runtime_component(module_id, phase):
    return RuntimeComponentMetadata(
        module_id=module_id,
        name=module_id,
        phase=phase,
        capabilities=(module_id.lower(),),
        contracts={"provides": (module_id,)},
    )
