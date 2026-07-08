# DIE-013 Decision Provenance Graph Engine

DIE-013 consumes a `StrategicPlanDecisionPackage` from DIE-012 and produces a `DecisionProvenancePackage`.

## Decision Provenance Graph

The Decision Provenance Graph, or DPG, is a deterministic directed acyclic graph that records how a final decision was produced. It spans the platform path from research and knowledge through evidence, reasoning, alternatives, evaluation, ranking, simulation, optimization, uncertainty, scenario analysis, learning, strategic planning, and final decision.

## Graph Architecture

Each `ProvenanceNode` stores origin, source module, confidence, timestamp, parent references, child references, and metadata. Each `ProvenanceEdge` stores relationship type, weight, confidence, reason, and propagation metadata.

The graph is built manually with no external graph library. Validation enforces node uniqueness, edge uniqueness, no cycles, connectedness, a single root, a single terminal node, valid confidence values, and valid references.

## Confidence, Lineage, Traceability, and Audit

`ConfidencePropagator` deterministically updates downstream confidence from parent confidence, edge confidence, and edge weight. `LineageTracker` creates an ordered decision history and readable summary. `DecisionProvenanceEngine` computes traceability scores and audit summaries for every strategic plan.

## Example

```python
from decision_engine.provenance import DecisionProvenanceEngine

provenance_package = DecisionProvenanceEngine().build(strategic_plan_package)
selected_graph = provenance_package.selected_provenance.graph
```

Future graph reasoners, temporal graph engines, graph database adapters, and LLM graph explorers can plug in by replacing factories, builders, validators, propagators, or trackers without changing the public API.
