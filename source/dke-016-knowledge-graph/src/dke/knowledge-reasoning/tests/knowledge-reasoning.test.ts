import assert from "node:assert/strict";
import test from "node:test";
import {
  createKnowledgeReasoningModule,
  GraphEdge,
  GraphNode,
  InMemoryGraphReadAdapter,
  KnowledgeGraphReadAdapter,
  KnowledgeGraphReadRepository,
  ReasoningValidationError
} from "../index.js";

const nodes = (): GraphNode[] => [
  { id: "supplier", canonicalName: "Supplier A", type: "Supplier" },
  { id: "factory", canonicalName: "Factory B", type: "Factory" },
  { id: "product", canonicalName: "Product C", type: "Product" },
  { id: "auto", canonicalName: "AutomobileCompany", type: "Class" },
  { id: "manufacturer", canonicalName: "Manufacturer", type: "Class" },
  { id: "company", canonicalName: "Company", type: "Class" },
  { id: "hidden", canonicalName: "Hidden Node", type: "Secret", visibility: { hidden: true } }
];

const baseEdges = (): GraphEdge[] => [
  { id: "e1", sourceNodeId: "supplier", targetNodeId: "factory", type: "SUPPLIES", confidence: 0.9, evidenceConfidence: 0.8, evidenceIds: ["ev1"] },
  { id: "e2", sourceNodeId: "factory", targetNodeId: "product", type: "PRODUCES", confidence: 0.8, evidenceConfidence: 0.9, evidenceIds: ["ev2"] },
  { id: "e3", sourceNodeId: "auto", targetNodeId: "manufacturer", type: "IS_A", confidence: 0.95 },
  { id: "e4", sourceNodeId: "manufacturer", targetNodeId: "company", type: "IS_A", confidence: 0.9 },
  { id: "expired", sourceNodeId: "supplier", targetNodeId: "product", type: "SUPPLIES", confidence: 1, validTo: "2020-01-01T00:00:00.000Z" },
  { id: "hidden-edge", sourceNodeId: "supplier", targetNodeId: "hidden", type: "SUPPLIES", confidence: 1 }
];

test("direct reasoning finds accessible direct paths", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 1 });
  assert.equal(result.paths.length, 1);
  assert.equal(result.paths[0].relationshipTypes[0], "SUPPLIES");
});

test("multi-hop reasoning applies configurable deterministic rules without graph mutation", async () => {
  const graph = new InMemoryGraphReadAdapter({ nodes: nodes(), edges: baseEdges() });
  const module = createKnowledgeReasoningModule({ graph });
  const before = await graph.getEdgesByNodeId("supplier");
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 2, minConfidence: 0.1 });
  const affects = result.conclusions.find((conclusion) => conclusion.relationshipType === "AFFECTS");
  const after = await graph.getEdgesByNodeId("supplier");
  assert.ok(affects);
  assert.equal(affects.sourceNodeId, "supplier");
  assert.equal(affects.targetNodeId, "product");
  assert.equal(after.length, before.length);
});

test("DKE-017 adapts DKE-016 graph repository through read-only public API", async () => {
  const repository: KnowledgeGraphReadRepository = {
    async getNodeById(id) {
      return (
        [
          { id: "supplier", canonicalName: "Supplier A", type: "supplier", aliases: ["Supplier Alpha"], attributes: { region: "NA" }, confidence: 0.95, sourceIds: ["source-1"] },
          { id: "factory", canonicalName: "Factory B", type: "factory", aliases: [], attributes: {}, confidence: 0.9, sourceIds: [] }
        ].find((node) => node.id === id) ?? null
      );
    },
    async getNodeByCanonicalName(canonicalName) {
      return canonicalName === "Supplier A" ? this.getNodeById("supplier") : null;
    },
    async getNeighbors(nodeId) {
      return nodeId === "supplier" ? [(await this.getNodeById("factory"))!] : [];
    },
    async getEdgesBySourceNode(sourceNodeId) {
      return sourceNodeId === "supplier"
        ? [
            {
              id: "kg-edge-1",
              sourceNodeId: "supplier",
              targetNodeId: "factory",
              relationType: "supplies",
              weight: 0.7,
              confidence: 0.8,
              evidenceIds: ["ev-kg"],
              temporalScope: { validFrom: "2024-01-01T00:00:00.000Z", validTo: null }
            }
          ]
        : [];
    },
    async getEdgesByTargetNode(targetNodeId) {
      return targetNodeId === "factory" ? this.getEdgesBySourceNode("supplier") : [];
    }
  };
  const graph = new KnowledgeGraphReadAdapter(repository);
  const module = createKnowledgeReasoningModule({ graph });
  const result = await module.service.reason({ sourceCanonicalName: "Supplier A", maxDepth: 1 });
  assert.equal(result.paths.length, 1);
  assert.equal(result.paths[0].nodes[0].labels?.[0], "Supplier Alpha");
  assert.equal(result.paths[0].nodes[0].properties?.region, "NA");
  assert.equal(result.paths[0].edges[0].type, "SUPPLIES");
});

