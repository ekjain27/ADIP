import pytest

from decision_engine.alternatives import AlternativeGenerator
from decision_engine.core import DIECore
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.explanation import ExplanationGenerator
from decision_engine.learning import DecisionLearningEngine
from decision_engine.multi_objective import MultiObjectiveEngine
from decision_engine.optimization import OptimizationEngine
from decision_engine.provenance import (
    ConfidencePropagator,
    DecisionProvenanceEngine,
    DecisionProvenanceGraph,
    EdgeFactory,
    GraphBuilder,
    GraphValidator,
    LineageTracker,
    NodeFactory,
    ProvenancePackageBuilder,
)
from decision_engine.ranking import DecisionRanker
from decision_engine.scenario_analysis import DecisionScenarioEngine
from decision_engine.simulation import DecisionSimulator
from decision_engine.strategic_planning import StrategicPlanningEngine
from decision_engine.uncertainty import UncertaintyEngine


def test_node_creation():
    nodes = NodeFactory().create_nodes(_strategic_plan())
    assert len(nodes) == 14
    assert nodes[0].node_type == "research"
    assert all(0.0 <= node.confidence <= 1.0 for node in nodes)


def test_edge_creation():
    nodes = NodeFactory().create_nodes(_strategic_plan())
    edges = EdgeFactory().create_edges(nodes)
    assert len(edges) == len(nodes) - 1
    assert edges[0].relationship == "generated_from"
    assert all(0.0 <= edge.confidence <= 1.0 for edge in edges)


def test_graph_construction():
    graph = GraphBuilder().build(_strategic_plan())
    assert graph.nodes
    assert graph.edges
    assert graph.root_node == graph.nodes[0].node_id
    assert graph.terminal_node == graph.nodes[-1].node_id


def test_graph_is_dag():
    graph = GraphBuilder().build(_strategic_plan())
    assert not GraphValidator().has_cycle(graph)


def test_single_root():
    graph = GraphBuilder().build(_strategic_plan())
    targets = {edge.target_node for edge in graph.edges}
    roots = [node.node_id for node in graph.nodes if node.node_id not in targets]
    assert roots == [graph.root_node]


def test_single_terminal_node():
    graph = GraphBuilder().build(_strategic_plan())
    sources = {edge.source_node for edge in graph.edges}
    terminals = [node.node_id for node in graph.nodes if node.node_id not in sources]
    assert terminals == [graph.terminal_node]


def test_confidence_propagation():
    nodes = NodeFactory().create_nodes(_strategic_plan())
    edges = EdgeFactory().create_edges(nodes)
    propagated = ConfidencePropagator().propagate(nodes, edges)
    assert len(propagated) == len(nodes)
    assert all(0.0 <= node.confidence <= 1.0 for node in propagated)


def test_lineage_generation():
    graph = GraphBuilder().build(_strategic_plan())
    lineage = LineageTracker().track(_strategic_plan().alternative_id, graph)
    assert lineage.ordered_nodes[0] == graph.root_node
    assert lineage.ordered_nodes[-1] == graph.terminal_node
    assert lineage.ordered_edges


def test_validator_catches_cycles():
    graph = GraphBuilder().build(_strategic_plan())
    cycle_edge = type(graph.edges[0])(
        "edge-cycle",
        graph.terminal_node,
        graph.root_node,
        "derived_from",
        0.9,
        0.9,
        "forced cycle",
    )
    bad_graph = DecisionProvenanceGraph(graph.nodes, (*graph.edges, cycle_edge), graph.root_node, graph.terminal_node, graph.metadata)
    with pytest.raises(ValueError, match="cycle"):
        GraphValidator().validate_graph(bad_graph)


def test_validator_catches_disconnected_graph():
    graph = GraphBuilder().build(_strategic_plan())
    isolated = type(graph.nodes[0])(
        "isolated",
        "evidence",
        "Isolated",
        "Disconnected node",
        "test",
        0.8,
        graph.nodes[0].timestamp,
    )
    bad_graph = DecisionProvenanceGraph((*graph.nodes, isolated), graph.edges, graph.root_node, graph.terminal_node, graph.metadata)
    with pytest.raises(ValueError, match="disconnected"):
        GraphValidator().validate_graph(bad_graph)


def test_package_builder():
    package = DecisionProvenanceEngine().build(_strategic_package())
    rebuilt = ProvenancePackageBuilder().build(package.provenance_results, package.selected_provenance)
    assert rebuilt.selected_provenance == package.selected_provenance
    assert rebuilt.metadata["module"] == "DIE-013"


def test_integration_die_001_to_die_013():
    provenance_package = DecisionProvenanceEngine().build(_strategic_package())
    assert provenance_package.selected_provenance is not None
    assert provenance_package.selected_provenance.traceability_score > 0.0
    assert provenance_package.graph_statistics["graph_count"] >= 1


def _strategic_plan():
    return _strategic_package().selected_plan


def _strategic_package():
    learning_package = DecisionLearningEngine().learn(_scenario_package())
    multi_objective_package = MultiObjectiveEngine().optimize(learning_package)
    return StrategicPlanningEngine().plan(multi_objective_package)


def _scenario_package():
    decision_package = DIECore().process(
        {
            "query": "Select a reliable technical vendor with low risk and policy alignment",
            "semantic_results": [
                {"id": "e1", "text": "Vendor A has strong reliability and measurable value.", "confidence": 0.9},
                {"id": "e2", "text": "Vendor B has compliance concerns and uncertain delivery.", "confidence": 0.65},
            ],
            "metadata": {"constraints": [{"type": "policy", "severity": "medium"}]},
        }
    )
    alternative_package = AlternativeGenerator().generate(decision_package.decision_state)
    evaluated_package = DecisionEvaluator().evaluate(alternative_package)
    ranked_package = DecisionRanker().rank(evaluated_package)
    simulation_package = DecisionSimulator().simulate(ranked_package)
    explanation_package = ExplanationGenerator().explain(simulation_package)
    optimized_package = OptimizationEngine().optimize(explanation_package)
    uncertainty_package = UncertaintyEngine().analyze(optimized_package)
    return DecisionScenarioEngine().analyze(uncertainty_package)
