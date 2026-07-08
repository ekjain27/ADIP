from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class StrategicGoal:
    goal_id: str
    title: str
    description: str
    priority: str
    parent_goal: str | None = None
    child_goals: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectiveNode:
    objective_id: str
    goal_id: str
    description: str
    priority: str
    dependencies: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Milestone:
    milestone_id: str
    title: str
    description: str
    target_completion: str
    priority: str
    dependencies: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPhase:
    phase_id: str
    title: str
    description: str
    sequence: int
    milestones: tuple[str, ...] = ()
    estimated_effort: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    title: str
    condition: str
    action: str
    priority: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategicPlanningGraph:
    vision: str
    strategic_goals: tuple[StrategicGoal, ...]
    objective_nodes: tuple[ObjectiveNode, ...]
    milestones: tuple[Milestone, ...]
    execution_phases: tuple[ExecutionPhase, ...]
    dependencies: Mapping[str, tuple[str, ...]]
    checkpoints: tuple[Checkpoint, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategicPlan:
    alternative_id: str
    planning_graph: StrategicPlanningGraph
    timeline_summary: str
    execution_summary: str
    risk_summary: str
    recommendations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategicPlanDecisionPackage:
    strategic_plans: tuple[StrategicPlan, ...]
    selected_plan: StrategicPlan | None
    planning_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
