from __future__ import annotations

from decision_engine.monitoring import MonitoringValidator

from .models import RecommendationDelivery, RecommendationResponse, RecommendationServicePackage
from .priority_assigner import PriorityAssigner
from .recommendation_formatter import RecommendationFormatter


class ServiceValidator:
    VALID_CHANNELS = {"api", "dashboard", "report", "audit"}

    def validate_response(self, response: RecommendationResponse) -> None:
        if not response.response_id.strip() or not response.alternative_id.strip():
            raise ValueError("recommendation response id and alternative_id are required")
        if response.priority not in PriorityAssigner.VALID_PRIORITIES:
            raise ValueError(f"invalid recommendation priority: {response.priority}")
        if response.health_status not in MonitoringValidator.VALID_WORKFLOW_STATUSES:
            raise ValueError(f"invalid recommendation health status: {response.health_status}")
        if not 0.0 <= response.confidence <= 1.0:
            raise ValueError("recommendation confidence must be between 0 and 1")

    def validate_delivery(self, delivery: RecommendationDelivery) -> None:
        if not delivery.delivery_id.strip():
            raise ValueError("recommendation delivery id is required")
        if delivery.channel not in self.VALID_CHANNELS:
            raise ValueError(f"invalid delivery channel: {delivery.channel}")
        if delivery.format_type not in RecommendationFormatter.VALID_FORMATS:
            raise ValueError(f"invalid delivery format: {delivery.format_type}")
        if not delivery.audience.strip():
            raise ValueError("recommendation delivery audience is required")

    def validate_package(self, package: RecommendationServicePackage) -> None:
        if not isinstance(package, RecommendationServicePackage):
            raise ValueError("Expected RecommendationServicePackage")
        for response in package.responses:
            self.validate_response(response)
        response_ids = {response.response_id for response in package.responses}
        alternatives = {response.alternative_id for response in package.responses}
        for delivery in package.deliveries:
            self.validate_delivery(delivery)
            if delivery.metadata.get("alternative_id") and delivery.metadata["alternative_id"] not in alternatives:
                raise ValueError("delivery alternative reference must be present in responses")
        if package.responses and package.selected_response is None:
            raise ValueError("selected response is required when responses exist")
        if not package.responses and package.selected_response is not None:
            raise ValueError("selected response must be None when no responses exist")
        if package.selected_response is not None and package.selected_response.response_id not in response_ids:
            raise ValueError("selected response must be present in responses")
