from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .api_errors import MalformedApiSignatureError, UndocumentedPublicInterfaceError


@dataclass(frozen=True)
class ApiParameter:
    name: str
    annotation: str
    default: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.annotation:
            raise MalformedApiSignatureError("API parameter requires name and annotation")

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "annotation": self.annotation,
            "default": self.default,
        }


@dataclass(frozen=True)
class ApiDocumentationEntry:
    api_id: str
    name: str
    module: str
    owner: str
    purpose: str
    parameters: tuple[ApiParameter, ...]
    return_type: str
    exceptions: tuple[str, ...]
    dependencies: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name, value in {"api_id": self.api_id, "name": self.name}.items():
            if not isinstance(value, str) or not value.strip():
                raise UndocumentedPublicInterfaceError(f"undocumented public interface field(s): {field_name}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "api_id": self.api_id,
            "name": self.name,
            "module": self.module,
            "owner": self.owner,
            "purpose": self.purpose,
            "parameters": tuple(parameter.snapshot() for parameter in self.parameters),
            "return_type": self.return_type,
            "exceptions": self.exceptions,
            "dependencies": self.dependencies,
        }


@dataclass(frozen=True)
class IntegrationMapping:
    mapping_id: str
    source: str
    target: str
    interaction: str
    contract: str
    entry_point: str

    def __post_init__(self) -> None:
        if not all((self.mapping_id, self.source, self.target, self.interaction, self.contract, self.entry_point)):
            raise MalformedApiSignatureError("integration mapping fields are required")

    def snapshot(self) -> dict[str, str]:
        return {
            "mapping_id": self.mapping_id,
            "source": self.source,
            "target": self.target,
            "interaction": self.interaction,
            "contract": self.contract,
            "entry_point": self.entry_point,
        }
