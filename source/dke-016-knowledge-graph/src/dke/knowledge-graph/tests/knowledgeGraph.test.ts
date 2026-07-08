import {
  createKnowledgeGraphModule,
  EdgeService,
  EntityResolutionService,
  GraphConfidenceService,
  GraphConstructionService,
  GraphConstructionError,
  GraphEvidenceService,
  GraphIndexService,
  GraphValidationError,
  GraphValidationService,
  InMemoryEventPublisherAdapter,
  InMemoryMetricsAdapter,
  MemoryGraphRepository,
  NodeService,
  type GraphEdgeInput,
  type GraphNodeInput,
  type LoggerPort,
} from "../index.js";

type TestCase = { name: string; run: () => Promise<void> | void };

const tests: TestCase[] = [];

function test(name: string, run: TestCase["run"]): void {
  tests.push({ name, run });
}

function assert(condition: unknown, message: string): void {
  if (!condition) throw new Error(message);
}

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (actual !== expected) throw new Error(`${message}. Expected ${String(expected)}, got ${String(actual)}.`);
}

async function assertRejects(run: () => Promise<unknown>, expected: new (...args: never[]) => Error, expectedMessage: string): Promise<void> {
  try {
    await run();
  } catch (error) {
    if (!(error instanceof Error)) throw new Error("Expected an Error instance.");
    assert(error instanceof expected, `Expected ${expected.name}, got ${error.name}.`);
    assert(error.message.includes(expectedMessage), `Expected message containing "${expectedMessage}", got "${error.message}".`);
    return;
  }
  throw new Error("Expected operation to reject.");
}

class CapturingLogger implements LoggerPort {
  messages: string[] = [];
  debug(message: string): void { this.messages.push(`debug:${message}`); }
  info(message: string): void { this.messages.push(`info:${message}`); }
  warn(message: string): void { this.messages.push(`warn:${message}`); }
  error(message: string): void { this.messages.push(`error:${message}`); }
}

function makeServices() {
  const repository = new MemoryGraphRepository();
  const validation = new GraphValidationService();
  const resolution = new EntityResolutionService();
  const events = new InMemoryEventPublisherAdapter();
  const metrics = new InMemoryMetricsAdapter();
  const logger = new CapturingLogger();
  const nodes = new NodeService(repository, validation, resolution, events, metrics, logger);
  const edges = new EdgeService(repository, validation, events, metrics, logger);
  const evidence = new GraphEvidenceService(repository, validation, events, metrics, logger);
  const index = new GraphIndexService(repository);
  const construction = new GraphConstructionService(
    repository,
    validation,
    nodes,
    edges,
    evidence,
    events,
    metrics,
    logger,
  );
  return { repository, nodes, edges, evidence, index, construction, confidence: new GraphConfidenceService(), events, metrics, logger };
}

function node(id: string, canonicalName = id): GraphNodeInput {
  return {
    id,
    type: "concept",
    canonicalName,
    aliases: [],
    attributes: {},
    confidence: 0.9,
    sourceIds: ["source_1"],
  };
}

function edge(id: string, sourceNodeId: string, targetNodeId: string): GraphEdgeInput {
  return {
    id,
    sourceNodeId,
    targetNodeId,
    relationType: "related_to",
    weight: 1,
    confidence: 0.8,
    evidenceIds: [],
  };
}

test("composition root creates usable module", async () => {
  const module = createKnowledgeGraphModule({ logger: new CapturingLogger() });
  const result = await module.controller.createNode(node("node_root"));
  assertEqual(result.node.id, "node_root", "Factory-created controller should create nodes.");
});

test("logger port is used", async () => {
  const { nodes, logger } = makeServices();
  await nodes.createNode(node("node_log"));
  assert(logger.messages.some((message) => message.includes("Graph node created")), "Logger should receive service messages.");
});

test("node creation", async () => {
  const { nodes } = makeServices();
  const result = await nodes.createNode(node("node_1", "Decision Quality"));
  assertEqual(result.node.canonicalName, "Decision Quality", "Node should be created.");
  assertEqual(result.node.version, 1, "Created node should start at version 1.");
});

