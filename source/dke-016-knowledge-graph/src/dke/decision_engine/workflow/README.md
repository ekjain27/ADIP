# DIE-017 Decision Workflow Orchestrator

DIE-017 consumes an `AdaptiveDecisionPackage` from DIE-016 and produces a `WorkflowDecisionPackage`.

## Adaptive Decision Workflow Graph

The Adaptive Decision Workflow Graph, or ADWG, turns adaptive decisions into executable enterprise workflows. It models stages, transitions, approvals, governance gates, adaptive routing, exception handling, and completion.

## Components

- `StageBuilder` creates deterministic workflow stages: Preparation, Validation, Approval, Execution, Monitoring, and Closure.
- `RoutingEngine` creates success, adaptive, alternative, and fallback routing paths without randomness.
- `ApprovalManager` creates automatic, manual, policy, and governance approval gates.
- `ExceptionHandler` creates deterministic recovery paths for approval failure, policy violation, execution failure, and adaptive drift.
- `WorkflowGraphBuilder` assembles the directed acyclic connected workflow graph.
- `WorkflowValidator` validates ordering, connectivity, transitions, approvals, exceptions, single start, and single end stage.
- `WorkflowPackageBuilder` assembles timestamped workflow packages.
- `DecisionWorkflowEngine` coordinates end-to-end orchestration.

Future workflow automation, business process engines, event-driven workflows, human approvals, and distributed workflow systems can replace builders, routers, approval managers, exception handlers, or validators without changing the public API.