test("confidence propagation multiplies path, rule, evidence, temporal, and conflict terms", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 2, includeConflicts: false });
  const affects = result.conclusions.find((conclusion) => conclusion.relationshipType === "AFFECTS");
  assert.ok(affects);
  assert.equal(Number(affects.confidence.toFixed(4)), 0.4925);
});

test("ontology reasoning returns inherited class conclusions", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "auto", maxDepth: 2 });
  assert.ok(result.conclusions.some((conclusion) => conclusion.relationshipType === "INHERITS_FROM" && conclusion.targetNodeId === "company"));
});

test("temporal reasoning ignores expired relationships and rejects invalid intervals", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "supplier", reasoningDate: "2024-01-01T00:00:00.000Z", maxDepth: 1 });
  assert.equal(result.paths.some((path) => path.edges.some((edge) => edge.id === "expired")), false);
  const invalid = createKnowledgeReasoningModule({
    nodes: nodes(),
    edges: [{ id: "bad", sourceNodeId: "supplier", targetNodeId: "factory", type: "SUPPLIES", validFrom: "2025-01-01", validTo: "2024-01-01" }]
  });
  await assert.rejects(() => invalid.service.reason({ sourceNodeId: "supplier" }), /validFrom after validTo/);
});

test("conflict detection detects contradictory relationships and temporal overlap", async () => {
  const module = createKnowledgeReasoningModule({
    nodes: nodes(),
    edges: [
      ...baseEdges(),
      { id: "c1", sourceNodeId: "supplier", targetNodeId: "factory", type: "DOES_NOT_SUPPLY", confidence: 0.9, validFrom: "2024-01-01", validTo: "2026-01-01" },
      { id: "c2", sourceNodeId: "supplier", targetNodeId: "factory", type: "SUPPLIES", confidence: 0.2, validFrom: "2025-01-01", validTo: "2027-01-01" }
    ]
  });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 1, reasoningDate: "2025-06-01" });
  assert.ok(result.conflicts.some((conflict) => conflict.type === "CONTRADICTORY_RELATIONSHIP"));
  assert.ok(result.conflicts.some((conflict) => conflict.type === "TEMPORAL_OVERLAP"));
  assert.ok(result.conflicts.some((conflict) => conflict.type === "CONFIDENCE_DISAGREEMENT"));
});

test("missing-link suggestions are returned only as suggestions", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 2, minConfidence: 0.4 });
  assert.equal(result.missingLinkSuggestions.length, 1);
  assert.equal(result.missingLinkSuggestions[0].relationshipType, "AFFECTS");
});

test("reasoning ranking prefers higher confidence paths", async () => {
  const module = createKnowledgeReasoningModule({
    nodes: [...nodes(), { id: "alt", canonicalName: "Alt Factory", type: "Factory" }],
    edges: [
      ...baseEdges(),
      { id: "a1", sourceNodeId: "supplier", targetNodeId: "alt", type: "SUPPLIES", confidence: 0.2 },
      { id: "a2", sourceNodeId: "alt", targetNodeId: "product", type: "PRODUCES", confidence: 0.2 }
    ]
  });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 2 });
  assert.equal(result.paths[0].confidence, 0.9);
  assert.ok(result.paths[0].confidence >= result.paths[1].confidence);
});

test("explanation generation includes steps, rules, evidence, and confidence evolution", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.controller.explain({ sourceNodeId: "supplier", maxDepth: 2 });
  assert.ok(result.steps.length > 0);
  assert.ok(result.appliedRuleIds.includes("rule_supplies_produces_affects"));
  assert.deepEqual([...result.evidenceIds].sort(), ["ev1", "ev2"]);
  assert.ok(result.confidenceEvolution.length > 0);
});

test("empty graph and invalid queries are handled with typed validation", async () => {
  const module = createKnowledgeReasoningModule();
  await assert.rejects(() => module.service.reason({ sourceNodeId: "missing" }), /source node was not found/);
  await assert.rejects(() => module.service.reason({}), ReasoningValidationError);
});

test("cycle prevention and depth limit keep traversal finite", async () => {
  const module = createKnowledgeReasoningModule({
    nodes: nodes(),
    edges: [...baseEdges(), { id: "cycle", sourceNodeId: "factory", targetNodeId: "supplier", type: "SUPPLIES", confidence: 1 }]
  });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 3 });
  assert.equal(result.paths.some((path) => path.nodes.filter((node) => node.id === "supplier").length > 1), false);
  await assert.rejects(() => module.service.reason({ sourceNodeId: "supplier", maxDepth: 0 }), ReasoningValidationError);
});

test("security filtering avoids hidden nodes and inaccessible evidence", async () => {
  const module = createKnowledgeReasoningModule({ nodes: nodes(), edges: baseEdges() });
  const result = await module.service.reason({ sourceNodeId: "supplier", maxDepth: 1, visibility: { allowedEvidenceIds: ["ev1"] } });
  assert.equal(result.paths.some((path) => path.nodes.some((node) => node.id === "hidden")), false);
  assert.equal(result.paths.every((path) => path.edges.every((edge) => !edge.evidenceIds?.length || edge.evidenceIds.includes("ev1"))), true);
});