test("invalid node rejection and typed validation errors", async () => {
  const { nodes } = makeServices();
  await assertRejects(() => nodes.createNode({ ...node("node_bad"), canonicalName: " " }), GraphValidationError, "canonicalName cannot be empty");
});

test("edge creation", async () => {
  const { nodes, edges } = makeServices();
  await nodes.createNode(node("a"));
  await nodes.createNode(node("b"));
  const created = await edges.createEdge(edge("edge_1", "a", "b"));
  assertEqual(created.sourceNodeId, "a", "Edge source should be stored.");
});

test("invalid self-edge rejection", async () => {
  const { nodes, edges } = makeServices();
  await nodes.createNode(node("a"));
  await assertRejects(() => edges.createEdge(edge("edge_self", "a", "a")), GraphValidationError, "cannot connect a node to itself");
});

test("confidence calculation", () => {
  const { confidence } = makeServices();
  const score = confidence.relationshipConfidence({
    sourceReliability: 0.9,
    extractionConfidence: 0.8,
    ontologyMatch: 0.75,
    temporalValidity: 1,
    crossSourceAgreement: 0.5,
  });
  assertEqual(score, 0.27, "Confidence should multiply and round factors.");
});

test("duplicate entity resolution", async () => {
  const { nodes } = makeServices();
  await nodes.createNode({ ...node("node_a", "Acme Corporation"), aliases: ["Acme"] });
  const duplicate = await nodes.createNode({ ...node("node_b", "Acme"), aliases: ["Acme Corp"] });
  assertEqual(duplicate.merged, true, "Duplicate should be merged.");
  assertEqual(duplicate.node.id, "node_a", "Duplicate should merge into existing node.");
});

test("node merging", async () => {
  const { nodes } = makeServices();
  await nodes.createNode({ ...node("node_a", "Revenue Growth"), attributes: { owner: "Finance" } });
  const merged = await nodes.mergeNodes("node_a", {
    ...node("node_b", "Revenue Expansion"),
    aliases: ["Growth"],
    attributes: { horizon: "FY26" },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    version: 1,
  });
  assertEqual(merged.version, 2, "Merged node should increment version.");
  assertEqual(merged.attributes.horizon, "FY26", "Merged node should combine attributes.");
});

test("graph construction from payload and transaction commit on success", async () => {
  const { construction, repository } = makeServices();
  const result = await construction.construct({
    nodes: [node("a"), node("b")],
    edges: [edge("e", "a", "b")],
    evidence: [{ id: "ev", sourceId: "source_1", sourceType: "document", confidence: 0.9 }],
  });
  assertEqual(result.nodesCreated, 2, "Construction should create nodes.");
  assertEqual(result.edgesCreated, 1, "Construction should create edges.");
  assertEqual(result.evidenceCreated, 1, "Construction should create evidence.");
  assert(await repository.getNodeById("a"), "Committed transaction should preserve nodes.");
});

test("transaction rollback on failure", async () => {
  const { construction, repository } = makeServices();
  await assertRejects(
    () => construction.construct({
      nodes: [node("rollback_a")],
      edges: [edge("bad", "rollback_a", "missing")],
      evidence: [],
    }),
    GraphConstructionError,
    "Target node not found",
  );
  assertEqual(await repository.getNodeById("rollback_a"), null, "Rollback should remove created nodes.");
});

test("batch node creation", async () => {
  const { nodes } = makeServices();
  const result = await nodes.createNodes([node("batch_a"), node("batch_b")]);
  assertEqual(result.nodes.length, 2, "Batch node creation should return all nodes.");
});

test("batch edge creation", async () => {
  const { nodes, edges } = makeServices();
  await nodes.createNodes([node("a"), node("b"), node("c")]);
  const result = await edges.createEdges([edge("ab", "a", "b"), edge("bc", "b", "c")]);
  assertEqual(result.length, 2, "Batch edge creation should return all edges.");
});

test("event publishing", async () => {
  const { nodes, events } = makeServices();
  await nodes.createNode(node("event_node"));
  const stored = await events.listEvents();
  assert(stored.some((event) => event.type === "GraphNodeCreated"), "Node creation should publish an event.");
});

