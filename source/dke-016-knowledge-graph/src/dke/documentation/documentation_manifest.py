from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .documentation_errors import DocumentationManifestError

DOCUMENTATION_BASELINE_VERSION = "DOC-001.1"


@dataclass(frozen=True)
class DocumentationManifest:
    module: str
    baseline_version: str
    architecture_summary: Mapping[str, Any]
    module_catalog: Mapping[str, Any]
    api_catalog: Mapping[str, Any]
    integration_catalog: Mapping[str, Any]
    validation_summary: Mapping[str, Any]
    runtime_registry: Mapping[str, Any]

    def snapshot(self) -> dict[str, Any]:
        if self.module != "DOC-001":
            raise DocumentationManifestError("documentation manifest module must be DOC-001")
        return {
            "module": self.module,
            "baseline_version": self.baseline_version,
            "status": "generated",
            "architecture_summary": _normalize(self.architecture_summary),
            "module_catalog": _normalize(self.module_catalog),
            "api_catalog": _normalize(self.api_catalog),
            "integration_catalog": _normalize(self.integration_catalog),
            "validation_summary": _normalize(self.validation_summary),
            "runtime_registry": _normalize(self.runtime_registry),
        }


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value
