import { EdgeNotFoundError, NodeNotFoundError, type GraphEdge, type GraphEdgeInput } from "../domain/index.js";
import type { EventPublisherPort, GraphRepositoryPort, LoggerPort, MetricsPort } from "../ports/index.js";
import { createGraphEvent } from "./EventFactory.js";
import { GraphValidationService } from "./GraphValidationService.js";

export class EdgeService {
  constructor(
    private readonly graphRepository: GraphRepositoryPort,
    private readonly validation: GraphValidationService,
    private readonly events?: EventPublisherPort,
    private readonly metrics?: MetricsPort,
    private readonly logger?: LoggerPort,
  ) {}

  async createEdge(input: GraphEdgeInput, allowSelfEdge = false): Promise<GraphEdge> {
    const now = new Date().toISOString();
    const edge: GraphEdge = { ...input, createdAt: input.createdAt ?? now, updatedAt: input.updatedAt ?? now };
    this.validateEdge(edge, allowSelfEdge);
    if (!(await this.graphRepository.getNodeById(edge.sourceNodeId))) throw new NodeNotFoundError(`Source node not found: ${edge.sourceNodeId}`);
    if (!(await this.graphRepository.getNodeById(edge.targetNodeId))) throw new NodeNotFoundError(`Target node not found: ${edge.targetNodeId}`);
    const created = await this.graphRepository.createEdge(edge);
    this.metrics?.increment("edgesCreated");
    this.metrics?.recordEdgeConfidence(created.confidence);
    this.logger?.info("Graph edge created", { edgeId: created.id });
    await this.events?.publish(createGraphEvent("GraphEdgeCreated", { edgeId: created.id }));
    return created;
  }

  async createEdges(inputs: GraphEdgeInput[], allowSelfEdge = false): Promise<GraphEdge[]> {
    const edges: GraphEdge[] = [];
    for (const input of inputs) edges.push(await this.createEdge(input, allowSelfEdge));
    return edges;
  }

  async updateEdge(input: GraphEdge, allowSelfEdge = false): Promise<GraphEdge> {
    if (!(await this.graphRepository.getEdgeById(input.id))) throw new EdgeNotFoundError(`Edge not found: ${input.id}`);
    const edge = { ...input, updatedAt: new Date().toISOString() };
    this.validateEdge(edge, allowSelfEdge);
    return this.graphRepository.updateEdge(edge);
  }

  async updateEdges(edges: GraphEdge[], allowSelfEdge = false): Promise<GraphEdge[]> {
    const updated: GraphEdge[] = [];
    for (const edge of edges) updated.push(await this.updateEdge(edge, allowSelfEdge));
    return updated;
  }

  async deleteEdge(id: string): Promise<void> {
    return this.graphRepository.deleteEdge(id);
  }

  async deleteEdges(ids: string[]): Promise<void> {
    return this.graphRepository.deleteEdges(ids);
  }

  private validateEdge(edge: GraphEdge, allowSelfEdge: boolean): void {
    try {
      this.validation.validateEdge(edge, allowSelfEdge);
    } catch (error) {
      this.metrics?.increment("validationFailures");
      throw error;
    }
  }
}
