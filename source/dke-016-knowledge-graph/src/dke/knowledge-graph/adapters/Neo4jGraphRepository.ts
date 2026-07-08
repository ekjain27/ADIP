import type { EvidenceRepositoryPort, GraphRepositoryPort } from "../ports/index.js";
import {
  EdgeNotFoundError,
  GraphRepositoryError,
  NodeNotFoundError,
  type GraphEdge,
  type GraphEvidence,
  type GraphNode,
} from "../domain/index.js";

type Neo4jRecord = { get(key: string): unknown };
type Neo4jResult = { records: Neo4jRecord[] };
type Neo4jRunnable = { run(query: string, parameters?: Record<string, unknown>): Promise<Neo4jResult> };
type Neo4jTransaction = Neo4jRunnable & { commit(): Promise<void>; rollback(): Promise<void> };
type Neo4jSession = Neo4jRunnable & { beginTransaction(): Neo4jTransaction; close(): Promise<void> };
type Neo4jDriver = { session(options?: Record<string, unknown>): Neo4jSession; close?(): Promise<void> };

export interface Neo4jGraphRepositoryOptions {
  driver?: Neo4jDriver;
  sessionFactory?: () => Neo4jSession;
  uri?: string;
  username?: string;
  password?: string;
  database?: string;
}

export class Neo4jGraphRepository implements GraphRepositoryPort, EvidenceRepositoryPort {
  private readonly providedDriver?: Neo4jDriver;
  private readonly sessionFactory?: () => Neo4jSession;
  private readonly uri?: string;
  private readonly username?: string;
  private readonly password?: string;
  private readonly database?: string;
  private driverPromise: Promise<Neo4jDriver> | null = null;
  private transactionSession: Neo4jSession | null = null;
  private transaction: Neo4jTransaction | null = null;

  constructor(options: Neo4jGraphRepositoryOptions = {}) {
    this.providedDriver = options.driver;
    this.sessionFactory = options.sessionFactory;
    this.uri = options.uri;
    this.username = options.username;
    this.password = options.password;
    this.database = options.database;
  }

  async beginTransaction(): Promise<void> {
    if (this.transaction) throw new GraphRepositoryError("Transaction already active.");
    const session = await this.openSession();
    this.transactionSession = session;
    this.transaction = session.beginTransaction();
  }

  async commitTransaction(): Promise<void> {
    if (!this.transaction) return;
    const transaction = this.transaction;
    const session = this.transactionSession;
    this.transaction = null;
    this.transactionSession = null;
    await transaction.commit();
    await session?.close();
  }

  async rollbackTransaction(): Promise<void> {
    if (!this.transaction) return;
    const transaction = this.transaction;
    const session = this.transactionSession;
    this.transaction = null;
    this.transactionSession = null;
    await transaction.rollback();
    await session?.close();
  }

  async createNode(node: GraphNode): Promise<GraphNode> {
    const result = await this.runWrite(
      "CREATE (node:KnowledgeNode) SET node = $node RETURN node",
      { node },
    );
    return this.nodeFromRecord(result.records[0], "node");
  }

  async createNodes(nodes: GraphNode[]): Promise<GraphNode[]> {
    const result = await this.runWrite(
      "UNWIND $nodes AS nodeData CREATE (node:KnowledgeNode) SET node = nodeData RETURN node ORDER BY node.id",
      { nodes },
    );
    return result.records.map((record) => this.nodeFromRecord(record, "node"));
  }

  async getNodeById(id: string): Promise<GraphNode | null> {
    const result = await this.runRead("MATCH (node:KnowledgeNode {id: $id}) RETURN node LIMIT 1", { id });
    return this.optionalNode(result);
  }

