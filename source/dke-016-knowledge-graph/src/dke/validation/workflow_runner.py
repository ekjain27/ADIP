from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from platform_integration import PlatformIntegrationLayer, default_platform_contracts

from .validation_errors import IncompleteWorkflowError, MissingPlatformComponentError


@dataclass(frozen=True)
class WorkflowResult:
    name: str
    status: str
    input_payload: Mapping[str, Any]
    output_payload: Mapping[str, Any]
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "input_payload": dict(sorted(self.input_payload.items())),
            "output_payload": dict(sorted(self.output_payload.items())),
            "diagnostics": self.diagnostics,
        }


class DeterministicWorkflowComponent:
    def retrieve_context(self, payload):
        return {"stage": "DKE", "query": payload["query"], "research": payload.get("research", ())}

    def process(self, payload):
        return {"stage": "DIE", "query": payload["query"], "decision": "approve", "evidence_count": len(payload.get("research", ()))}

    def build(self, payload):
        return {"stage": "DPG", "decision": payload.get("decision", "approve"), "provenance": "linked"}

    def evaluate(self, payload):
        return {"stage": "DDGM", "governance": "compliant", **dict(payload)}

    def track(self, payload):
        return {"stage": "TDLL", "lineage": "tracked", **dict(payload)}

    def adapt(self, payload):
        return {"stage": "ADBM", "adaptive": "stable", **dict(payload)}

    def orchestrate(self, payload):
        return {"stage": "ADWG", "workflow": "ready", **dict(payload)}

    def monitor(self, payload):
        return {"stage": "DHMF", "health": "healthy", **dict(payload)}

    def serve(self, payload):
        return {"stage": "DRIF", "recommendation": "ship", **dict(payload)}


class EnterpriseWorkflowComponent(DeterministicWorkflowComponent):
    def orchestrate(self, payload):
        return {"stage": "EDOF", "enterprise": "ready", **dict(payload)}


class WorkflowRunner:
    def __init__(self, platform_layer: PlatformIntegrationLayer | None = None) -> None:
        self.platform_layer = platform_layer or create_validation_platform_layer()
        self._workflows: dict[str, Callable[[Mapping[str, Any]], WorkflowResult]] = {
            "research_to_dke": self._research_to_dke,
            "dke_to_die": self._dke_to_die,
            "die_to_platform": self._die_to_platform,
            "complete_platform_pipeline": self._complete_platform_pipeline,
        }

    def execute_workflow(self, name: str, payload: Mapping[str, Any] | None = None) -> WorkflowResult:
        if name not in self._workflows:
            raise IncompleteWorkflowError(f"workflow is not registered: {name}")
        self._validate_required_components()
        input_payload = dict(payload or self._default_payload())
        return self._workflows[name](input_payload)

    def workflow_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._workflows))

    def _research_to_dke(self, payload: Mapping[str, Any]) -> WorkflowResult:
        research_payload = {"query": payload["query"], "research": ("R-001", "R-010")}
        output = self.platform_layer.execute_component("DKE", research_payload).output_payload
        return WorkflowResult("research_to_dke", "passed", research_payload, output)

    def _dke_to_die(self, payload: Mapping[str, Any]) -> WorkflowResult:
        dke_output = self._research_to_dke(payload).output_payload
        output = self.platform_layer.execute_component("DIE", dke_output).output_payload
        return WorkflowResult("dke_to_die", "passed", dke_output, output)

    def _die_to_platform(self, payload: Mapping[str, Any]) -> WorkflowResult:
        die_output = self._dke_to_die(payload).output_payload
        pipeline = self.platform_layer.execute_pipeline(("DPG", "DDGM", "TDLL", "ADBM"), die_output)
        return WorkflowResult("die_to_platform", "passed", die_output, pipeline.output_payload)

    def _complete_platform_pipeline(self, payload: Mapping[str, Any]) -> WorkflowResult:
        dke_output = self._research_to_dke(payload).output_payload
        pipeline = self.platform_layer.execute_pipeline(("DIE", "DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF"), dke_output)
        return WorkflowResult("complete_platform_pipeline", "passed", dke_output, pipeline.output_payload)

    def _default_payload(self) -> dict[str, Any]:
        return {"query": "Validate enterprise deployment readiness"}

    def _validate_required_components(self) -> None:
        missing = tuple(name for name in default_platform_contracts() if name not in self.platform_layer.list_components())
        if missing:
            raise MissingPlatformComponentError(f"missing platform component(s): {', '.join(missing)}")


def create_validation_platform_layer() -> PlatformIntegrationLayer:
    layer = PlatformIntegrationLayer()
    contracts = default_platform_contracts()
    shared = DeterministicWorkflowComponent()
    for name in sorted(contracts):
        component = EnterpriseWorkflowComponent() if name == "EDOF" else shared
        layer.register_component(name, component, contracts[name])
    return layer
