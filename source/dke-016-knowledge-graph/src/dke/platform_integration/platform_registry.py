from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .platform_contracts import PlatformContract
from .platform_errors import ComponentNotFoundError, ComponentRegistrationError, ContractValidationError


@dataclass(frozen=True)
class RegisteredPlatformComponent:
    name: str
    component: Any
    contract: PlatformContract

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "component_class": self.component.__class__.__name__,
            "contract": self.contract.to_metadata(),
        }


class PlatformRegistry:
    def __init__(self) -> None:
        self._components: dict[str, RegisteredPlatformComponent] = {}

    def register_component(self, name: str, component: Any, contract: PlatformContract) -> RegisteredPlatformComponent:
        normalized = self._normalize_name(name)
        if normalized in self._components:
            raise ComponentRegistrationError(f"platform component already registered: {normalized}")
        if not isinstance(contract, PlatformContract):
            raise ContractValidationError("contract must be a PlatformContract")
        if contract.name != normalized:
            raise ContractValidationError(f"contract name {contract.name} does not match component name {normalized}")
        contract.validate_component(component)
        registered = RegisteredPlatformComponent(normalized, component, contract)
        self._components[normalized] = registered
        return registered

    def get_component(self, name: str) -> Any:
        return self.get_registration(name).component

    def get_registration(self, name: str) -> RegisteredPlatformComponent:
        normalized = self._normalize_name(name)
        try:
            return self._components[normalized]
        except KeyError as exc:
            raise ComponentNotFoundError(f"platform component is not registered: {normalized}") from exc

    def list_components(self) -> tuple[str, ...]:
        return tuple(sorted(self._components))

    def registrations(self) -> Mapping[str, RegisteredPlatformComponent]:
        return MappingProxyType(dict(sorted(self._components.items())))

    def validate_platform(self, required_components: tuple[str, ...] = ()) -> dict[str, Any]:
        missing = tuple(name for name in required_components if name not in self._components)
        if missing:
            raise ComponentNotFoundError(f"missing platform component(s): {', '.join(missing)}")
        validation: dict[str, Any] = {
            "status": "valid",
            "component_count": len(self._components),
            "components": self.list_components(),
            "contracts": {},
        }
        for name, registration in sorted(self._components.items()):
            registration.contract.validate_component(registration.component)
            validation["contracts"][name] = registration.contract.to_metadata()
        return validation

    def _normalize_name(self, name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ComponentRegistrationError("platform component name is required")
        return name.strip().upper()