  async getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    const result = await this.runRead(
      "MATCH (node:KnowledgeNode) WHERE toLower(trim(node.canonicalName)) = toLower(trim($canonicalName)) RETURN node LIMIT 1",
      { canonicalName },
    );
    return this.optionalNode(result);
  }

  async listNodes(): Promise<GraphNode[]> {
    const result = await this.runRead("MATCH (node:KnowledgeNode) RETURN node ORDER BY node.id");
    return result.records.map((record) => this.nodeFromRecord(record, "node"));
  }

  async updateNode(node: GraphNode): Promise<GraphNode> {
    const result = await this.runWrite(
      "MATCH (node:KnowledgeNode {id: $id}) SET node = $node RETURN node",
      { id: node.id, node },
    );
    if (result.records.length === 0) throw new NodeNotFoundError(`Node not found: ${node.id}`);
    return this.nodeFromRecord(result.records[0], "node");
  }

  async updateNodes(nodes: GraphNode[]): Promise<GraphNode[]> {
    const updated: GraphNode[] = [];
    for (const node of nodes) updated.push(await this.updateNode(node));
    return updated;
  }

  async deleteNode(id: string): Promise<void> {
    await this.runWrite("MATCH (node:KnowledgeNode {id: $id}) DETACH DELETE node", { id });
  }

  async deleteNodes(ids: string[]): Promise<void> {
    await this.runWrite("MATCH (node:KnowledgeNode) WHERE node.id IN $ids DETACH DELETE node", { ids });
  }

  async createEdge(edge: GraphEdge): Promise<GraphEdge> {
    const result = await this.runWrite(
      [
        "MATCH (source:KnowledgeNode {id: $sourceNodeId})",
        "MATCH (target:KnowledgeNode {id: $targetNodeId})",
        "CREATE (source)-[edge:KNOWLEDGE_RELATIONSHIP]->(target)",
        "SET edge = $edge",
        "RETURN edge",
      ].join(" "),
      { sourceNodeId: edge.sourceNodeId, targetNodeId: edge.targetNodeId, edge },
    );
    return this.edgeFromRecord(result.records[0], "edge");
  }

  async createEdges(edges: GraphEdge[]): Promise<GraphEdge[]> {
    const created: GraphEdge[] = [];
    for (const edge of edges) created.push(await this.createEdge(edge));
    return created;
  }

  async getEdgeById(id: string): Promise<GraphEdge | null> {
    const result = await this.runRead("MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP {id: $id}]->() RETURN edge LIMIT 1", { id });
    return result.records[0] ? this.edgeFromRecord(result.records[0], "edge") : null;
  }

  async listEdges(): Promise<GraphEdge[]> {
    const result = await this.runRead("MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP]->() RETURN edge ORDER BY edge.id");
    return result.records.map((record) => this.edgeFromRecord(record, "edge"));
  }

  async updateEdge(edge: GraphEdge): Promise<GraphEdge> {
    const result = await this.runWrite(
      "MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP {id: $id}]->() SET edge = $edge RETURN edge",
      { id: edge.id, edge },
    );
    if (result.records.length === 0) throw new EdgeNotFoundError(`Edge not found: ${edge.id}`);
    return this.edgeFromRecord(result.records[0], "edge");
  }

  async updateEdges(edges: GraphEdge[]): Promise<GraphEdge[]> {
    const updated: GraphEdge[] = [];
    for (const edge of edges) updated.push(await this.updateEdge(edge));
    return updated;
  }

  async deleteEdge(id: string): Promise<void> {
    await this.runWrite("MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP {id: $id}]->() DELETE edge", { id });
  }

  async deleteEdges(ids: string[]): Promise<void> {
    await this.runWrite("MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP]->() WHERE edge.id IN $ids DELETE edge", { ids });
  }

  async getNeighbors(nodeId: string): Promise<GraphNode[]> {
    const result = await this.runRead(
      "MATCH (:KnowledgeNode {id: $nodeId})--(neighbor:KnowledgeNode) RETURN DISTINCT neighbor ORDER BY neighbor.id",
      { nodeId },
    );
    return result.records.map((record) => this.nodeFromRecord(record, "neighbor"));
  }

  async findPath(sourceNodeId: string, targetNodeId: string): Promise<GraphNode[]> {
    const result = await this.runRead(
      [
        "MATCH (source:KnowledgeNode {id: $sourceNodeId}), (target:KnowledgeNode {id: $targetNodeId})",
        "MATCH path = shortestPath((source)-[:KNOWLEDGE_RELATIONSHIP*..25]-(target))",
        "RETURN nodes(path) AS nodes",
      ].join(" "),
      { sourceNodeId, targetNodeId },
    );
    const nodes = result.records[0]?.get("nodes");
    if (!Array.isArray(nodes)) return [];
    return nodes.map((node) => this.nodeFromValue(node));
  }

  async getNodesByAlias(alias: string): Promise<GraphNode[]> {
    const result = await this.runRead(
      "MATCH (node:KnowledgeNode) WHERE any(alias IN node.aliases WHERE toLower(trim(alias)) = toLower(trim($alias))) RETURN node ORDER BY node.id",
      { alias },
    );
    return result.records.map((record) => this.nodeFromRecord(record, "node"));
  }

  async getNodesByType(type: string): Promise<GraphNode[]> {
    const result = await this.runRead("MATCH (node:KnowledgeNode {type: $type}) RETURN node ORDER BY node.id", { type });
    return result.records.map((record) => this.nodeFromRecord(record, "node"));
  }

  async getEdgesBySourceNode(sourceNodeId: string): Promise<GraphEdge[]> {
    const result = await this.runRead(
      "MATCH (:KnowledgeNode {id: $sourceNodeId})-[edge:KNOWLEDGE_RELATIONSHIP]->() RETURN edge ORDER BY edge.id",
      { sourceNodeId },
    );
    return result.records.map((record) => this.edgeFromRecord(record, "edge"));
  }

  async getEdgesByTargetNode(targetNodeId: string): Promise<GraphEdge[]> {
    const result = await this.runRead(
      "MATCH ()-[edge:KNOWLEDGE_RELATIONSHIP]->(:KnowledgeNode {id: $targetNodeId}) RETURN edge ORDER BY edge.id",
      { targetNodeId },
    );
    return result.records.map((record) => this.edgeFromRecord(record, "edge"));
  }

  async createEvidence(evidence: GraphEvidence): Promise<GraphEvidence> {
    const result = await this.runWrite(
      "CREATE (evidence:GraphEvidence) SET evidence = $evidence RETURN evidence",
      { evidence },
    );
    return this.evidenceFromRecord(result.records[0], "evidence");
  }

  async getEvidenceById(id: string): Promise<GraphEvidence | null> {
    const result = await this.runRead("MATCH (evidence:GraphEvidence {id: $id}) RETURN evidence LIMIT 1", { id });
    return result.records[0] ? this.evidenceFromRecord(result.records[0], "evidence") : null;
  }

  async listEvidence(): Promise<GraphEvidence[]> {
    const result = await this.runRead("MATCH (evidence:GraphEvidence) RETURN evidence ORDER BY evidence.id");
    return result.records.map((record) => this.evidenceFromRecord(record, "evidence"));
  }

  private async runRead(query: string, parameters: Record<string, unknown> = {}): Promise<Neo4jResult> {
    return this.run(query, parameters);
  }

  private async runWrite(query: string, parameters: Record<string, unknown> = {}): Promise<Neo4jResult> {
    return this.run(query, parameters);
  }

  private async run(query: string, parameters: Record<string, unknown>): Promise<Neo4jResult> {
    if (this.transaction) return this.transaction.run(query, parameters);
    const session = await this.openSession();
    try {
      return await session.run(query, parameters);
    } finally {
      await session.close();
    }
  }

  private async openSession(): Promise<Neo4jSession> {
    if (this.sessionFactory) return this.sessionFactory();
    const driver = await this.getDriver();
    return driver.session(this.database ? { database: this.database } : undefined);
  }

  private async getDriver(): Promise<Neo4jDriver> {
    if (this.providedDriver) return this.providedDriver;
    if (!this.uri || !this.username || this.password === undefined) {
      throw new GraphRepositoryError("Neo4jGraphRepository requires a driver, sessionFactory, or uri/username/password options.");
    }
    this.driverPromise ??= this.createDriver();
    return this.driverPromise;
  }

  private async createDriver(): Promise<Neo4jDriver> {
    let neo4j: { driver: (uri: string, authToken: unknown) => Neo4jDriver; auth: { basic: (username: string, password: string) => unknown } };
    try {
      const dynamicImport = new Function("specifier", "return import(specifier)") as (specifier: string) => Promise<typeof neo4j>;
      neo4j = await dynamicImport("neo4j-driver");
    } catch (error) {
      throw new GraphRepositoryError(
        `Neo4jGraphRepository requires optional package "neo4j-driver" when no driver/sessionFactory is supplied: ${this.errorMessage(error)}`,
      );
    }
    return neo4j.driver(this.uri!, neo4j.auth.basic(this.username!, this.password!));
  }

  private optionalNode(result: Neo4jResult): GraphNode | null {
    return result.records[0] ? this.nodeFromRecord(result.records[0], "node") : null;
  }

  private nodeFromRecord(record: Neo4jRecord, key: string): GraphNode {
    return this.nodeFromValue(record.get(key));
  }

  private edgeFromRecord(record: Neo4jRecord, key: string): GraphEdge {
    return this.edgeFromValue(record.get(key));
  }

  private evidenceFromRecord(record: Neo4jRecord, key: string): GraphEvidence {
    return this.evidenceFromValue(record.get(key));
  }

  private nodeFromValue(value: unknown): GraphNode {
    const properties = this.properties(value);
    return {
      id: String(properties.id),
      type: String(properties.type ?? "unknown") as GraphNode["type"],
      canonicalName: String(properties.canonicalName),
      aliases: this.stringArray(properties.aliases),
      attributes: this.objectValue(properties.attributes),
      confidence: this.numberValue(properties.confidence, 0),
      sourceIds: this.stringArray(properties.sourceIds),
      embedding: Array.isArray(properties.embedding) ? properties.embedding.map((item) => this.numberValue(item, 0)) : undefined,
      createdAt: String(properties.createdAt),
      updatedAt: String(properties.updatedAt),
      version: this.numberValue(properties.version, 1),
    };
  }

  private edgeFromValue(value: unknown): GraphEdge {
    const properties = this.properties(value);
    return {
      id: String(properties.id),
      sourceNodeId: String(properties.sourceNodeId),
      targetNodeId: String(properties.targetNodeId),
      relationType: String(properties.relationType ?? "related_to") as GraphEdge["relationType"],
      weight: this.numberValue(properties.weight, 0),
      confidence: this.numberValue(properties.confidence, 0),
      evidenceIds: this.stringArray(properties.evidenceIds),
      temporalScope: properties.temporalScope ? this.objectValue(properties.temporalScope) as GraphEdge["temporalScope"] : undefined,
      createdAt: String(properties.createdAt),
      updatedAt: String(properties.updatedAt),
    };
  }

  private evidenceFromValue(value: unknown): GraphEvidence {
    const properties = this.properties(value);
    return {
      id: String(properties.id),
      sourceId: String(properties.sourceId),
      sourceType: String(properties.sourceType),
      excerpt: properties.excerpt === undefined ? undefined : String(properties.excerpt),
      confidence: this.numberValue(properties.confidence, 0),
      createdAt: String(properties.createdAt),
    };
  }

  private properties(value: unknown): Record<string, unknown> {
    if (!value || typeof value !== "object") throw new GraphRepositoryError("Neo4j record did not contain a graph entity.");
    const raw = value as { properties?: Record<string, unknown> };
    return raw.properties ?? (value as Record<string, unknown>);
  }

  private stringArray(value: unknown): string[] {
    return Array.isArray(value) ? value.map((item) => String(item)) : [];
  }

  private objectValue(value: unknown): Record<string, unknown> {
    return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
  }

  private numberValue(value: unknown, fallback: number): number {
    if (typeof value === "number") return value;
    if (value && typeof value === "object" && "toNumber" in value && typeof (value as { toNumber: unknown }).toNumber === "function") {
      return ((value as { toNumber: () => number }).toNumber());
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  private errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : String(error);
  }
}
