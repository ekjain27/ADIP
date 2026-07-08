import pytest

from platform_integration import (
    ComponentNotFoundError,
    ComponentRegistrationError,
    ContractValidationError,
    InvalidExecutionRequestError,
    PlatformContract,
    PlatformIntegrationLayer,
    create_default_platform_integration_layer,
    default_platform_contracts,
)


class EchoComponent:
    def execute(self, payload):
        return {"echo": payload}


class AddStageComponent:
    def __init__(self, stage):
        self.stage = stage

    def execute(self, payload):
        stages = tuple(payload.get("stages", ()))
        return {"stages": (*stages, self.stage)}


class InvalidComponent:
    pass


def test_successful_registration():
    layer = PlatformIntegrationLayer()
    contract = PlatformContract("DIE", "decision_intelligence", "execute")
    result = layer.register_component("DIE", EchoComponent(), contract)
    assert result.status == "registered"
    assert result.component_name == "DIE"
    assert layer.list_components() == ("DIE",)


def test_duplicate_registration_rejected():
    layer = _layer_with_echo("DIE")
    with pytest.raises(ComponentRegistrationError, match="already registered"):
        layer.register_component("DIE", EchoComponent(), PlatformContract("DIE", "decision_intelligence", "execute"))


def test_missing_component_lookup_rejected():
    layer = PlatformIntegrationLayer()
    with pytest.raises(ComponentNotFoundError, match="not registered"):
        layer.get_component("DKE")


def test_platform_validation():
    layer = _layer_with_echo("DKE")
    validation = layer.validate_platform(required_components=("DKE",))
    assert validation["status"] == "valid"
    assert validation["module"] == "PI-001"
    assert validation["components"] == ("DKE",)


def test_platform_validation_rejects_missing_required_component():
    layer = _layer_with_echo("DKE")
    with pytest.raises(ComponentNotFoundError, match="missing platform component"):
        layer.validate_platform(required_components=("DKE", "DIE"))


def test_contract_validation_rejects_incompatible_component():
    layer = PlatformIntegrationLayer()
    with pytest.raises(ContractValidationError, match="missing callable method"):
        layer.register_component("DIE", InvalidComponent(), PlatformContract("DIE", "decision_intelligence", "execute"))


def test_single_component_execution():
    layer = _layer_with_echo("DIE")
    payload = {"decision": "approve"}
    result = layer.execute_component("DIE", payload)
    assert result.status == "success"
    assert result.component_name == "DIE"
    assert result.input_payload == payload
    assert result.output_payload == {"echo": payload}
    assert result.errors == ()
    assert result.validation_metadata["module"] == "PI-001"


def test_invalid_execution_request_rejected():
    layer = _layer_with_echo("DIE")
    with pytest.raises(InvalidExecutionRequestError, match="payload is required"):
        layer.execute_component("DIE", None)
    with pytest.raises(InvalidExecutionRequestError, match="pipeline sequence is required"):
        layer.execute_pipeline((), {"ok": True})


def test_multi_component_pipeline_execution():
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", AddStageComponent("DKE"), PlatformContract("DKE", "knowledge_extraction", "execute"))
    layer.register_component("DIE", AddStageComponent("DIE"), PlatformContract("DIE", "decision_intelligence", "execute"))
    result = layer.execute_pipeline(("DKE", "DIE"), {"stages": ()})
    assert result.status == "success"
    assert result.component_name == "PIPELINE"
    assert result.output_payload == {"stages": ("DKE", "DIE")}
    assert result.validation_metadata["sequence"] == ("DKE", "DIE")
    assert result.validation_metadata["step_count"] == 2


def test_deterministic_output():
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", AddStageComponent("DKE"), PlatformContract("DKE", "knowledge_extraction", "execute"))
    payload = {"stages": ()}
    first = layer.execute_component("DKE", payload).to_dict()
    second = layer.execute_component("DKE", payload).to_dict()
    assert first == second


def test_default_contracts_cover_required_platform_boundaries():
    contracts = default_platform_contracts()
    assert tuple(sorted(contracts)) == ("ADBM", "ADWG", "DDGM", "DHMF", "DIE", "DKE", "DPG", "DRIF", "EDOF", "TDLL")
    assert contracts["DKE"].component_type == "knowledge_extraction"
    assert contracts["EDOF"].execution_method == "orchestrate"


def test_default_platform_registration_is_backward_compatible():
    layer = create_default_platform_integration_layer()
    assert layer.list_components() == ("ADBM", "ADWG", "DDGM", "DHMF", "DIE", "DKE", "DPG", "DRIF", "EDOF", "TDLL")
    validation = layer.validate_platform(required_components=layer.list_components())
    assert validation["status"] == "valid"


def _layer_with_echo(name):
    layer = PlatformIntegrationLayer()
    layer.register_component(name, EchoComponent(), PlatformContract(name, "test_component", "execute"))
    return layer
