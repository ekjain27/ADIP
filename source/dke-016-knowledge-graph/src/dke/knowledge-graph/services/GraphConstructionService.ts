import { GraphConstructionError, type GraphConstructionInput, type GraphConstructionResult, type GraphEdge, type GraphNode } from "../domain/index.js";
import type { EventPublisherPort, GraphRepositoryPort, LoggerPort, MetricsPort } from "../ports/index.js";
import { EdgeService } from "./EdgeService.js";
import { createGraphEvent } from "./EventFactory.js";
import { GraphEvidenceService } from "./GraphEvidenceService.js";
import { GraphValidationService } from "./GraphValidationService.js";
import { NodeService } from "./NodeService.js";

export class GraphConstructionService {
  constructor(
    private readonly graphRepository: GraphRepositoryPort,
    private readonly validation: GraphValidationService,
    private readonly nodeService: NodeService,
    private readonly edgeService: EdgeService,
    private readonly evidenceService: GraphEvidenceService,
    private readonly events?: EventPublisherPort,
    private readonly metrics?: MetricsPort,
    private readonly logger?: LoggerPort,
  ) {}

  async construct(input: GraphConstructionInput): Promise<GraphConstructionResult> {
    const correlationId = crypto.randomUUID();
    await this.graphRepository.beginTransaction();
    try {
      const nodes = input.nodes.map((node) => this.materializeNode(node));
      const edges = input.edges.map((edge) => this.materializeEdge(edge));
      this.validation.validateUniqueIds(nodes, edges);
      const evidenceIds = new Set(input.evidence.map((evidence) => evidence.id));
      for (const edge of edges) this.validation.validateEvidenceReferences(edge, evidenceIds);

      const result: GraphConstructionResult = {
        nodesCreated: 0,
        nodesMerged: 0,
        edgesCreated: 0,
        evidenceCreated: 0,
        nodeIds: [],
        edgeIds: [],
        evidenceIds: [],
        warnings: [],
      };

      for (const evidenceInput of input.evidence) {
        const evidence = await this.evidenceService.createEvidence(evidenceInput);
        result.evidenceCreated += 1;
        result.evidenceIds.push(evidence.id);
      }

      const nodeResult = await this.nodeService.createNodes(nodes);
      result.nodesMerged = nodeResult.mergedCount;
      result.nodesCreated = nodeResult.nodes.length - nodeResult.mergedCount;
      result.nodeIds = nodeResult.nodes.map((node) => node.id);

      const createdEdges = await this.edgeService.createEdges(edges, input.allowSelfEdge ?? false);
      result.edgesCreated = createdEdges.length;
      result.edgeIds = createdEdges.map((edge) => edge.id);

      await this.graphRepository.commitTransaction();
      this.metrics?.increment("constructionSuccesses");
      this.logger?.info("Graph construction completed", { correlationId });
      await this.events?.publish(createGraphEvent("GraphConstructionCompleted", result as unknown as Record<string, unknown>, correlationId));
      return result;
    } catch (error) {
      await this.graphRepository.rollbackTransaction();
      this.metrics?.increment("constructionFailures");
      this.logger?.error("Graph construction failed", { correlationId, error: error instanceof Error ? error.message : String(error) });
      await this.events?.publish(createGraphEvent("GraphConstructionFailed", { message: error instanceof Error ? error.message : String(error) }, correlationId));
      if (error instanceof GraphConstructionError) throw error;
      throw new GraphConstructionError(error instanceof Error ? error.message : "Graph construction failed.");
    }
  }

  private materializeNode(input: GraphConstructionInput["nodes"][number]): GraphNode {
    const now = new Date().toISOString();
    return {
      ...input,
      createdAt: input.createdAt ?? now,
      updatedAt: input.updatedAt ?? now,
      version: input.version ?? 1,
    };
  }

  private materializeEdge(input: GraphConstructionInput["edges"][number]): GraphEdge {
    const now = new Date().toISOString();
    return {
      ...input,
      createdAt: input.createdAt ?? now,
      updatedAt: input.updatedAt ?? now,
    };
  }
}
