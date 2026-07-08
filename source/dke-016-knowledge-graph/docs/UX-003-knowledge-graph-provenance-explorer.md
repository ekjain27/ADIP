# UX-003 Knowledge Graph & Provenance Explorer

## Purpose

UX-003 replaces the Knowledge Graph & Provenance placeholder with an application-layer explorer for graph and provenance outputs. It renders backend-owned knowledge graph, decision provenance graph, temporal lineage, governance relationship, and traceability data without implementing graph reasoning in the UI.

## Page Structure

- Explorer header with graph status, selected source, node/edge counts, refresh timestamp, and actions.
- Graph visualization panel with nodes, edges, relationship labels, and selected node/edge state.
- Graph filters for node type, relationship type, confidence range, governance status, time period, and provenance source.
- Node inspector for selected node metadata.
- Edge inspector for selected relationship metadata.
- Provenance timeline for extraction, fusion, state update, evaluation, ranking, governance, and recommendation events.

## Adapter Boundary

UX-003 uses `KnowledgeGraphProvenanceClient` in `src/ux/knowledge-graph-provenance/client.ts`.

Adapter methods:

- `getGraphSummary()`
- `getGraphData()`
- `getProvenanceTimeline()`
- `getNodeDetails(nodeId)`
- `getEdgeDetails(edgeId)`
- `refreshGraph()`
- `loadDecisionProvenance(decisionId)`

## Supported Interactions

- Clicking a graph node updates the Node Inspector.
- Clicking a graph edge updates the Edge Inspector.
- Refresh Graph calls the adapter and updates status/timestamp.
- Load Provenance calls the adapter and updates source/status/timeline.
- Reset View clears selection back to the default node/edge and restores filters.
- Filters update visible state in the UX layer without performing backend graph reasoning.

## Fallback Data Policy

Live frontend graph/provenance endpoints were not clear in the current repository. UX-003 therefore uses deterministic UX-layer fallback graph data isolated behind the adapter. Future endpoint wiring should replace only the adapter internals.

## Intentionally Not Implemented In UI

- graph reasoning
- provenance construction
- lineage ledger generation
- governance evaluation
- ranking or recommendation algorithms
- backend mutation

## UX-004 Extension Notes

UX-004 explainability should consume backend explanation outputs through its own adapter and can link from UX-003 using node IDs, edge IDs, provenance references, decision IDs, and recommendation IDs.
