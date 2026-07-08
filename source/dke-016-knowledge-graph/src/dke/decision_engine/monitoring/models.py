from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class MonitoringMetric:
    metric_id: str
    name: str
    value: float
    status: str
    threshold: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionAlert:
    alert_id: str
    alert_type: str
    severity: str
    message: str
    related_metric: str
    recommended_action: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionHealth:
    alternative_id: str
    health_score: float
    workflow_status: str
    risk_drift: float
    confidence_drift: float
    governance_drift: float
    metrics: tuple[MonitoringMetric, ...]
    alerts: tuple[DecisionAlert, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MonitoringDecisionPackage:
    monitoring_results: tuple[DecisionHealth, ...]
    selected_monitoring: DecisionHealth | None
    monitoring_strategy: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