test("metrics tracking", async () => {
  const { nodes, metrics } = makeServices();
  await nodes.createNode(node("metric_node"));
  const snapshot = metrics.snapshot();
  assertEqual(snapshot.nodesCreated, 1, "Metrics should count created nodes.");
  assertEqual(snapshot.averageNodeConfidence, 0.9, "Metrics should track average node confidence.");
});

test("neighbor lookup", async () => {
  const { nodes, edges, index } = makeServices();
  await nodes.createNode(node("a"));
  await nodes.createNode(node("b"));
  await edges.createEdge(edge("e", "a", "b"));
  const neighbors = await index.getNeighbors("a");
  assertEqual(neighbors.length, 1, "Neighbor lookup should find connected node.");
  assertEqual(neighbors[0].id, "b", "Neighbor should be node b.");
});

test("path lookup", async () => {
  const { nodes, edges, index } = makeServices();
  await nodes.createNode(node("a"));
  await nodes.createNode(node("b"));
  await nodes.createNode(node("c"));
  await edges.createEdge(edge("ab", "a", "b"));
  await edges.createEdge(edge("bc", "b", "c"));
  const path = await index.findPath("a", "c");
  assertEqual(path.map((item) => item.id).join(">"), "a>b>c", "Path lookup should find shortest path.");
});

test("index lookup by alias", async () => {
  const { nodes, index } = makeServices();
  await nodes.createNode({ ...node("alias_node", "Canonical"), aliases: ["Known Alias"] });
  const found = await index.getNodesByAlias("Known Alias");
  assertEqual(found[0].id, "alias_node", "Alias lookup should find node.");
});

test("index lookup by type", async () => {
  const { nodes, index } = makeServices();
  await nodes.createNode({ ...node("decision_node", "Decision"), type: "decision" });
  const found = await index.getNodesByType("decision");
  assertEqual(found[0].id, "decision_node", "Type lookup should find node.");
});

test("evidence storage", async () => {
  const { evidence } = makeServices();
  const created = await evidence.createEvidence({ id: "ev", sourceId: "source_1", sourceType: "note", excerpt: "Approved.", confidence: 0.8 });
  const found = await evidence.getEvidenceById(created.id);
  assert(found, "Evidence should be stored.");
  assertEqual(found?.excerpt, "Approved.", "Evidence excerpt should be retrievable.");
});

test("temporal edge support", async () => {
  const { nodes, edges, repository } = makeServices();
  await nodes.createNode(node("a"));
  await nodes.createNode(node("b"));
  await edges.createEdge({
    ...edge("temporal", "a", "b"),
    temporalScope: { validFrom: "2026-01-01T00:00:00.000Z", validTo: null, observedAt: "2026-02-01T00:00:00.000Z" },
  });
  const stored = await repository.getEdgeById("temporal");
  assertEqual(stored?.temporalScope?.validFrom, "2026-01-01T00:00:00.000Z", "Temporal fields should be stored.");
});

test("invalid temporal scope rejection", async () => {
  const { nodes, edges } = makeServices();
  await nodes.createNode(node("a"));
  await nodes.createNode(node("b"));
  await assertRejects(
    () => edges.createEdge({
      ...edge("bad_temporal", "a", "b"),
      temporalScope: { validFrom: "2026-02-01T00:00:00.000Z", validTo: "2026-01-01T00:00:00.000Z" },
    }),
    GraphValidationError,
    "validTo cannot be before validFrom",
  );
});

test("graph construction failure event", async () => {
  const { construction, events } = makeServices();
  await assertRejects(
    () => construction.construct({
      nodes: [node("failure_node")],
      edges: [edge("failure_edge", "failure_node", "missing")],
      evidence: [],
    }),
    GraphConstructionError,
    "Target node not found",
  );
  const stored = await events.listEvents();
  assert(stored.some((event) => event.type === "GraphConstructionFailed"), "Failure should publish event.");
});

for (const item of tests) {
  await item.run();
  console.log(`ok - ${item.name}`);
}
