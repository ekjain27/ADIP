from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .platform_contracts import PlatformContract, default_platform_contracts, execute_contract
from .platform_errors import InvalidExecutionRequestError, PlatformIntegrationError
from .platform_registry import PlatformRegistry


@dataclass(frozen=True)
class PlatformExecutionResult:
    status: str
    component_name: str
    input_payload: Any
    output_payload: Any
    validation_metadata: Mapping[str, Any]
    errors: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "component_name": self.component_name,
            "input_payload": self.input_payload,
            "output_payload": self.output_payload,
            "validation_metadata": dict(self.validation_metadata),
            "errors": self.errors,
        }


class PlatformIntegrationLayer:
    MODULE = "PI-001"

    def __init__(self, registry: PlatformRegistry | None = None) -> None:
        self.registry = registry or PlatformRegistry()

    def register_component(self, name: str, component: Any, contract: PlatformContract) -> PlatformExecutionResult:
        registered = self.registry.register_component(name, component, contract)
        return PlatformExecutionResult(
            status="registered",
            component_name=registered.name,
            input_payload={"name": name, "contract": contract.to_metadata()},
            output_payload=registered.metadata(),
            validation_metadata=self._metadata(registered.name, contract),
        )

    def get_component(self, name: str) -> Any:
        return self.registry.get_component(name)

    def list_components(self) -> tuple[str, ...]:
        return self.registry.list_components()

    def validate_platform(self, required_components: tuple[str, ...] = ()) -> dict[str, Any]:
        validation = self.registry.validate_platform(required_components)
        validation["module"] = self.MODULE
        return validation

    def execute_component(self, name: str, payload: Any) -> PlatformExecutionResult:
        if payload is None:
            raise InvalidExecutionRequestError("execution payload is required")
        registration = self.registry.get_registration(name)
        try:
            output = execute_contract(registration.component, registration.contract, payload)
        except PlatformIntegrationError:
            raise
        except Exception as exc:  # pragma: no cover - defensive envelope for real integrations
            return PlatformExecutionResult(
                status="error",
                component_name=registration.name,
                input_payload=payload,
                output_payload=None,
                validation_metadata=self._metadata(registration.name, registration.contract),
                errors=(str(exc),),
            )
        return PlatformExecutionResult(
            status="success",
            component_name=registration.name,
            input_payload=payload,
            output_payload=output,
            validation_metadata=self._metadata(registration.name, registration.contract),
        )

    def execute_pipeline(self, sequence: Sequence[str], payload: Any) -> PlatformExecutionResult:
        if not sequence:
            raise InvalidExecutionRequestError("pipeline sequence is required")
        current_payload = payload
        steps: list[dict[str, Any]] = []
        errors: list[str] = []
        for component_name in tuple(sequence):
            result = self.execute_component(component_name, current_payload)
            steps.append(
                {
                    "component_name": result.component_name,
                    "status": result.status,
                    "validation_metadata": dict(result.validation_metadata),
                    "errors": result.errors,
                }
            )
            if result.errors:
                errors.extend(result.errors)
                return PlatformExecutionResult(
                    status="error",
                    component_name="PIPELINE",
                    input_payload=payload,
                    output_payload=current_payload,
                    validation_metadata=self._pipeline_metadata(sequence, steps),
                    errors=tuple(errors),
                )
            current_payload = result.output_payload
        return PlatformExecutionResult(
            status="success",
            component_name="PIPELINE",
            input_payload=payload,
            output_payload=current_payload,
            validation_metadata=self._pipeline_metadata(sequence, steps),
        )

    def _metadata(self, name: str, contract: PlatformContract) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "component_name": name,
            "contract": contract.to_metadata(),
            "registered_components": self.list_components(),
        }

    def _pipeline_metadata(self, sequence: Sequence[str], steps: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "component_name": "PIPELINE",
            "sequence": tuple(name.strip().upper() for name in sequence),
            "step_count": len(steps),
            "steps": tuple(steps),
            "registered_components": self.list_components(),
        }


def create_default_platform_integration_layer() -> PlatformIntegrationLayer:
    from decision_engine.adaptive import AdaptiveDecisionEngine
    from decision_engine.core import DIECore
    from decision_engine.enterprise_orchestrator import EnterpriseDecisionOrchestrator
    from decision_engine.governance import DecisionGovernanceEngine
    from decision_engine.monitoring import DecisionMonitoringEngine
    from decision_engine.provenance import DecisionProvenanceEngine
    from decision_engine.recommendation_service import DecisionRecommendationService
    from decision_engine.temporal import TemporalDecisionEngine
    from decision_engine.workflow import DecisionWorkflowEngine
    from knowledge_retrieval import KnowledgeRetrievalEngine

    contracts = default_platform_contracts()
    components = {
        "DKE": KnowledgeRetrievalEngine(),
        "DIE": DIECore(),
        "DPG": DecisionProvenanceEngine(),
        "DDGM": DecisionGovernanceEngine(),
        "TDLL": TemporalDecisionEngine(),
        "ADBM": AdaptiveDecisionEngine(),
        "ADWG": DecisionWorkflowEngine(),
        "DHMF": DecisionMonitoringEngine(),
        "DRIF": DecisionRecommendationService(),
        "EDOF": EnterpriseDecisionOrchestrator(),
    }
    layer = PlatformIntegrationLayer()
    for name in sorted(components):
        layer.register_component(name, components[name], contracts[name])
    return layer
