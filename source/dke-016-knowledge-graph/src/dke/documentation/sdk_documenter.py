from __future__ import annotations

from typing import Any

from .api_documenter import ApiIntegrationDocumentationFramework, create_api_integration_documentation_framework
from .developer_errors import MalformedApiReferenceError

SDK_COMPONENTS = (
    "PlatformIntegrationLayer",
    "UnifiedPlatformRuntimeRegistry",
    "ContractAdapterRegistry",
    "EnterpriseApiGateway",
    "PersistenceIntegrationLayer",
    "ObservabilityIntegrationLayer",
    "EndToEndRegressionValidator",
    "DecisionQualityBenchmarkSuite",
    "PerformanceBenchmarkHarness",
    "GovernanceProvenanceValidationFramework",
    "EnterpriseStressTestEngine",
)


class SDKDocumenter:
    def __init__(self, api_framework: ApiIntegrationDocumentationFramework | None = None) -> None:
        self.api_framework = api_framework or create_api_integration_documentation_framework()

    def generate_sdk_reference(self) -> dict[str, Any]:
        api_catalog = self.api_framework.generate_api_catalog()
        references = []
        for component in SDK_COMPONENTS:
            apis = tuple(api for api in api_catalog["apis"] if api["api_id"].startswith(f"{component}."))
            references.append(
                {
                    "component": component,
                    "api_count": len(apis),
                    "apis": apis,
                    "example": self._example_for(component),
                }
            )
        self.validate_sdk_reference(tuple(references))
        return {
            "reference_type": "sdk_reference",
            "status": "generated",
            "component_count": len(references),
            "components": tuple(sorted(references, key=lambda item: item["component"])),
        }

    def validate_sdk_reference(self, references: tuple[dict[str, Any], ...]) -> dict[str, Any]:
        for reference in references:
            if not reference.get("component") or "apis" not in reference or not reference.get("example"):
                raise MalformedApiReferenceError("malformed SDK API reference")
        return {"status": "valid", "component_count": len(references)}

    def _example_for(self, component: str) -> str:
        examples = {
            "PlatformIntegrationLayer": "layer.execute_component('DIE', {'query': 'example'})",
            "UnifiedPlatformRuntimeRegistry": "registry.export_registry_snapshot()",
            "ContractAdapterRegistry": "adapters.export_adapter_snapshot()",
            "EnterpriseApiGateway": "gateway.handle_request('/platform/components', 'GET')",
            "PersistenceIntegrationLayer": "persistence.export_persistence_snapshot()",
            "ObservabilityIntegrationLayer": "observability.export_observability_snapshot()",
            "EndToEndRegressionValidator": "validator.execute_full_regression()",
            "DecisionQualityBenchmarkSuite": "quality.generate_scorecard('decision-quality-default')",
            "PerformanceBenchmarkHarness": "performance.generate_performance_report()",
            "GovernanceProvenanceValidationFramework": "governance.generate_governance_report()",
            "EnterpriseStressTestEngine": "stress.generate_stress_report()",
        }
        return examples[component]
