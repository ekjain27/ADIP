import { ConflictError, NodeNotFoundError, type GraphNode, type GraphNodeInput, type GraphNodeType } from "../domain/index.js";
import type { EntityResolutionPort, EventPublisherPort, GraphRepositoryPort, LoggerPort, MetricsPort } from "../ports/index.js";
import { createGraphEvent } from "./EventFactory.js";
import { GraphValidationService } from "./GraphValidationService.js";

const allowedNodeTypes = new Set<GraphNodeType>([
  "unknown",
  "organization",
  "department",
  "user",
  "decision",
  "evidence",
  "alternative",
  "risk",
  "outcome",
  "lesson",
  "concept",
  "custom",
]);

export class NodeService {
  constructor(
    private readonly graphRepository: GraphRepositoryPort,
    private readonly validation: GraphValidationService,
    private readonly entityResolution: EntityResolutionPort,
    private readonly events?: EventPublisherPort,
    private readonly metrics?: MetricsPort,
    private readonly logger?: LoggerPort,
  ) {}

  async createNode(input: GraphNodeInput): Promise<{ node: GraphNode; merged: boolean }> {
    const now = new Date().toISOString();
    const node: GraphNode = {
      ...input,
      type: allowedNodeTypes.has(input.type) ? input.type : "unknown",
      aliases: input.aliases ?? [],
      attributes: input.attributes ?? {},
      sourceIds: input.sourceIds ?? [],
      createdAt: input.createdAt ?? now,
      updatedAt: input.updatedAt ?? now,
      version: input.version ?? 1,
    };
    this.validateNode(node);
    const duplicate = await this.entityResolution.findDuplicate(node, await this.graphRepository.listNodes());
    if (duplicate) return { node: await this.mergeNodes(duplicate.id, node), merged: true };
    const created = await this.graphRepository.createNode(node);
    this.metrics?.increment("nodesCreated");
    this.metrics?.recordNodeConfidence(created.confidence);
    this.logger?.info("Graph node created", { nodeId: created.id });
    await this.events?.publish(createGraphEvent("GraphNodeCreated", { nodeId: created.id }));
    return { node: created, merged: false };
  }

  async createNodes(inputs: GraphNodeInput[]): Promise<{ nodes: GraphNode[]; mergedCount: number }> {
    const nodes: GraphNode[] = [];
    let mergedCount = 0;
    for (const input of inputs) {
      const result = await this.createNode(input);
      nodes.push(result.node);
      if (result.merged) mergedCount += 1;
    }
    return { nodes, mergedCount };
  }

  async getNodeById(id: string): Promise<GraphNode | null> {
    return this.graphRepository.getNodeById(id);
  }

  async getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    return this.graphRepository.getNodeByCanonicalName(canonicalName);
  }

  async updateNode(input: GraphNode): Promise<GraphNode> {
    if (!(await this.graphRepository.getNodeById(input.id))) throw new NodeNotFoundError(`Node not found: ${input.id}`);
    const node = { ...input, updatedAt: new Date().toISOString(), version: input.version + 1 };
    this.validateNode(node);
    const updated = await this.graphRepository.updateNode(node);
    this.metrics?.increment("nodesUpdated");
    this.metrics?.recordNodeConfidence(updated.confidence);
    this.logger?.info("Graph node updated", { nodeId: updated.id });
    await this.events?.publish(createGraphEvent("GraphNodeUpdated", { nodeId: updated.id }));
    return updated;
  }

  async updateNodes(nodes: GraphNode[]): Promise<GraphNode[]> {
    const updated: GraphNode[] = [];
    for (const node of nodes) updated.push(await this.updateNode(node));
    return updated;
  }

  async mergeNodes(targetNodeId: string, incoming: GraphNode): Promise<GraphNode> {
    const target = await this.graphRepository.getNodeById(targetNodeId);
    if (!target) throw new NodeNotFoundError(`Node not found: ${targetNodeId}`);
    if (target.type !== incoming.type) throw new ConflictError("Cannot merge nodes with different types.");
    const merged: GraphNode = {
      ...target,
      aliases: Array.from(new Set([...target.aliases, incoming.canonicalName, ...incoming.aliases])).filter((alias) => alias !== target.canonicalName),
      attributes: { ...target.attributes, ...incoming.attributes },
      confidence: Math.max(target.confidence, incoming.confidence),
      sourceIds: Array.from(new Set([...target.sourceIds, ...incoming.sourceIds])),
      embedding: target.embedding ?? incoming.embedding,
      updatedAt: new Date().toISOString(),
      version: target.version + 1,
    };
    this.validateNode(merged);
    const saved = await this.graphRepository.updateNode(merged);
    this.metrics?.increment("duplicatesMerged");
    this.metrics?.recordNodeConfidence(saved.confidence);
    this.logger?.info("Graph nodes merged", { targetNodeId, incomingNodeId: incoming.id });
    await this.events?.publish(createGraphEvent("GraphNodeMerged", { targetNodeId, incomingNodeId: incoming.id }));
    return saved;
  }

  async deleteNode(id: string): Promise<void> {
    return this.graphRepository.deleteNode(id);
  }

  async deleteNodes(ids: string[]): Promise<void> {
    return this.graphRepository.deleteNodes(ids);
  }

  private validateNode(node: GraphNode): void {
    try {
      this.validation.validateNode(node);
    } catch (error) {
      this.metrics?.increment("validationFailures");
      throw error;
    }
  }
}
