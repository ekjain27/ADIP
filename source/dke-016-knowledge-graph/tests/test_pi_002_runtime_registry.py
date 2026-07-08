import pytest

from platform_integration import (
    FrozenRuntimeComponentError,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeCompatibilityError,
    RuntimeComponentMetadata,
    RuntimeComponentNotFoundError,
    RuntimeComponentRegistrationError,
    RuntimeDependencyError,
    UnifiedPlatformRuntimeRegistry,
    create_runtime_registry_from_platform_layer,
)


class EchoComponent:
    def execute(self, payload):
        return payload


def test_register_runtime_component_tracks_required_metadata():
    registry = UnifiedPlatformRuntimeRegistry()
    component = _component("PI-001", "Platform Integration Layer", "platform_integration", capabilities=("registry",))
    result = registry.register_runtime_component(component)
    assert result.module_id == "PI-001"
    assert result.phase == "platform_integration"
    assert result.capabilities == ("registry",)
    assert result.frozen


def test_duplicate_module_id_rejected():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DIE-020", "Enterprise Orchestrator", "die"))
    with pytest.raises(RuntimeComponentRegistrationError, match="already registered"):
        registry.register_runtime_component(_component("die-020", "Duplicate", "die"))


def test_missing_runtime_component_lookup_rejected():
    registry = UnifiedPlatformRuntimeRegistry()
    with pytest.raises(RuntimeComponentNotFoundError, match="not registered"):
        registry.get_runtime_component("DKE-001")


def test_invalid_phase_rejected():
    with pytest.raises(RuntimeComponentRegistrationError, match="invalid runtime phase"):
        _component("BAD-001", "Bad Phase", "operations")


def test_list_by_phase_is_deterministic():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DIE-020", "Enterprise", "die"))
    registry.register_runtime_component(_component("DIE-001", "Core", "die"))
    registry.register_runtime_component(_component("DKE-020", "Knowledge", "dke"))
    assert tuple(component.module_id for component in registry.list_by_phase("die")) == ("DIE-001", "DIE-020")


def test_list_capabilities_is_deterministic():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DKE-020", "Knowledge", "dke", capabilities=("extract", "graph")))
    registry.register_runtime_component(_component("DIE-020", "Decision", "die", capabilities=("decide",)))
    assert registry.list_capabilities() == {
        "DIE-020": ("decide",),
        "DKE-020": ("extract", "graph"),
    }


def test_dependency_validation_success():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DKE-020", "Knowledge", "dke"))
    registry.register_runtime_component(_component("DIE-020", "Decision", "die", dependencies=("DKE-020",)))
    validation = registry.validate_dependencies()
    assert validation["status"] == "valid"
    assert validation["dependency_count"] == 1


def test_missing_dependency_rejected():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DIE-020", "Decision", "die", dependencies=("DKE-020",)))
    with pytest.raises(RuntimeDependencyError, match="missing runtime dependencies"):
        registry.validate_dependencies()


def test_compatibility_validation_success():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(
        _component("DKE-020", "Knowledge", "dke", contracts={"provides": ("knowledge_context",)})
    )
    registry.register_runtime_component(
        _component(
            "DIE-020",
            "Decision",
            "die",
            dependencies=("DKE-020",),
            contracts={"requires": ("knowledge_context",), "provides": ("enterprise_decision",)},
        )
    )
    assert registry.validate_compatibility()["status"] == "compatible"


def test_incompatible_contract_rejected():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("DKE-020", "Knowledge", "dke", contracts={"provides": ("facts",)}))
    registry.register_runtime_component(
        _component("DIE-020", "Decision", "die", dependencies=("DKE-020",), contracts={"requires": ("knowledge_context",)})
    )
    with pytest.raises(RuntimeCompatibilityError, match="incompatible runtime contracts"):
        registry.validate_compatibility()


def test_frozen_component_update_rejected():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("PI-001", "Platform Integration Layer", "platform_integration", frozen=True))
    with pytest.raises(FrozenRuntimeComponentError, match="frozen"):
        registry.update_runtime_component("PI-001", status="active")


def test_non_frozen_component_update_allowed():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("PI-003", "Future Integration", "platform_integration", frozen=False))
    updated = registry.update_runtime_component("PI-003", status="active", capabilities=("runtime", "future"))
    assert updated.status == "active"
    assert updated.capabilities == ("future", "runtime")


def test_registry_snapshot_is_deterministic():
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(_component("PI-001", "Platform Integration Layer", "platform_integration"))
    first = registry.export_registry_snapshot()
    second = registry.export_registry_snapshot()
    assert first == second
    assert first["module"] == "PI-002"
    assert first["components"][0]["created_at"] == "1970-01-01T00:00:00Z"


def test_runtime_registry_integrates_with_pi_001_layer():
    layer = PlatformIntegrationLayer()
    layer.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))
    layer.register_component("DIE", EchoComponent(), PlatformContract("DIE", "decision_intelligence", "execute"))
    registry = create_runtime_registry_from_platform_layer(layer)
    assert tuple(component.module_id for component in registry.list_runtime_components()) == ("DIE", "DKE")
    assert registry.validate_compatibility()["status"] == "compatible"


def _component(
    module_id,
    name,
    phase,
    capabilities=(),
    dependencies=(),
    contracts=None,
    frozen=True,
):
    return RuntimeComponentMetadata(
        module_id=module_id,
        name=name,
        phase=phase,
        version="1.0.0",
        status="complete",
        capabilities=capabilities,
        dependencies=dependencies,
        contracts=contracts or {},
        frozen=frozen,
    )
