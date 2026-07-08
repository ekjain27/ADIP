from __future__ import annotations

from .models import WorkflowDecision, WorkflowDecisionPackage, WorkflowGraph


class WorkflowValidator:
    VALID_STAGE_STATUSES = {"ready", "pending", "complete", "blocked"}

    def validate_graph(self, graph: WorkflowGraph) -> None:
        stage_ids = tuple(stage.stage_id for stage in graph.stages)
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("workflow stages must be unique")
        if not stage_ids and (graph.transitions or graph.approval_gates):
            raise ValueError("workflow graph cannot have transitions or approvals without stages")
        for stage in graph.stages:
            if stage.status not in self.VALID_STAGE_STATUSES:
                raise ValueError(f"invalid workflow stage status: {stage.status}")
        self._validate_ordering(graph)
        self._validate_transitions(graph, set(stage_ids))
        self._validate_approvals(graph, set(stage_ids))
        self._validate_exceptions(graph)
        if graph.stages:
            self._validate_connectivity(graph)
            if self.has_cycle(graph):
                raise ValueError("workflow graph contains a cycle")

    def validate_decision(self, decision: WorkflowDecision) -> None:
        if not decision.alternative_id.strip():
            raise ValueError("WorkflowDecision.alternative_id is required")
        self.validate_graph(decision.workflow_graph)
        if not 0.0 <= decision.completion_score <= 1.0:
            raise ValueError("completion score must be between 0 and 1")

    def validate_package(self, package: WorkflowDecisionPackage) -> None:
        if not isinstance(package, WorkflowDecisionPackage):
            raise ValueError("Expected WorkflowDecisionPackage")
        for result in package.workflow_results:
            self.validate_decision(result)
        if package.workflow_results and package.selected_workflow is None:
            raise ValueError("selected workflow is required when workflow results exist")
        if not package.workflow_results and package.selected_workflow is not None:
            raise ValueError("selected workflow must be None when no workflow results exist")
        if package.selected_workflow is not None and package.selected_workflow not in package.workflow_results:
            raise ValueError("selected workflow must be present in workflow results")

    def has_cycle(self, graph: WorkflowGraph) -> bool:
        adjacency = {stage.stage_id: [] for stage in graph.stages}
        for transition in graph.transitions:
            adjacency.setdefault(transition.source_stage, []).append(transition.target_stage)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(stage_id: str) -> bool:
            if stage_id in visiting:
                return True
            if stage_id in visited:
                return False
            visiting.add(stage_id)
            for child in adjacency.get(stage_id, ()):
                if visit(child):
                    return True
            visiting.remove(stage_id)
            visited.add(stage_id)
            return False

        return any(visit(stage_id) for stage_id in adjacency)

    def _validate_ordering(self, graph: WorkflowGraph) -> None:
        sequences = tuple(stage.sequence for stage in graph.stages)
        if sequences != tuple(sorted(sequences)):
            raise ValueError("workflow stages must be ordered by sequence")
        if len(sequences) != len(set(sequences)):
            raise ValueError("workflow stage sequence values must be unique")

    def _validate_transitions(self, graph: WorkflowGraph, stage_ids: set[str]) -> None:
        transition_ids = tuple(transition.transition_id for transition in graph.transitions)
        if len(transition_ids) != len(set(transition_ids)):
            raise ValueError("workflow transitions must be unique")
        for transition in graph.transitions:
            if transition.source_stage not in stage_ids or transition.target_stage not in stage_ids:
                raise ValueError("workflow transition references missing stage")

    def _validate_approvals(self, graph: WorkflowGraph, stage_ids: set[str]) -> None:
        gate_ids = tuple(gate.gate_id for gate in graph.approval_gates)
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("approval gates must be unique")
        for gate in graph.approval_gates:
            if gate.stage_id not in stage_ids:
                raise ValueError("approval gate references missing stage")

    def _validate_exceptions(self, graph: WorkflowGraph) -> None:
        path_ids = tuple(path.path_id for path in graph.exception_paths)
        if len(path_ids) != len(set(path_ids)):
            raise ValueError("exception paths must be unique")
        for path in graph.exception_paths:
            if not path.trigger.strip() or not path.recovery_action.strip():
                raise ValueError("exception paths require trigger and recovery action")

    def _validate_connectivity(self, graph: WorkflowGraph) -> None:
        targets = {transition.target_stage for transition in graph.transitions}
        sources = {transition.source_stage for transition in graph.transitions}
        roots = [stage.stage_id for stage in graph.stages if stage.stage_id not in targets]
        terminals = [stage.stage_id for stage in graph.stages if stage.stage_id not in sources]
        if len(roots) != 1:
            raise ValueError("workflow graph must have a single start stage")
        if len(terminals) != 1:
            raise ValueError("workflow graph must have a single end stage")
        undirected = {stage.stage_id: set() for stage in graph.stages}
        for transition in graph.transitions:
            undirected[transition.source_stage].add(transition.target_stage)
            undirected[transition.target_stage].add(transition.source_stage)
        seen: set[str] = set()
        stack = [roots[0]]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(sorted(undirected.get(current, set()) - seen))
        if len(seen) != len(graph.stages):
            raise ValueError("workflow graph contains isolated stages")
