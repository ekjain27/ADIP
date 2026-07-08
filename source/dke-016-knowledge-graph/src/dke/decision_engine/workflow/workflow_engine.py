from __future__ import annotations

import logging

from decision_engine.adaptive import AdaptiveDecision, AdaptiveDecisionPackage
from decision_engine.core.models import clamp_confidence

from .models import WorkflowDecision
from .workflow_graph import WorkflowGraphBuilder
from .workflow_package import WorkflowPackageBuilder

logger = logging.getLogger(__name__)


class DecisionWorkflowEngine:
    STRATEGY = "deterministic_adaptive_decision_workflow_graph"

    def __init__(
        self,
        graph_builder: WorkflowGraphBuilder | None = None,
        package_builder: WorkflowPackageBuilder | None = None,
    ) -> None:
        self.graph_builder = graph_builder or WorkflowGraphBuilder()
        self.package_builder = package_builder or WorkflowPackageBuilder()

    def orchestrate(self, adaptive_package: AdaptiveDecisionPackage):
        if not isinstance(adaptive_package, AdaptiveDecisionPackage):
            raise ValueError("DecisionWorkflowEngine.orchestrate requires an AdaptiveDecisionPackage")
        logger.info("Orchestrating adaptive decision workflows")
        results = tuple(self._orchestrate_decision(result) for result in adaptive_package.adaptive_results)
        selected = self._selected_workflow(results, adaptive_package.selected_adaptive_result)
        return self.package_builder.build(
            results,
            selected,
            workflow_strategy=self.STRATEGY,
            metadata={
                "source_module": adaptive_package.metadata.get("module", "DIE-016"),
                "adaptive_result_count": len(adaptive_package.adaptive_results),
            },
        )

    def _orchestrate_decision(self, decision: AdaptiveDecision) -> WorkflowDecision:
        graph = self.graph_builder.build(decision)
        execution_plan = tuple(stage.stage_id for stage in sorted(graph.stages, key=lambda stage: stage.sequence))
        completion_score = self._completion_score(decision, graph)
        return WorkflowDecision(
            alternative_id=decision.alternative_id,
            workflow_graph=graph,
            execution_plan=execution_plan,
            routing_summary=f"Workflow routes {len(graph.stages)} stages through {len(graph.transitions)} deterministic transition(s).",
            completion_score=completion_score,
            metadata={
                "adaptive_confidence": decision.confidence,
                "approval_gate_count": len(graph.approval_gates),
                "exception_path_count": len(graph.exception_paths),
            },
        )

    def _selected_workflow(self, results: tuple[WorkflowDecision, ...], selected_adaptive: AdaptiveDecision | None) -> WorkflowDecision | None:
        if not results:
            return None
        if selected_adaptive is not None:
            for result in results:
                if result.alternative_id == selected_adaptive.alternative_id:
                    return result
        return max(results, key=lambda result: (result.completion_score, result.alternative_id))

    def _completion_score(self, decision: AdaptiveDecision, graph) -> float:
        approval_load = sum(1 for gate in graph.approval_gates if gate.approval_required) / max(1, len(graph.approval_gates))
        exception_load = len(graph.exception_paths) / 6.0
        score = (decision.confidence * 0.45) + (decision.adaptation_score * 0.35) + ((1.0 - approval_load) * 0.10) + ((1.0 - min(1.0, exception_load)) * 0.10)
        return clamp_confidence(score)
