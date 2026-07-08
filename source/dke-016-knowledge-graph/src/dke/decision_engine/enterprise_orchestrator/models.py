from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class DecisionManifest:
    manifest_id: str
    alternative_id: str
    decision_title: str
    decision_summary: str
    recommendation_priority: str
    governance_status: str
    monitoring_status: str
    workflow_status: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LifecycleState:
    state_id: str
    current_stage: str
    completed_stages: tuple[str, ...]
    pending_stages: tuple[str, ...]
    blocked_stages: tuple[str, ...]
    readiness_score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnterpriseDecision:
    alternative_id: str
    manifest: DecisionManifest
    lifecycle_state: LifecycleState
    readiness_score: float
    enterprise_status: str
    final_recommendation: str
    next_actions: tuple[str, ...]
    audit_notes: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnterpriseDecisionPackage:
    enterprise_decisions: tuple[EnterpriseDecision, ...]
    selected_enterprise_decision: EnterpriseDecision | None
    orchestration_strategy: str
    lifecycle_summary: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
