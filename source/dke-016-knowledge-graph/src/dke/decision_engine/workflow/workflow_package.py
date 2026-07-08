from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import WorkflowDecision, WorkflowDecisionPackage
from .workflow_validator import WorkflowValidator


class WorkflowPackageBuilder:
    def __init__(self, validator: WorkflowValidator | None = None) -> None:
        self.validator = validator or WorkflowValidator()

    def build(
        self,
        workflow_results: tuple[WorkflowDecision, ...],
        selected_workflow: WorkflowDecision | None,
        workflow_strategy: str = "deterministic_adaptive_decision_workflow_graph",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowDecisionPackage:
        package_metadata = {
            "module": "DIE-017",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.workflow",
        }
        package_metadata.update(metadata or {})
        package = WorkflowDecisionPackage(
            workflow_results=workflow_results,
            selected_workflow=selected_workflow,
            workflow_strategy=workflow_strategy,
            summary=summary or self._summary(workflow_results, selected_workflow),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, results: tuple[WorkflowDecision, ...], selected: WorkflowDecision | None) -> str:
        if not results:
            return "No adaptive decisions were available for workflow orchestration."
        if selected is None:
            return f"Generated {len(results)} workflow(s), but no selected workflow is available."
        return f"Selected workflow for {selected.alternative_id} with completion score {selected.completion_score:.3f}."
