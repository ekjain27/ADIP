from __future__ import annotations

from typing import Sequence

from .models import ContextPackage, EvidenceItem, KnowledgeRelationship, RetrievalQuery, RetrievalResult, RetrievalTrace, clamp_score


class ContextBuilder:
    def build(
        self,
        query: RetrievalQuery,
        entities: Sequence[str],
        results: Sequence[RetrievalResult],
        trace: RetrievalTrace,
    ) -> ContextPackage:
        facts = tuple(result.node for result in results)
        relationships: dict[str, KnowledgeRelationship] = {}
        evidence: dict[str, EvidenceItem] = {}
        for result in results:
            for relationship in result.relationships:
                relationships[relationship.id] = relationship
            for item in result.evidence:
                evidence[item.id] = item
        confidence = 0.0 if not results else sum(result.score for result in results) / len(results)
        return ContextPackage(
            query=query,
            entities=tuple(dict.fromkeys(entities)),
            facts=facts,
            relationships=tuple(sorted(relationships.values(), key=lambda item: item.id)),
            evidence=tuple(sorted(evidence.values(), key=lambda item: item.id)),
            confidence=clamp_score(confidence),
            metadata={"trace": trace, "result_count": len(results), "retrieval_results": tuple(results), "engine": "DKE-018"},
        )
