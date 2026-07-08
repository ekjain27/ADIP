from __future__ import annotations

from decision_engine.core.models import clamp_confidence
from decision_engine.workflow import WorkflowDecision

from .models import MonitoringMetric


class MetricCollector:
    def collect(self, workflow: WorkflowDecision) -> tuple[MonitoringMetric, ...]:
        graph = workflow.workflow_graph
        stage_count = len(graph.stages)
        approval_count = sum(1 for gate in graph.approval_gates if gate.approval_required)
        exception_count = len(graph.exception_paths)
        routing_complexity = len(graph.transitions) / max(1, stage_count)
        metrics = (
            self._metric(workflow.alternative_id, "completion_score", workflow.completion_score, 0.72, higher_is_better=True),
            self._metric(workflow.alternative_id, "stage_count", clamp_confidence(stage_count / 10.0), 0.80, higher_is_better=False, raw=stage_count),
            self._metric(workflow.alternative_id, "approval_count", clamp_confidence(approval_count / max(1, stage_count)), 0.65, higher_is_better=False, raw=approval_count),
            self._metric(workflow.alternative_id, "exception_count", clamp_confidence(exception_count / 6.0), 0.50, higher_is_better=False, raw=exception_count),
            self._metric(workflow.alternative_id, "routing_complexity", clamp_confidence(routing_complexity / 1.5), 0.75, higher_is_better=False, raw=round(routing_complexity, 6)),
        )
        return metrics

    def _metric(
        self,
        alternative_id: str,
        name: str,
        value: float,
        threshold: float,
        higher_is_better: bool,
        raw: float | int | None = None,
    ) -> MonitoringMetric:
        normalized = clamp_confidence(value)
        if higher_is_better:
            status = "healthy" if normalized >= threshold else "watch" if normalized >= threshold * 0.8 else "degraded"
        else:
            status = "healthy" if normalized <= threshold else "watch" if normalized <= min(1.0, threshold + 0.15) else "degraded"
        return MonitoringMetric(
            metric_id=f"metric-{alternative_id}-{name}".lower().replace(" ", "-").replace("_", "-"),
            name=name,
            value=normalized,
            status=status,
            threshold=threshold,
            metadata={"raw_value": raw if raw is not None else normalized},
        )
