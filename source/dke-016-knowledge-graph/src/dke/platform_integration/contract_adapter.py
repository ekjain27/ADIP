from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .contract_adapter_errors import ContractAdapterValidationError


VALID_ENGINE_IDS: tuple[str, ...] = (
    "RESEARCH",
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
class PayloadContract:
    required_fields: tuple[str, ...] = field(default_factory=tuple)
    optional_fields: tuple[str, ...] = field(default_factory=tuple)
    contract_name: str = "payload_contract"

    def validate(self, payload: Any) -> None:
        if not isinstance(payload, Mapping):
            raise ContractAdapterValidationError("payload must be a mapping")
        missing = tuple(field_name for field_name in self.required_fields if field_name not in payload)
        if missing:
            raise ContractAdapterValidationError(f"payload missing required field(s): {', '.join(missing)}")

    def metadata(self) -> dict[str, Any]:
        return {
            "contract_name": self.contract_name,
            "required_fields": tuple(sorted(self.required_fields)),
            "optional_fields": tuple(sorted(self.optional_fields)),
        }


@dataclass(frozen=True)
class AdapterResult:
    source: str
    target: str
    status: str
    original_payload: Any
    adapted_payload: Any
    validation_metadata: Mapping[str, Any]
    errors: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "status": self.status,
            "original_payload": self.original_payload,
            "adapted_payload": self.adapted_payload,
            "validation_metadata": dict(self.validation_metadata),
            "errors": self.errors,
        }


class CrossEngineContractAdapter:
    def __init__(
        self,
        source: str,
        target: str,
        input_contract: PayloadContract | None = None,
        output_contract: PayloadContract | None = None,
        transform: Callable[[dict[str, Any]], Mapping[str, Any]] | None = None,
    ) -> None:
        self.source = normalize_engine_id(source)
        self.target = normalize_engine_id(target)
        self.input_contract = input_contract or PayloadContract()
        self.output_contract = output_contract or PayloadContract()
        self.transform = transform or self._identity_transform

    def adapt(self, payload: Any) -> AdapterResult:
        self.input_contract.validate(payload)
        original_payload = deepcopy(payload)
        normalized_input = self.normalize_input(payload)
        transformed = self.transform(normalized_input)
        adapted_payload = self.normalize_output(transformed)
        self.output_contract.validate(adapted_payload)
        return AdapterResult(
            source=self.source,
            target=self.target,
            status="success",
            original_payload=original_payload,
            adapted_payload=adapted_payload,
            validation_metadata=self.metadata(),
        )

    def normalize_input(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return _deterministic_mapping(deepcopy(payload))

    def normalize_output(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ContractAdapterValidationError("adapted payload must be a mapping")
        return _deterministic_mapping(deepcopy(payload))

    def validate(self) -> dict[str, Any]:
        return {
            "status": "valid",
            "source": self.source,
            "target": self.target,
            "input_contract": self.input_contract.metadata(),
            "output_contract": self.output_contract.metadata(),
        }

    def metadata(self) -> dict[str, Any]:
        return {
            "module": "PI-003",
            "source": self.source,
            "target": self.target,
            "input_contract": self.input_contract.metadata(),
            "output_contract": self.output_contract.metadata(),
        }

    def _identity_transform(self, payload: dict[str, Any]) -> Mapping[str, Any]:
        return payload


def normalize_engine_id(engine_id: str) -> str:
    if not isinstance(engine_id, str) or not engine_id.strip():
        raise ContractAdapterValidationError("engine id is required")
    normalized = engine_id.strip().upper()
    if normalized not in VALID_ENGINE_IDS:
        raise ContractAdapterValidationError(f"invalid engine id: {normalized}")
    return normalized


def _deterministic_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: payload[key] for key in sorted(payload)}
