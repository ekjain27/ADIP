from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class DecisionVersion:
    version_id: str
    decision_id: str
    version_number: int
    created_at: str
    parent_version: str | None
    status: str
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionChange:
    change_id: str
    change_type: str
    previous_value: str
    new_value: str
    reason: str
    source_module: str
    timestamp: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineEvent:
    event_id: str
    event_type: str
    timestamp: str
    description: str
    related_version: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RollbackPoint:
    rollback_id: str
    target_version: str
    reason: str
    created_at: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalLineageLedger:
    versions: tuple[DecisionVersion, ...]
    changes: tuple[DecisionChange, ...]
    timeline: tuple[TimelineEvent, ...]
    rollback_points: tuple[RollbackPoint, ...]
    active_version: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalDecision:
    alternative_id: str
    ledger: TemporalLineageLedger
    evolution_summary: str
    stability_score: float
    change_frequency: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalDecisionPackage:
    temporal_results: tuple[TemporalDecision, ...]
    selected_result: TemporalDecision | None
    timeline_summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
