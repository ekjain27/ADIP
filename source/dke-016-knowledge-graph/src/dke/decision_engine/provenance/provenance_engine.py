from __future__ import annotations

import logging

from decision_engine.core.models import clamp_confidence
from decision_engine.strategic_planning import StrategicPlan, StrategicPlanDecisionPackage

from .graph_builder import GraphBuilder
from .lineage_tracker import LineageTracker
from .models import DecisionProvenance
from .provenance_package import ProvenancePackageBuilder

logger = logging.getLogger(__name__)


class DecisionProvenanceEngine:
    def __init__(
        self,
        graph_builder: GraphBuilder | None = None,
        lineage_tracker: LineageTracker | None = None,
        package_builder: ProvenancePackageBuilder | None = None,
    ) -> None:
        self.graph_builder = graph_builder or GraphBuilder()
        self.lineage_tracker = lineage_tracker or LineageTracker()
        self.package_builder = package_builder or ProvenancePackageBuilder()

    def build(self, strategy_package: StrategicPlanDecisionPackage):
        if not isinstance(strategy_package, StrategicPlanDecisionPackage):
            raise ValueError("DecisionProvenanceEngine.build requires a StrategicPlanDecisionPackage")
        logger.info("Building deterministic decision provenance graphs")
        results = tuple(self._build_plan(plan) for plan in strategy_package.strategic_plans)
        selected = self._selected(results, strategy_package.selected_plan)
        statistics = self.package_builder._statistics(results)
        return self.package_builder.build(
            results,
            selected,
            graph_statistics=statistics,
            metadata={
                "source_planning_strategy": strategy_package.planning_strategy,
                "strategic_plan_count": len(strategy_package.strategic_plans),
            },
        )

    def _build_plan(self, plan: StrategicPlan) -> DecisionProvenance:
        graph = self.graph_builder.build(plan)
        lineage = self.lineage_tracker.track(plan.alternative_id, graph)
        traceability_score = self._traceability_score(graph, lineage)
        return DecisionProvenance(
            alternative_id=plan.alternative_id,
            graph=graph,
            lineage=lineage,
            traceability_score=traceability_score,
            audit_summary=f"DPG audit confirms {len(graph.nodes)} traceable nodes and {len(graph.edges)} traceable edges for {plan.alternative_id}.",
            metadata={"graph_type": graph.metadata.get("graph_type", "Decision Provenance Graph")},
        )

    def _selected(self, results: tuple[DecisionProvenance, ...], selected_plan: StrategicPlan | None) -> DecisionProvenance | None:
        if not results:
            return None
        if selected_plan is not None:
            for result in results:
                if result.alternative_id == selected_plan.alternative_id:
                    return result
        return max(results, key=lambda result: (result.traceability_score, result.alternative_id))

    def _traceability_score(self, graph, lineage) -> float:
        node_coverage = len(lineage.ordered_nodes) / len(graph.nodes) if graph.nodes else 0.0
        edge_coverage = len(lineage.ordered_edges) / len(graph.edges) if graph.edges else 0.0
        return clamp_confidence((node_coverage * 0.40) + (edge_coverage * 0.30) + (lineage.confidence * 0.30))
