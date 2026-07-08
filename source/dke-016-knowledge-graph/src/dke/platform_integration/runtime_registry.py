from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_errors import (
    FrozenRuntimeComponentError,
    RuntimeCompatibilityError,
    RuntimeComponentNotFoundError,
    RuntimeComponentRegistrationError,
    RuntimeDependencyError,
)
from .runtime_metadata import RuntimeComponentMetadata, VALID_RUNTIME_PHASES


class UnifiedPlatformRuntimeRegistry:
    MODULE = "PI-002"

    def __init__(self) -> None:
        self._components: dict[str, RuntimeComponentMetadata] = {}

    def register_runtime_component(self, metadata: RuntimeComponentMetadata) -> RuntimeComponentMetadata:
        if not isinstance(metadata, RuntimeComponentMetadata):
            raise RuntimeComponentRegistrationError("metadata must be RuntimeComponentMetadata")
        if metadata.module_id in self._components:
            raise RuntimeComponentRegistrationError(f"runtime component already registered: {metadata.module_id}")
        self._components[metadata.module_id] = metadata
        return metadata

    def get_runtime_component(self, module_id: str) -> RuntimeComponentMetadata:
        normalized = self._normalize_module_id(module_id)
        try:
            return self._components[normalized]
        except KeyError as exc:
            raise RuntimeComponentNotFoundError(f"runtime component is not registered: {normalized}") from exc

    def list_runtime_components(self) -> tuple[RuntimeComponentMetadata, ...]:
        return tuple(self._components[module_id] for module_id in sorted(self._components))

    def list_by_phase(self, phase: str) -> tuple[RuntimeComponentMetadata, ...]:
        if phase not in VALID_RUNTIME_PHASES:
            raise RuntimeComponentRegistrationError(f"invalid runtime phase: {phase}")
        return tuple(component for component in self.list_runtime_components() if component.phase == phase)

    def list_capabilities(self) -> dict[str, tuple[str, ...]]:
        return {
            component.module_id: component.capabilities
            for component in self.list_runtime_components()
        }

    def validate_dependencies(self) -> dict[str, Any]:
        missing: dict[str, tuple[str, ...]] = {}
        for component in self.list_runtime_components():
            absent = tuple(dependency for dependency in component.dependencies if dependency not in self._components)
            if absent:
                missing[component.module_id] = absent
        if missing:
            formatted = "; ".join(f"{module}: {', '.join(deps)}" for module, deps in sorted(missing.items()))
            raise RuntimeDependencyError(f"missing runtime dependencies: {formatted}")
        return {
            "module": self.MODULE,
            "status": "valid",
            "component_count": len(self._components),
            "dependency_count": sum(len(component.dependencies) for component in self._components.values()),
            "components": tuple(sorted(self._components)),
        }

    def validate_compatibility(self) -> dict[str, Any]:
        self.validate_dependencies()
        incompatible: dict[str, tuple[str, ...]] = {}
        for component in self.list_runtime_components():
            required = component.contracts.get("requires", ())
            if not required:
                continue
            dependency_contracts = self._provided_contracts(component.dependencies)
            missing = tuple(contract for contract in required if contract not in dependency_contracts)
            if missing:
                incompatible[component.module_id] = missing
        if incompatible:
            formatted = "; ".join(f"{module}: {', '.join(contracts)}" for module, contracts in sorted(incompatible.items()))
            raise RuntimeCompatibilityError(f"incompatible runtime contracts: {formatted}")
        return {
            "module": self.MODULE,
            "status": "compatible",
            "component_count": len(self._components),
            "components": tuple(sorted(self._components)),
        }

    def export_registry_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "component_count": len(self._components),
            "components": tuple(component.snapshot() for component in self.list_runtime_components()),
            "capabilities": self.list_capabilities(),
        }

    def update_runtime_component(self, module_id: str, **changes: Any) -> RuntimeComponentMetadata:
        component = self.get_runtime_component(module_id)
        if component.frozen:
            raise FrozenRuntimeComponentError(f"runtime component is frozen: {component.module_id}")
        updated = component.with_updates(**changes)
        if updated.module_id != component.module_id and updated.module_id in self._components:
            raise RuntimeComponentRegistrationError(f"runtime component already registered: {updated.module_id}")
        self._components[updated.module_id] = updated
        if updated.module_id != component.module_id:
            del self._components[component.module_id]
        return updated

    def components(self) -> Mapping[str, RuntimeComponentMetadata]:
        return MappingProxyType(dict(sorted(self._components.items())))

    def register_platform_layer(
        self,
        layer: PlatformIntegrationLayer,
        phase: str = "platform_integration",
        version: str = "1.0.0",
        frozen: bool = True,
    ) -> tuple[RuntimeComponentMetadata, ...]:
        registered: list[RuntimeComponentMetadata] = []
        for name, registration in layer.registry.registrations().items():
            contract = registration.contract.to_metadata()
            metadata = RuntimeComponentMetadata(
                module_id=name,
                name=contract["component_type"],
                phase=phase,
                version=version,
                status="complete",
                capabilities=(contract["component_type"], registration.contract.execution_method),
                dependencies=(),
                contracts={"provides": (registration.contract.name, registration.contract.component_type)},
                frozen=frozen,
            )
            registered.append(self.register_runtime_component(metadata))
        return tuple(registered)

    def _provided_contracts(self, dependencies: tuple[str, ...]) -> tuple[str, ...]:
        provided: list[str] = []
        for dependency in dependencies:
            provided.extend(self._components[dependency].contracts.get("provides", ()))
            provided.extend(self._components[dependency].capabilities)
        return tuple(sorted(dict.fromkeys(provided)))

    def _normalize_module_id(self, module_id: str) -> str:
        if not isinstance(module_id, str) or not module_id.strip():
            raise RuntimeComponentRegistrationError("module_id is required")
        return module_id.strip().upper()


def create_runtime_registry_from_platform_layer(layer: PlatformIntegrationLayer) -> UnifiedPlatformRuntimeRegistry:
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_platform_layer(layer)
    return registry
