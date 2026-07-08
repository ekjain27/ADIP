from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .contract_adapter import AdapterResult, CrossEngineContractAdapter, normalize_engine_id
from .contract_adapter_errors import (
    ContractAdapterCompatibilityError,
    ContractAdapterNotFoundError,
    ContractAdapterRegistrationError,
)
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry


class ContractAdapterRegistry:
    MODULE = "PI-003"

    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    ) -> None:
        self.platform_layer = platform_layer
        self.runtime_registry = runtime_registry
        self._adapters: dict[tuple[str, str], CrossEngineContractAdapter] = {}

    def register_adapter(self, source: str, target: str, adapter: CrossEngineContractAdapter) -> CrossEngineContractAdapter:
        normalized_source = normalize_engine_id(source)
        normalized_target = normalize_engine_id(target)
        self._validate_engine_available(normalized_source)
        self._validate_engine_available(normalized_target)
        if not isinstance(adapter, CrossEngineContractAdapter):
            raise ContractAdapterRegistrationError("adapter must be a CrossEngineContractAdapter")
        if adapter.source != normalized_source or adapter.target != normalized_target:
            raise ContractAdapterCompatibilityError("adapter source and target must match registration")
        key = (normalized_source, normalized_target)
        if key in self._adapters:
            raise ContractAdapterRegistrationError(f"adapter already registered: {normalized_source}->{normalized_target}")
        self._adapters[key] = adapter
        return adapter

    def get_adapter(self, source: str, target: str) -> CrossEngineContractAdapter:
        key = self._key(source, target)
        try:
            return self._adapters[key]
        except KeyError as exc:
            raise ContractAdapterNotFoundError(f"adapter is not registered: {key[0]}->{key[1]}") from exc

    def adapt_payload(self, source: str, target: str, payload: Any) -> AdapterResult:
        adapter = self.get_adapter(source, target)
        return adapter.adapt(payload)

    def validate_adapter(self, source: str, target: str) -> dict[str, Any]:
        adapter = self.get_adapter(source, target)
        validation = adapter.validate()
        validation["module"] = self.MODULE
        return validation

    def list_adapters(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._adapters))

    def export_adapter_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "adapter_count": len(self._adapters),
            "adapters": tuple(
                {
                    "source": source,
                    "target": target,
                    "metadata": self._adapters[(source, target)].metadata(),
                }
                for source, target in self.list_adapters()
            ),
        }

    def adapters(self) -> Mapping[tuple[str, str], CrossEngineContractAdapter]:
        return MappingProxyType(dict(sorted(self._adapters.items())))

    def _key(self, source: str, target: str) -> tuple[str, str]:
        normalized_source = normalize_engine_id(source)
        normalized_target = normalize_engine_id(target)
        self._validate_engine_available(normalized_source)
        self._validate_engine_available(normalized_target)
        return normalized_source, normalized_target

    def _validate_engine_available(self, engine_id: str) -> None:
        if self.platform_layer is not None and engine_id != "RESEARCH":
            if engine_id not in self.platform_layer.list_components():
                raise ContractAdapterCompatibilityError(f"engine is not registered in PI-001: {engine_id}")
        if self.runtime_registry is not None:
            registered = set(self.runtime_registry.components())
            if engine_id not in registered and not any(module_id.startswith(f"{engine_id}-") for module_id in registered):
                raise ContractAdapterCompatibilityError(f"engine is not registered in PI-002: {engine_id}")


def create_contract_adapter_registry(
    platform_layer: PlatformIntegrationLayer | None = None,
    runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
) -> ContractAdapterRegistry:
    return ContractAdapterRegistry(platform_layer=platform_layer, runtime_registry=runtime_registry)
