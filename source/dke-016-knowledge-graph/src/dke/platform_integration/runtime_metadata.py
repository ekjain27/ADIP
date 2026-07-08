from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from .runtime_errors import FrozenRuntimeComponentError, RuntimeComponentRegistrationError, RuntimeCompatibilityError


VALID_RUNTIME_PHASES: tuple[str, ...] = (
    "research",
    "dke",
    "die",
    "platform_integration",
    "validation_benchmarking",
    "documentation",
    "patent",
    "research_paper",
    "commercial_release",
)

VALID_RUNTIME_STATUSES: tuple[str, ...] = (
    "planned",
    "active",
    "complete",
    "deprecated",
    "retired",
)

DETERMINISTIC_RUNTIME_TIMESTAMP = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class RuntimeComponentMetadata:
    module_id: str
    name: str
    phase: str
    version: str = "1.0.0"
    status: str = "complete"
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    contracts: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    frozen: bool = True
    created_at: str = DETERMINISTIC_RUNTIME_TIMESTAMP
    updated_at: str = DETERMINISTIC_RUNTIME_TIMESTAMP

    def __post_init__(self) -> None:
        module_id = self._required_text(self.module_id, "module_id").upper()
        name = self._required_text(self.name, "name")
        phase = self._required_text(self.phase, "phase")
        version = self._required_text(self.version, "version")
        status = self._required_text(self.status, "status")
        if phase not in VALID_RUNTIME_PHASES:
            raise RuntimeComponentRegistrationError(f"invalid runtime phase: {phase}")
        if status not in VALID_RUNTIME_STATUSES:
            raise RuntimeComponentRegistrationError(f"invalid runtime status: {status}")
        normalized_contracts = {
            key: tuple(sorted(dict.fromkeys(value)))
            for key, value in sorted((self.contracts or {}).items())
        }
        unknown_contract_keys = tuple(key for key in normalized_contracts if key not in {"provides", "requires"})
        if unknown_contract_keys:
            raise RuntimeCompatibilityError(f"unsupported contract key(s): {', '.join(unknown_contract_keys)}")
        object.__setattr__(self, "module_id", module_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "capabilities", tuple(sorted(dict.fromkeys(self.capabilities))))
        object.__setattr__(self, "dependencies", tuple(sorted(dep.upper() for dep in dict.fromkeys(self.dependencies))))
        object.__setattr__(self, "contracts", normalized_contracts)

    def snapshot(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "phase": self.phase,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "contracts": {
                key: value
                for key, value in sorted(self.contracts.items())
            },
            "frozen": self.frozen,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def with_updates(self, **changes: Any) -> "RuntimeComponentMetadata":
        if self.frozen:
            raise FrozenRuntimeComponentError(f"runtime component is frozen: {self.module_id}")
        return replace(self, **changes, updated_at=DETERMINISTIC_RUNTIME_TIMESTAMP)

    def _required_text(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RuntimeComponentRegistrationError(f"{field_name} is required")
        return value.strip()
