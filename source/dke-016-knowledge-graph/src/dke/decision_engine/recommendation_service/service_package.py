from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .models import RecommendationDelivery, RecommendationResponse, RecommendationServicePackage
from .service_validator import ServiceValidator


class RecommendationServicePackageBuilder:
    def __init__(self, validator: ServiceValidator | None = None) -> None:
        self.validator = validator or ServiceValidator()

    def build(
        self,
        responses: tuple[RecommendationResponse, ...],
        selected_response: RecommendationResponse | None,
        deliveries: tuple[RecommendationDelivery, ...],
        service_strategy: str = "deterministic_decision_recommendation_interface_fabric",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> RecommendationServicePackage:
        package_metadata = {
            "module": "DIE-019",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.recommendation_service",
        }
        package_metadata.update(metadata or {})
        package = RecommendationServicePackage(
            responses=responses,
            selected_response=selected_response,
            deliveries=deliveries,
            service_strategy=service_strategy,
            summary=summary or self._summary(responses, selected_response),
            metadata=package_metadata,
        )
        self.validator.validate_package(package)
        return package

    def _summary(self, responses: tuple[RecommendationResponse, ...], selected: RecommendationResponse | None) -> str:
        if not responses:
            return "No monitoring results were available for recommendation service responses."
        if selected is None:
            return f"Generated {len(responses)} recommendation response(s), but no selected response is available."
        return f"Selected recommendation response for {selected.alternative_id} with priority {selected.priority} and confidence {selected.confidence:.3f}."
