from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, round(value, 6)))


class RetrievalMode(str, Enum):
    EXACT = "exact"
    SEMANTIC = "semantic"
    GRAPH = "graph"
    HYBRID = "hybrid"
    EVIDENCE = "evidence"


class EvidenceType(str, Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    EVENT = "event"
    OBSERVATION = "observation"
    POLICY = "policy"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    BELONGS_TO = "belongs_to"
    CREATED_BY = "created_by"
    SUPPORTED_BY = "supported_by"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    MITIGATES = "mitigates"
    RESULTED_IN = "resulted_in"
    LEARNED_FROM = "learned_from"
    DECIDED = "decided"
    RELATED_TO = "related_to"
    CUSTOM = "custom"


@dataclass(frozen=True)
class RetrievalQuery:
    text: str = ""
    entities: tuple[str, ...] = ()
    mode: RetrievalMode = RetrievalMode.HYBRID
    max_results: int = 10
    max_depth: int = 2
    min_confidence: float = 0.0
    include_obsolete: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text and not self.entities:
            raise ValueError("RetrievalQuery requires text or entities")
        if self.max_results < 1:
            raise ValueError("max_results must be at least 1")
        if self.max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        if not 0 <= self.min_confidence <= 100:
            raise ValueError("min_confidence must be between 0 and 100")


@dataclass(frozen=True)
class KnowledgeNode:
    id: str
    name: str
    type: str = "unknown"
    aliases: tuple[str, ...] = ()
    facts: Mapping[str, Any] = field(default_factory=dict)
    confidence: float = 100.0
    authority: float = 50.0
    freshness: float = 50.0
    usage_frequency: float = 0.0
    obsolete: bool = False
    complete: bool = True
    supported: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("KnowledgeNode.id is required")
        if not self.name:
            raise ValueError("KnowledgeNode.name is required")
        for field_name in ("confidence", "authority", "freshness", "usage_frequency"):
            value = getattr(self, field_name)
            if not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be between 0 and 100")


@dataclass(frozen=True)
class KnowledgeRelationship:
    id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType | str = RelationshipType.RELATED_TO
    confidence: float = 100.0
    weight: float = 1.0
    evidence_ids: tuple[str, ...] = ()
    obsolete: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.source_id or not self.target_id:
            raise ValueError("relationship id, source_id, and target_id are required")
        if not 0 <= self.confidence <= 100:
            raise ValueError("relationship confidence must be between 0 and 100")
        if self.weight < 0:
            raise ValueError("relationship weight cannot be negative")


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    node_id: str | None = None
    relationship_id: str | None = None
    evidence_type: EvidenceType | str = EvidenceType.UNKNOWN
    source: str = ""
    excerpt: str = ""
    confidence: float = 100.0
    authority: float = 50.0
    created_at: datetime = field(default_factory=utc_now)
    obsolete: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("EvidenceItem.id is required")
        if not self.node_id and not self.relationship_id:
            raise ValueError("EvidenceItem requires node_id or relationship_id")
        for field_name in ("confidence", "authority"):
            value = getattr(self, field_name)
            if not 0 <= value <= 100:
                raise ValueError(f"{field_name} must be between 0 and 100")


@dataclass(frozen=True)
class RetrievalTrace:
    query: RetrievalQuery
    expanded_entities: tuple[str, ...] = ()
    semantic_node_ids: tuple[str, ...] = ()
    graph_node_ids: tuple[str, ...] = ()
    filtered_node_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResult:
    node: KnowledgeNode
    score: float
    similarity: float = 0.0
    confidence: float = 0.0
    authority: float = 0.0
    freshness: float = 0.0
    connectivity: float = 0.0
    usage_frequency: float = 0.0
    evidence: tuple[EvidenceItem, ...] = ()
    relationships: tuple[KnowledgeRelationship, ...] = ()
    trace: RetrievalTrace | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "score", clamp_score(self.score))


@dataclass(frozen=True)
class ContextPackage:
    query: RetrievalQuery
    entities: tuple[str, ...]
    facts: tuple[KnowledgeNode, ...]
    relationships: tuple[KnowledgeRelationship, ...]
    evidence: tuple[EvidenceItem, ...]
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "confidence", clamp_score(self.confidence))
