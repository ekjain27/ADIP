from __future__ import annotations

import logging

from decision_engine.monitoring import MonitoringDecisionPackage

from .delivery_router import DeliveryRouter
from .models import RecommendationResponse
from .response_builder import ResponseBuilder
from .service_package import RecommendationServicePackageBuilder

logger = logging.getLogger(__name__)


class DecisionRecommendationService:
    STRATEGY = "deterministic_decision_recommendation_interface_fabric"

    def __init__(
        self,
        response_builder: ResponseBuilder | None = None,
        delivery_router: DeliveryRouter | None = None,
        package_builder: RecommendationServicePackageBuilder | None = None,
    ) -> None:
        self.response_builder = response_builder or ResponseBuilder()
        self.delivery_router = delivery_router or DeliveryRouter()
        self.package_builder = package_builder or RecommendationServicePackageBuilder()

    def serve(self, monitoring_package: MonitoringDecisionPackage):
        if not isinstance(monitoring_package, MonitoringDecisionPackage):
            raise ValueError("DecisionRecommendationService.serve requires a MonitoringDecisionPackage")
        logger.info("Building deterministic recommendation service package")
        responses = self.response_builder.build(monitoring_package)
        selected = self._selected_response(responses, monitoring_package.selected_monitoring.alternative_id if monitoring_package.selected_monitoring else "")
        deliveries = self.delivery_router.route(responses)
        return self.package_builder.build(
            responses,
            selected,
            deliveries,
            service_strategy=self.STRATEGY,
            metadata={
                "source_module": monitoring_package.metadata.get("module", "DIE-018"),
                "monitoring_result_count": len(monitoring_package.monitoring_results),
            },
        )

    def _selected_response(self, responses: tuple[RecommendationResponse, ...], selected_alternative_id: str) -> RecommendationResponse | None:
        if not responses:
            return None
        if selected_alternative_id:
            for response in responses:
                if response.alternative_id == selected_alternative_id:
                    return response
        priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        return max(responses, key=lambda response: (priority_order[response.priority], response.confidence, response.alternative_id))
