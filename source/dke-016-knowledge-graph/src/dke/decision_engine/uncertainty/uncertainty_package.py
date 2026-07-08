from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import UncertaintyDecisionPackage, UncertaintyResult
from .uncertainty_validator import UncertaintyValidator


class UncertaintyPackageBuilder:
    def __init__(self, validator: UncertaintyValidator | None = None) -> None:
        self.validator = validator or UncertaintyValidator()

    def build(
        self,
        uncertainty_results: tuple[UncertaintyResult, ...],
        selected_result: UncertaintyResult | None,
        uncertainty_strategy: str = "deterministic_uncertainty_sensitivity",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> UncertaintyDecisionPackage:
        package_metadata = {
            "module": "DIE-008",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.uncertainty",
        }
        package_metadata.update(metadata or {})
        package = UncertaintyDecisionPackage(
            uncertainty_results=uncertainty_results,
            selected_result=selected_result,
            uncertainty_strategy=uncertainty_strategy,
            summary=summary or self._summary(uncertainty_results, selected_result),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(
        self,
        results: tuple[UncertaintyResult, ...],
        selected: UncertaintyResult | None,
    ) -> str:
        if not results:
            return "No optimized decisions were available for uncertainty analysis."
        if selected is None:
            return f"Analyzed {len(results)} result(s), but no selected uncertainty result is available."
        return (
            f"Selected {selected.alternative_id} reliability {selected.reliability_score:.3f} "
            f"with uncertainty {selected.uncertainty_score:.3f}."
        )
