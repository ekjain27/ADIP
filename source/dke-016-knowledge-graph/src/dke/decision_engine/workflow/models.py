from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class WorkflowStage:
    stage_id: str
    name: str
    description: str
    sequence: int
    status: str
    dependencies: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowTransition:
    transition_id: str
    source_stage: str
    target_stage: str
    condition: str
    priority: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovalGate:
    gate_id: str
    stage_id: str
    approval_required: bool
    approval_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExceptionPath:
    path_id: str
    trigger: str
    recovery_action: str
    severity: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowGraph:
    stages: tuple[WorkflowStage, ...]
    transitions: tuple[WorkflowTransition, ...]
    approval_gates: tuple[ApprovalGate, ...]
    exception_paths: tuple[ExceptionPath, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowDecision:
    alternative_id: str
    workflow_graph: WorkflowGraph
    execution_plan: tuple[str, ...]
    routing_summary: str
    completion_score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowDecisionPackage:
    workflow_results: tuple[WorkflowDecision, ...]
    selected_workflow: WorkflowDecision | None
    workflow_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
