# DIE-012 Strategic Planning Engine

DIE-012 consumes a `MultiObjectiveDecisionPackage` from DIE-011 and produces a `StrategicPlanDecisionPackage`.

## Hierarchical Strategic Planning Graph

The module introduces the Hierarchical Strategic Planning Graph, or HSPG. It represents strategy as a deterministic graph:

Vision -> Strategic Goals -> Objectives -> Milestones -> Execution Phases -> Tasks and Dependencies -> KPIs -> Adaptive Checkpoints.

The current implementation models the graph through strategic goals, objective nodes, milestones, execution phases, explicit dependencies, and adaptive checkpoints. KPI readiness is expressed through milestone success criteria and checkpoint conditions.

## Components

- `GoalDecomposer` turns a balanced decision result into strategic goals and objective nodes.
- `MilestoneGenerator` creates short-term, mid-term, and long-term milestones.
- `DependencyGraphBuilder` builds and validates a directed acyclic dependency graph.
- `ExecutionPlanner` creates preparation, planning, execution, validation, optimization, and completion phases.
- `CheckpointGenerator` creates adaptive checkpoints for budget, confidence, schedule, and risk changes.
- `PlanningValidator` validates graph structure, ordering, dependencies, checkpoints, and package selection.
- `PlanningPackageBuilder` assembles the final strategic planning package.
- `StrategicPlanningEngine` coordinates the deterministic end-to-end workflow.

## Example

```python
from decision_engine.strategic_planning import StrategicPlanningEngine

strategic_package = StrategicPlanningEngine().plan(multi_objective_package)
selected_plan = strategic_package.selected_plan
```

Future planners can plug in by replacing the decomposer, milestone generator, dependency builder, execution planner, checkpoint generator, or package builder without changing the public engine API.
