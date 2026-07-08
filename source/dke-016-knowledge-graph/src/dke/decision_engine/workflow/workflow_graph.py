from __future__ import annotations

from decision_engine.adaptive import AdaptiveDecision

from .approval_manager import ApprovalManager
from .exception_handler import ExceptionHandler
from .models import WorkflowGraph
from .routing_engine import RoutingEngine
from .stage_builder import StageBuilder
from .workflow_validator import WorkflowValidator


class WorkflowGraphBuilder:
    def __init__(
        self,
        stage_builder: StageBuilder | None = None,
        routing_engine: RoutingEngine | None = None,
        approval_manager: ApprovalManager | None = None,
        exception_handler: ExceptionHandler | None = None,
        validator: WorkflowValidator | None = None,
    ) -> None:
        self.stage_builder = stage_builder or StageBuilder()
        self.routing_engine = routing_engine or RoutingEngine()
        self.approval_manager = approval_manager or ApprovalManager()
        self.exception_handler = exception_handler or ExceptionHandler()
        self.validator = validator or WorkflowValidator()

    def build(self, decision: AdaptiveDecision) -> WorkflowGraph:
        stages = self.stage_builder.build(decision)
        transitions = self.routing_engine.route(decision, stages)
        approval_gates = self.approval_manager.build(decision, stages)
        exception_paths = self.exception_handler.build(decision)
        graph = WorkflowGraph(
            stages=stages,
            transitions=transitions,
            approval_gates=approval_gates,
            exception_paths=exception_paths,
            metadata={
                "graph_type": "Adaptive Decision Workflow Graph",
                "alternative_id": decision.alternative_id,
                "dag": True,
            },
        )
        self.validator.validate_graph(graph)
        return graph
