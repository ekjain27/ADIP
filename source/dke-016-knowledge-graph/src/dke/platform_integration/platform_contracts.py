from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .platform_errors import ContractValidationError


PLATFORM_COMPONENTS: tuple[str, ...] = (
    "DKE",
    "DIE",
    "DPG",
    "DDGM",
    "TDLL",
    "ADBM",
    "ADWG",
    "DHMF",
    "DRIF",
    "EDOF",
)


@dataclass(frozen=True)
class PlatformContract:
    name: str
    component_type: str
    execution_method: str
    required_methods: tuple[str, ...] = field(default_factory=tuple)
    payload_type: type = object
    description: str = ""

    def validate_component(self, component: Any) -> None:
        if component is None:
            raise ContractValidationError(f"{self.name} component is required")
        if not self.name or not isinstance(self.name, str):
            raise ContractValidationError("contract name is required")
        if self.name not in PLATFORM_COMPONENTS:
            raise ContractValidationError(f"unsupported platform component: {self.name}")
        if not self.execution_method or not isinstance(self.execution_method, str):
            raise ContractValidationError(f"{self.name} execution method is required")
        required = (*self.required_methods, self.execution_method)
        missing = tuple(method for method in required if not callable(getattr(component, method, None)))
        if missing:
            missing_text = ", ".join(sorted(set(missing)))
            raise ContractValidationError(f"{self.name} component missing callable method(s): {missing_text}")

    def validate_payload(self, payload: Any) -> None:
        if self.payload_type is object:
            return
        if not isinstance(payload, self.payload_type):
            raise ContractValidationError(
                f"{self.name} payload must be {self.payload_type.__name__}, got {type(payload).__name__}"
            )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_name": self.name,
            "component_type": self.component_type,
            "execution_method": self.execution_method,
            "required_methods": tuple(sorted(set((*self.required_methods, self.execution_method)))),
            "payload_type": self.payload_type.__name__,
            "description": self.description,
        }


def default_platform_contracts() -> Mapping[str, PlatformContract]:
    return {
        "DKE": PlatformContract("DKE", "knowledge_extraction", "retrieve_context", description="Knowledge extraction boundary"),
        "DIE": PlatformContract("DIE", "decision_intelligence", "process", description="Decision intelligence boundary"),
        "DPG": PlatformContract("DPG", "provenance", "build", description="Decision provenance graph boundary"),
        "DDGM": PlatformContract("DDGM", "governance", "evaluate", description="Dynamic decision governance mesh boundary"),
        "TDLL": PlatformContract("TDLL", "temporal_lineage", "track", description="Temporal decision lineage ledger boundary"),
        "ADBM": PlatformContract("ADBM", "adaptive_behavior", "adapt", description="Adaptive decision behavior boundary"),
        "ADWG": PlatformContract("ADWG", "workflow_orchestration", "orchestrate", description="Adaptive workflow graph boundary"),
        "DHMF": PlatformContract("DHMF", "monitoring", "monitor", description="Decision health monitoring boundary"),
        "DRIF": PlatformContract("DRIF", "recommendation", "serve", description="Decision recommendation interface boundary"),
        "EDOF": PlatformContract("EDOF", "enterprise_orchestration", "orchestrate", description="Enterprise orchestration boundary"),
    }


def execute_contract(component: Any, contract: PlatformContract, payload: Any) -> Any:
    contract.validate_payload(payload)
    method: Callable[[Any], Any] = getattr(component, contract.execution_method)
    return method(payload)
