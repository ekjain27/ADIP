from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class RecommendationResponse:
    response_id: str
    alternative_id: str
    title: str
    summary: str
    recommendation: str
    priority: str
    confidence: float
    health_status: str
    alerts: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationDelivery:
    delivery_id: str
    channel: str
    audience: str
    format_type: str
    routing_reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationServicePackage:
    responses: tuple[RecommendationResponse, ...]
    selected_response: RecommendationResponse | None
    deliveries: tuple[RecommendationDelivery, ...]
    service_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
