from __future__ import annotations

from typing import Any

from decision_engine.core.models import utc_now

from .graph_validator import GraphValidator
from .models import DecisionProvenance, DecisionProvenancePackage


class ProvenancePackageBuilder:
    def __init__(self, validator: GraphValidator | None = None) -> None:
        self.validator = validator or GraphValidator()

    def build(
        self,
        provenance_results: tuple[DecisionProvenance, ...],
        selected_provenance: DecisionProvenance | None,
        graph_statistics: dict[str, Any] | None = None,
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> DecisionProvenancePackage:
        for result in provenance_results:
            self.validator.validate_provenance(result)
        if provenance_results and selected_provenance is None:
            raise ValueError("selected provenance is required when provenance results exist")
        if not provenance_results and selected_provenance is not None:
            raise ValueError("selected provenance must be None when no provenance results exist")
        if selected_provenance is not None and selected_provenance not in provenance_results:
            raise ValueError("selected provenance must be present in provenance results")
        package_metadata = {
            "module": "DIE-013",
            "timestamp": utc_now().isoformat(),
            "source": "decision_engine.provenance",
        }
        package_metadata.update(metadata or {})
        stats = graph_statistics or self._statistics(provenance_results)
        return DecisionProvenancePackage(
            provenance_results=provenance_results,
            selected_provenance=selected_provenance,
            graph_statistics=stats,
            summary=summary or self._summary(provenance_results, selected_provenance),
            metadata=package_metadata,
        )

    def _statistics(self, results: tuple[DecisionProvenance, ...]) -> dict[str, Any]:
        total_nodes = sum(len(result.graph.nodes) for result in results)
        total_edges = sum(len(result.graph.edges) for result in results)
        return {
            "graph_count": len(results),
            "node_count": total_nodes,
            "edge_count": total_edges,
            "average_traceability": round(sum(result.traceability_score for result in results) / len(results), 6) if results else 0.0,
        }

    def _summary(self, results: tuple[DecisionProvenance, ...], selected: DecisionProvenance | None) -> str:
        if not results:
            return "No strategic plans were available for decision provenance."
        if selected is None:
            return f"Generated {len(results)} provenance graph(s), but no selected provenance is available."
        return f"Selected provenance for {selected.alternative_id} with traceability score {selected.traceability_score:.3f}."
