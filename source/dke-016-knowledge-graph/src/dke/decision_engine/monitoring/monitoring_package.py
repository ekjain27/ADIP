from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import DecisionHealth, MonitoringDecisionPackage
from .monitoring_validator import MonitoringValidator


class MonitoringPackageBuilder:
    def __init__(self, validator: MonitoringValidator | None = None) -> None:
        self.validator = validator or MonitoringValidator()

    def build(
        self,
        monitoring_results: tuple[DecisionHealth, ...],
        selected_monitoring: DecisionHealth | None,
        monitoring_strategy: str = "deterministic_decision_health_monitoring_fabric",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MonitoringDecisionPackage:
        package_metadata = {
            "module": "DIE-018",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.monitoring",
        }
        package_metadata.update(metadata or {})
        package = MonitoringDecisionPackage(
            monitoring_results=monitoring_results,
            selected_monitoring=selected_monitoring,
            monitoring_strategy=monitoring_strategy,
            summary=summary or self._summary(monitoring_results, selected_monitoring),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, results: tuple[DecisionHealth, ...], selected: DecisionHealth | None) -> str:
        if not results:
            return "No workflow decisions were available for monitoring."
        if selected is None:
            return f"Generated {len(results)} monitoring result(s), but no selected result is available."
        return f"Selected monitoring for {selected.alternative_id} with status {selected.workflow_status} and health score {selected.health_score:.3f}."
