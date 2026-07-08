from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable, Mapping, Sequence

from .cache import RetrievalCache
from .context_builder import ContextBuilder
from .evidence_collector import EvidenceCollector
from .filters import RetrievalFilter
from .graph_search import InMemoryGraphSearch
from .interfaces import EntityExpansionProvider, KnowledgeStore
from .models import (
    ContextPackage,
    EvidenceItem,
    KnowledgeNode,
    KnowledgeRelationship,
    RetrievalMode,
    RetrievalQuery,
    RetrievalResult,
    RetrievalTrace,
)
from .ranking import WeightedRanker
from .semantic_search import InMemorySemanticSearch, tokenize


class InMemoryKnowledgeStore:
    def __init__(
        self,
        nodes: Iterable[KnowledgeNode] = (),
        relationships: Iterable[KnowledgeRelationship] = (),
        evidence: Iterable[EvidenceItem] = (),
    ) -> None:
        self._nodes = {node.id: node for node in nodes}
        self._relationships = {relationship.id: relationship for relationship in relationships}
        self._evidence = {item.id: item for item in evidence}

    def all_nodes(self) -> Sequence[KnowledgeNode]:
        return tuple(sorted(self._nodes.values(), key=lambda node: node.id))

    def all_relationships(self) -> Sequence[KnowledgeRelationship]:
        return tuple(sorted(self._relationships.values(), key=lambda relationship: relationship.id))

    def all_evidence(self) -> Sequence[EvidenceItem]:
        return tuple(sorted(self._evidence.values(), key=lambda item: item.id))

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self._nodes.get(node_id)

    def find_node_by_name(self, name: str) -> KnowledgeNode | None:
        normalized = name.lower()
        for node in self._nodes.values():
            names = {node.name.lower(), *(alias.lower() for alias in node.aliases)}
            if normalized in names:
                return node
        return None

    def relationships_for_node(self, node_id: str) -> Sequence[KnowledgeRelationship]:
        return tuple(
            sorted(
                (
                    relationship
                    for relationship in self._relationships.values()
                    if relationship.source_id == node_id or relationship.target_id == node_id
                ),
                key=lambda relationship: relationship.id,
            )
        )

    def evidence_for_node(self, node_id: str) -> Sequence[EvidenceItem]:
        return tuple(sorted((item for item in self._evidence.values() if item.node_id == node_id), key=lambda item: item.id))

    def evidence_for_relationship(self, relationship_id: str) -> Sequence[EvidenceItem]:
        return tuple(
            sorted((item for item in self._evidence.values() if item.relationship_id == relationship_id), key=lambda item: item.id)
        )


class StaticEntityExpansionProvider:
    def __init__(self, aliases: Mapping[str, Sequence[str]] | None = None, store: KnowledgeStore | None = None) -> None:
        self._aliases = {key.lower(): tuple(value) for key, value in (aliases or {}).items()}
        self._store = store

    def expand_entity(self, entity: str) -> Sequence[str]:
        expanded = [entity]
        expanded.extend(self._aliases.get(entity.lower(), ()))
        if self._store is not None:
            node = self._store.find_node_by_name(entity)
            if node is not None:
                expanded.extend(node.aliases)
                expanded.append(node.name)
        return tuple(dict.fromkeys(item for item in expanded if item))


