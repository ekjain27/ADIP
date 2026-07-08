from __future__ import annotations

import inspect
from typing import Any

from platform_integration import ContractAdapterRegistry, EnterpriseApiGateway

from .api_errors import DuplicateApiIdentifierError, MalformedApiSignatureError, UndocumentedPublicInterfaceError
from .api_models import ApiDocumentationEntry, ApiParameter
from .documentation_generator import ArchitectureDocumentationGenerator, create_architecture_documentation_generator
from .integration_documenter import IntegrationDocumenter
from .module_registry_documenter import ModuleRegistryDocumenter, create_module_registry_documenter


class ApiIntegrationDocumentationFramework:
    MODULE = "DOC-003"

    def __init__(
        self,
        doc_generator: ArchitectureDocumentationGenerator | None = None,
        module_registry: ModuleRegistryDocumenter | None = None,
    ) -> None:
        self.doc_generator = doc_generator or create_architecture_documentation_generator()
        self.module_registry = module_registry or create_module_registry_documenter(self.doc_generator.runtime_registry)
        self.adapter_registry = ContractAdapterRegistry(self.doc_generator.platform_layer, self.doc_generator.runtime_registry)
        self.api_gateway = EnterpriseApiGateway(
            platform_layer=self.doc_generator.platform_layer,
            runtime_registry=self.doc_generator.runtime_registry,
            adapter_registry=self.adapter_registry,
        )
        self.integration_documenter = IntegrationDocumenter(
            self.doc_generator.platform_layer,
            self.doc_generator.runtime_registry,
            self.api_gateway,
            self.adapter_registry,
        )

    def generate_api_catalog(self) -> dict[str, Any]:
        entries = self._discover_api_entries()
        self.validate_api_documentation(entries)
        return {
            "module": self.MODULE,
            "catalog_type": "api_integration_catalog",
            "status": "generated",
            "api_count": len(entries),
            "apis": tuple(entry.snapshot() for entry in entries),
            "doc_001_manifest": self.doc_generator.export_json_manifest(),
            "doc_002_registry": self.module_registry.export_registry_json(),
        }

    def generate_integration_documentation(self) -> dict[str, Any]:
        return self.integration_documenter.generate_integration_documentation()

    def generate_integration_matrix(self) -> dict[str, Any]:
        return self.integration_documenter.generate_integration_matrix()

    def export_api_markdown(self) -> str:
        catalog = self.generate_api_catalog()
        integration = self.generate_integration_documentation()
        lines = [
            "# Project-1 API & Integration Documentation",
            "",
            f"Module: {self.MODULE}",
            f"API count: {catalog['api_count']}",
            "",
            "## Public APIs",
        ]
        for api in catalog["apis"]:
            params = ", ".join(f"{param['name']}: {param['annotation']}" for param in api["parameters"]) or "none"
            exceptions = ", ".join(api["exceptions"]) if api["exceptions"] else "none"
            dependencies = ", ".join(api["dependencies"]) if api["dependencies"] else "none"
            lines.append(f"- {api['api_id']}")
            lines.append(f"  - Purpose: {api['purpose']}")
            lines.append(f"  - Parameters: {params}")
            lines.append(f"  - Returns: {api['return_type']}")
            lines.append(f"  - Exceptions: {exceptions}")
            lines.append(f"  - Dependencies: {dependencies}")
        lines.extend(["", "## Integration Matrix"])
        for mapping in integration["integration_matrix"]["mappings"]:
            lines.append(f"- {mapping['source']} -> {mapping['target']}: {mapping['interaction']} via {mapping['entry_point']}")
        return "\n".join(lines) + "\n"

    def export_api_json(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "generated",
            "api_catalog": self.generate_api_catalog(),
            "integration_documentation": self.generate_integration_documentation(),
            "integration_matrix": self.generate_integration_matrix(),
        }

    def validate_api_documentation(self, entries: tuple[ApiDocumentationEntry, ...] | None = None) -> dict[str, Any]:
        active_entries = entries or self._discover_api_entries()
        seen: set[str] = set()
        for entry in active_entries:
            if entry.api_id in seen:
                raise DuplicateApiIdentifierError(f"duplicate API identifier: {entry.api_id}")
            seen.add(entry.api_id)
            snapshot = entry.snapshot()
            required = ("api_id", "name", "module", "purpose", "parameters", "return_type", "exceptions", "dependencies")
            missing = tuple(field for field in required if field not in snapshot or snapshot[field] in (None, ""))
            if missing:
                raise UndocumentedPublicInterfaceError(f"undocumented public interface field(s): {', '.join(missing)}")
        return {"module": self.MODULE, "status": "valid", "api_count": len(active_entries)}

    def _discover_api_entries(self) -> tuple[ApiDocumentationEntry, ...]:
        objects = {
            "platform_layer": self.doc_generator.platform_layer,
            "runtime_registry": self.doc_generator.runtime_registry,
            "api_gateway": self.api_gateway,
            "contract_adapter_registry": self.adapter_registry,
            "deployment_readiness": self.doc_generator.deployment_readiness,
            "module_registry_documenter": self.module_registry,
            "documentation_generator": self.doc_generator,
        }
        entries: list[ApiDocumentationEntry] = []
        for owner, obj in sorted(objects.items()):
            for method_name, method in inspect.getmembers(obj.__class__, predicate=inspect.isfunction):
                if method_name.startswith("_"):
                    continue
                signature = inspect.signature(method)
                entries.append(
                    ApiDocumentationEntry(
                        api_id=f"{obj.__class__.__name__}.{method_name}",
                        name=method_name,
                        module=obj.__class__.__module__,
                        owner=owner,
                        purpose=self._purpose(method_name),
                        parameters=self._parameters(signature),
                        return_type=self._annotation(signature.return_annotation),
                        exceptions=self._exceptions_for(owner),
                        dependencies=self._dependencies_for(owner),
                    )
                )
        return tuple(sorted(entries, key=lambda entry: entry.api_id))

    def _parameters(self, signature: inspect.Signature) -> tuple[ApiParameter, ...]:
        parameters = []
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                raise MalformedApiSignatureError(f"unsupported variadic API parameter: {name}")
            default = None if parameter.default is inspect._empty else repr(parameter.default)
            parameter_name = f"**{name}" if parameter.kind == inspect.Parameter.VAR_KEYWORD else name
            parameters.append(ApiParameter(parameter_name, self._annotation(parameter.annotation), default))
        return tuple(parameters)

    def _annotation(self, annotation: Any) -> str:
        if annotation is inspect._empty:
            return "Any"
        if isinstance(annotation, str):
            return annotation
        return getattr(annotation, "__name__", str(annotation))

    def _purpose(self, method_name: str) -> str:
        return method_name.replace("_", " ").strip().capitalize()

    def _exceptions_for(self, owner: str) -> tuple[str, ...]:
        return {
            "platform_layer": ("PlatformIntegrationError",),
            "runtime_registry": ("RuntimeRegistryError",),
            "api_gateway": ("ApiGatewayError",),
            "contract_adapter_registry": ("ContractAdapterError",),
            "deployment_readiness": ("DeploymentReadinessError",),
            "module_registry_documenter": ("ModuleRegistryDocumentationError",),
            "documentation_generator": ("DocumentationGenerationError",),
        }.get(owner, ())

    def _dependencies_for(self, owner: str) -> tuple[str, ...]:
        return {
            "platform_layer": ("PI-001",),
            "runtime_registry": ("PI-002",),
            "contract_adapter_registry": ("PI-001", "PI-002", "PI-003"),
            "api_gateway": ("PI-001", "PI-002", "PI-003", "PI-004"),
            "deployment_readiness": ("PI-001", "PI-002", "PI-004", "PI-008"),
            "module_registry_documenter": ("DOC-001", "PI-002"),
            "documentation_generator": ("DOC-001", "PI-002", "PI-008"),
        }.get(owner, ())


def create_api_integration_documentation_framework() -> ApiIntegrationDocumentationFramework:
    return ApiIntegrationDocumentationFramework()
