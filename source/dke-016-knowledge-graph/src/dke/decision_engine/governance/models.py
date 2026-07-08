from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class GovernancePolicy:
    policy_id: str
    name: str
    category: str
    priority: str
    version: str
    description: str
    enabled: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComplianceResult:
    policy: GovernancePolicy
    status: str
    score: float
    violations: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EthicsAssessment:
    fairness_score: float
    transparency_score: float
    accountability_score: float
    bias_risk: float
    explanation: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceEvaluation:
    alternative_id: str
    policy_results: tuple[ComplianceResult, ...]
    ethics_assessment: EthicsAssessment
    overall_score: float
    governance_status: str
    violations: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceMesh:
    policies: tuple[GovernancePolicy, ...]
    relationships: Mapping[str, tuple[str, ...]]
    evaluation_flow: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceDecisionPackage:
    evaluations: tuple[GovernanceEvaluation, ...]
    selected_evaluation: GovernanceEvaluation | None
    mesh: GovernanceMesh
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