class KnowledgeRetrievalEngine:
    def __init__(
        self,
        store: KnowledgeStore | None = None,
        entity_expander: EntityExpansionProvider | None = None,
        cache: RetrievalCache[ContextPackage] | None = None,
    ) -> None:
        self.store = store or InMemoryKnowledgeStore()
        self.entity_expander = entity_expander or StaticEntityExpansionProvider(store=self.store)
        self.semantic_search = InMemorySemanticSearch(self.store)
        self.graph_search = InMemoryGraphSearch(self.store)
        self.evidence_collector = EvidenceCollector(self.store)
        self.ranker = WeightedRanker()
        self.filter = RetrievalFilter()
        self.context_builder = ContextBuilder()
        self.cache = cache or RetrievalCache()

    def retrieve(self, query: str | RetrievalQuery) -> Sequence[RetrievalResult]:
        retrieval_query = self._coerce_query(query)
        context = self.retrieve_context(retrieval_query)
        stored_results = context.metadata.get("retrieval_results")
        trace = context.metadata.get("trace")
        if isinstance(stored_results, tuple) and all(isinstance(result, RetrievalResult) for result in stored_results):
            return tuple(replace(result, trace=trace if isinstance(trace, RetrievalTrace) else result.trace) for result in stored_results)
        return tuple(
            RetrievalResult(
                node=node,
                score=node.confidence,
                confidence=node.confidence,
                authority=node.authority,
                freshness=node.freshness,
                usage_frequency=node.usage_frequency,
                evidence=tuple(item for item in context.evidence if item.node_id == node.id),
                relationships=tuple(rel for rel in context.relationships if rel.source_id == node.id or rel.target_id == node.id),
                trace=trace if isinstance(trace, RetrievalTrace) else None,
            )
            for node in context.facts
        )

    def retrieve_context(self, query: str | RetrievalQuery) -> ContextPackage:
        retrieval_query = self._coerce_query(query)
        cache_key = repr(retrieval_query)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        entities = self._entities_for_query(retrieval_query)
        semantic_results: Sequence[RetrievalResult] = ()
        graph_results: Sequence[RetrievalResult] = ()
        if retrieval_query.mode in {RetrievalMode.SEMANTIC, RetrievalMode.HYBRID, RetrievalMode.EVIDENCE}:
            semantic_results = self.semantic_search.search(retrieval_query, entities)
        if retrieval_query.mode in {RetrievalMode.EXACT, RetrievalMode.GRAPH, RetrievalMode.HYBRID, RetrievalMode.EVIDENCE}:
            graph_results = self.graph_search.search(entities, retrieval_query.max_depth)

        merged = self._merge_results((*semantic_results, *graph_results))
        with_evidence = self._attach_evidence(merged)
        ranked = self.ranker.rank(with_evidence)
        filtered = self.filter.filter(ranked, retrieval_query)
        trace = RetrievalTrace(
            query=retrieval_query,
            expanded_entities=tuple(entities),
            semantic_node_ids=tuple(result.node.id for result in semantic_results),
            graph_node_ids=tuple(result.node.id for result in graph_results),
            filtered_node_ids=tuple(result.node.id for result in filtered),
            evidence_ids=tuple(item.id for result in filtered for item in result.evidence),
            steps=("entities_expanded", "semantic_search", "graph_search", "evidence_collected", "ranked", "filtered", "context_built"),
        )
        context = self.context_builder.build(retrieval_query, entities, filtered, trace)
        self.cache.set(cache_key, context)
        return context

    def retrieve_entity(self, entity: str) -> Sequence[RetrievalResult]:
        return self.retrieve(RetrievalQuery(entities=(entity,), mode=RetrievalMode.EXACT))

    def retrieve_related(self, node: str | KnowledgeNode) -> Sequence[KnowledgeNode]:
        node_id = node.id if isinstance(node, KnowledgeNode) else node
        return self.graph_search.related(node_id)

    def retrieve_evidence(self, query: str | RetrievalQuery) -> Sequence[EvidenceItem]:
        return self.retrieve_context(query).evidence

    def retrieve_subgraph(self, node: str | KnowledgeNode) -> tuple[Sequence[KnowledgeNode], Sequence[KnowledgeRelationship]]:
        node_id = node.id if isinstance(node, KnowledgeNode) else node
        return self.graph_search.subgraph(node_id)

    def expand_entity(self, entity: str) -> Sequence[str]:
        return self.entity_expander.expand_entity(entity)

    def _coerce_query(self, query: str | RetrievalQuery) -> RetrievalQuery:
        if isinstance(query, RetrievalQuery):
            return query
        return RetrievalQuery(text=query)

    def _entities_for_query(self, query: RetrievalQuery) -> tuple[str, ...]:
        entities = list(query.entities)
        if query.text:
            quoted = re.findall(r'"([^"]+)"', query.text)
            title_case = re.findall(r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*\b", query.text)
            entities.extend((*quoted, *title_case))
            if not entities:
                entities.extend(tokenize(query.text))
        expanded: list[str] = []
        for entity in entities:
            expanded.extend(self.expand_entity(entity))
        return tuple(dict.fromkeys(expanded))

    def _merge_results(self, results: Sequence[RetrievalResult]) -> Sequence[RetrievalResult]:
        merged: dict[str, RetrievalResult] = {}
        for result in results:
            existing = merged.get(result.node.id)
            if existing is None:
                merged[result.node.id] = result
                continue
            relationships = tuple({relationship.id: relationship for relationship in (*existing.relationships, *result.relationships)}.values())
            merged[result.node.id] = replace(
                existing,
                score=max(existing.score, result.score),
                similarity=max(existing.similarity, result.similarity),
                confidence=max(existing.confidence, result.confidence),
                authority=max(existing.authority, result.authority),
                freshness=max(existing.freshness, result.freshness),
                connectivity=max(existing.connectivity, result.connectivity),
                usage_frequency=max(existing.usage_frequency, result.usage_frequency),
                relationships=relationships,
            )
        return tuple(merged.values())

    def _attach_evidence(self, results: Sequence[RetrievalResult]) -> Sequence[RetrievalResult]:
        enriched = []
        for result in results:
            relationship_ids = tuple(relationship.id for relationship in result.relationships)
            evidence = self.evidence_collector.collect((result.node.id,), relationship_ids)
            enriched.append(replace(result, evidence=tuple(evidence)))
        return tuple(enriched)


_default_engine = KnowledgeRetrievalEngine()


def retrieve(query: str | RetrievalQuery) -> Sequence[RetrievalResult]:
    return _default_engine.retrieve(query)


def retrieve_entity(entity: str) -> Sequence[RetrievalResult]:
    return _default_engine.retrieve_entity(entity)


def retrieve_context(query: str | RetrievalQuery) -> ContextPackage:
    return _default_engine.retrieve_context(query)


def retrieve_related(node: str | KnowledgeNode) -> Sequence[KnowledgeNode]:
    return _default_engine.retrieve_related(node)


def retrieve_evidence(query: str | RetrievalQuery) -> Sequence[EvidenceItem]:
    return _default_engine.retrieve_evidence(query)


def retrieve_subgraph(node: str | KnowledgeNode) -> tuple[Sequence[KnowledgeNode], Sequence[KnowledgeRelationship]]:
    return _default_engine.retrieve_subgraph(node)


def expand_entity(entity: str) -> Sequence[str]:
    return _default_engine.expand_entity(entity)
