from __future__ import annotations

from .models import RecommendationDelivery, RecommendationResponse


class DeliveryRouter:
    CHANNELS = (
        ("api", "applications", "summary"),
        ("dashboard", "operators", "detailed"),
        ("report", "executives", "executive"),
        ("audit", "governance", "technical"),
    )

    def route(self, responses: tuple[RecommendationResponse, ...]) -> tuple[RecommendationDelivery, ...]:
        deliveries: list[RecommendationDelivery] = []
        for response in responses:
            for channel, audience, format_type in self.CHANNELS:
                deliveries.append(
                    RecommendationDelivery(
                        delivery_id=f"delivery-{response.response_id}-{channel}",
                        channel=channel,
                        audience=audience,
                        format_type=format_type,
                        routing_reason=self._reason(response, channel),
                        metadata={"alternative_id": response.alternative_id, "priority": response.priority},
                    )
                )
        return tuple(deliveries)

    def _reason(self, response: RecommendationResponse, channel: str) -> str:
        if channel == "audit":
            return "Preserve governed recommendation trace for audit consumers."
        if channel == "report":
            return "Provide executive-ready decision recommendation summary."
        if channel == "dashboard":
            return "Expose operational health, alerts, and next actions."
        return "Expose structured recommendation response for application integration."
