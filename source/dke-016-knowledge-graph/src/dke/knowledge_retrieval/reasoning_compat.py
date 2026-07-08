from __future__ import annotations

from typing import Any

from .models import ContextPackage, EvidenceItem, KnowledgeNode, KnowledgeRelationship


class DKE017ContextAdapter:
    def to_reasoning_input(self, context: ContextPackage) -> dict[str, Any]:
        return context_to_reasoning_input(context)


def context_to_reasoning_input(context: ContextPackage) -> dict[str, Any]:
    return {
        "query": {
            "text": context.query.text,
            "entities": list(context.query.entities),
            "mode": context.query.mode.value,
            "max_depth": context.query.max_depth,
            "min_confidence": context.query.min_confidence,
        },
        "entities": list(context.entities),
        "facts": [_node_to_dict(node) for node in context.facts],
        "relationships": [_relationship_to_dict(relationship) for relationship in context.relationships],
        "evidence": [_evidence_to_dict(item) for item in context.evidence],
        "confidence": context.confidence,
        "metadata": {
            "source_module": "DKE-018",
            "target_module": "DKE-017",
            "result_count": context.metadata.get("result_count", len(context.facts)),
        },
    }


def _node_to_dict(node: KnowledgeNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "canonicalName": node.name,
        "type": node.type,
        "labels": list(node.aliases),
        "properties": dict(node.facts),
        "confidence": node.confidence,
    }


def _relationship_to_dict(relationship: KnowledgeRelationship) -> dict[str, Any]:
    relationship_type = getattr(relationship.relationship_type, "value", relationship.relationship_type)
    return {
        "id": relationship.id,
        "sourceNodeId": relationship.source_id,
        "targetNodeId": relationship.target_id,
        "type": str(relationship_type),
        "confidence": relationship.confidence,
        "evidenceIds": list(relationship.evidence_ids),
    }


def _evidence_to_dict(item: EvidenceItem) -> dict[str, Any]:
    evidence_type = getattr(item.evidence_type, "value", item.evidence_type)
    return {
        "id": item.id,
        "nodeId": item.node_id,
        "relationshipId": item.relationship_id,
        "type": str(evidence_type),
        "source": item.source,
        "excerpt": item.excerpt,
        "confidence": item.confidence,
    }
