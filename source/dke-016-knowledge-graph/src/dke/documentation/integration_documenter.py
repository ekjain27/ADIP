from __future__ import annotations

from typing import Any

from platform_integration import ContractAdapterRegistry, EnterpriseApiGateway, PlatformIntegrationLayer, UnifiedPlatformRuntimeRegistry

from .api_models import IntegrationMapping
from .integration_matrix import generate_integration_matrix


class IntegrationDocumenter:
    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer,
        runtime_registry: UnifiedPlatformRuntimeRegistry,
        api_gateway: EnterpriseApiGateway,
        adapter_registry: ContractAdapterRegistry | None = None,
    ) -> None:
        self.platform_layer = platform_layer
        self.runtime_registry = runtime_registry
        self.api_gateway = api_gateway
        self.adapter_registry = adapter_registry or ContractAdapterRegistry(platform_layer, runtime_registry)

    def generate_integration_documentation(self) -> dict[str, Any]:
        matrix = self.generate_integration_matrix()
        return {
            "module": "DOC-003",
            "status": "generated",
            "documentation_type": "integration_documentation",
            "integration_matrix": matrix,
            "runtime_registry_interactions": self.runtime_registry.export_registry_snapshot(),
            "contract_adapter_mappings": self.adapter_registry.export_adapter_snapshot(),
            "api_gateway_routes": self._gateway_routes(),
        }

    def generate_integration_matrix(self) -> dict[str, Any]:
        mappings = (
            IntegrationMapping("research-to-dke", "Research", "DKE", "knowledge extraction handoff", "research_context", "DKE.retrieve_context"),
            IntegrationMapping("dke-to-die", "DKE", "DIE", "decision intelligence handoff", "knowledge_context", "DIE.process"),
            IntegrationMapping("die-to-platform", "DIE", "Platform Integration", "platform execution boundary", "decision_payload", "PlatformIntegrationLayer.execute_pipeline"),
            IntegrationMapping("platform-to-validation", "Platform Integration", "Validation", "validation scenario execution", "platform_snapshot", "EndToEndRegressionValidator.execute_full_regression"),
            IntegrationMapping("runtime-registry", "PI-002", "Documentation", "runtime registry documentation", "runtime_metadata", "UnifiedPlatformRuntimeRegistry.export_registry_snapshot"),
            IntegrationMapping("contract-adapter", "PI-003", "Platform Integration", "cross-engine payload mapping", "adapter_contract", "ContractAdapterRegistry.export_adapter_snapshot"),
            IntegrationMapping("api-gateway", "PI-004", "Platform Services", "internal route dispatch", "gateway_route", "EnterpriseApiGateway.handle_request"),
        )
        return generate_integration_matrix(mappings)

    def _gateway_routes(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "route": route["path"],
                "method": route["method"],
                "required_fields": route["required_fields"],
                "description": route["description"],
            }
            for route in self.api_gateway.list_routes()
        )
