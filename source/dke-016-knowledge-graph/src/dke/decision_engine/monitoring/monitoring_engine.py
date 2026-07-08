from __future__ import annotations

import logging

from decision_engine.workflow import WorkflowDecision, WorkflowDecisionPackage

from .drift_detector import DriftDetector
from .health_monitor import HealthMonitor
from .metric_collector import MetricCollector
from .models import DecisionHealth
from .monitoring_package import MonitoringPackageBuilder

logger = logging.getLogger(__name__)


class DecisionMonitoringEngine:
    STRATEGY = "deterministic_decision_health_monitoring_fabric"

    def __init__(
        self,
        metric_collector: MetricCollector | None = None,
        drift_detector: DriftDetector | None = None,
        health_monitor: HealthMonitor | None = None,
        package_builder: MonitoringPackageBuilder | None = None,
    ) -> None:
        self.metric_collector = metric_collector or MetricCollector()
        self.drift_detector = drift_detector or DriftDetector()
        self.health_monitor = health_monitor or HealthMonitor()
        self.package_builder = package_builder or MonitoringPackageBuilder()

    def monitor(self, workflow_package: WorkflowDecisionPackage):
        if not isinstance(workflow_package, WorkflowDecisionPackage):
            raise ValueError("DecisionMonitoringEngine.monitor requires a WorkflowDecisionPackage")
        logger.info("Running deterministic decision health monitoring")
        results = tuple(self._monitor_workflow(workflow) for workflow in workflow_package.workflow_results)
        selected = self._selected_monitoring(results, workflow_package.selected_workflow)
        return self.package_builder.build(
            results,
            selected,
            monitoring_strategy=self.STRATEGY,
            metadata={
                "source_module": workflow_package.metadata.get("module", "DIE-017"),
                "workflow_result_count": len(workflow_package.workflow_results),
            },
        )

    def _monitor_workflow(self, workflow: WorkflowDecision) -> DecisionHealth:
        metrics = self.metric_collector.collect(workflow)
        drift = self.drift_detector.detect(workflow, metrics)
        return self.health_monitor.evaluate(workflow.alternative_id, metrics, drift)

    def _selected_monitoring(self, results: tuple[DecisionHealth, ...], selected_workflow: WorkflowDecision | None) -> DecisionHealth | None:
        if not results:
            return None
        if selected_workflow is not None:
            for result in results:
                if result.alternative_id == selected_workflow.alternative_id:
                    return result
        return max(results, key=lambda result: (result.health_score, result.alternative_id))
