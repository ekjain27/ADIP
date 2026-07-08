import type { GraphEdge, GraphNode, ReasoningPath, ReasoningQuery } from "../domain/models.js";
import type { GraphReadPort } from "../ports/index.js";
import { ReasoningConfidenceService, TemporalReasoningService } from "../services/index.js";

export class InMemoryGraphReadAdapter implements GraphReadPort {
  private readonly nodes: Map<string, GraphNode>;
  private readonly edges: Map<string, GraphEdge>;
  private readonly temporal = new TemporalReasoningService();
  private readonly confidence = new ReasoningConfidenceService();

  constructor(input: { nodes?: readonly GraphNode[]; edges?: readonly GraphEdge[] } = {}) {
    this.nodes = new Map((input.nodes ?? []).map((node) => [node.id, node]));
    this.edges = new Map((input.edges ?? []).map((edge) => [edge.id, edge]));
  }

  async getNodeById(id: string): Promise<GraphNode | null> {
    return this.nodes.get(id) ?? null;
  }

  async getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    return [...this.nodes.values()].find((node) => node.canonicalName === canonicalName) ?? null;
  }

  async getNeighbors(nodeId: string): Promise<readonly GraphNode[]> {
    return [...this.edges.values()]
      .filter((edge) => edge.sourceNodeId === nodeId)
      .map((edge) => this.nodes.get(edge.targetNodeId))
      .filter((node): node is GraphNode => Boolean(node));
  }

  async getEdgesByNodeId(nodeId: string): Promise<readonly GraphEdge[]> {
    return [...this.edges.values()].filter((edge) => edge.sourceNodeId === nodeId || edge.targetNodeId === nodeId);
  }

  async findPaths(query: ReasoningQuery): Promise<readonly ReasoningPath[]> {
    const source = query.sourceNodeId
      ? await this.getNodeById(query.sourceNodeId)
      : query.sourceCanonicalName
        ? await this.getNodeByCanonicalName(query.sourceCanonicalName)
        : null;
    if (!source) {
      return [];
    }
    const paths: ReasoningPath[] = [];
    const maxDepth = query.maxDepth ?? 4;
    const walk = async (node: GraphNode, nodes: GraphNode[], edges: GraphEdge[], visited: Set<string>): Promise<void> => {
      if (edges.length >= maxDepth) {
        return;
      }
      for (const edge of [...this.edges.values()].filter((candidate) => candidate.sourceNodeId === node.id)) {
        if (query.reasoningDate && !this.temporal.isEdgeValid(edge, query.reasoningDate)) {
          continue;
        }
        const next = this.nodes.get(edge.targetNodeId);
        if (!next || visited.has(next.id)) {
          continue;
        }
        const nextEdges = [...edges, edge];
        const nextNodes = [...nodes, next];
        paths.push({
          id: `path_${nextEdges.map((pathEdge) => pathEdge.id).join("_")}`,
          nodes: nextNodes,
          edges: nextEdges,
          relationshipTypes: nextEdges.map((pathEdge) => pathEdge.type),
          confidence: this.confidence.calculatePathConfidence(nextEdges),
          temporalValidity: 1
        });
        visited.add(next.id);
        await walk(next, nextNodes, nextEdges, visited);
        visited.delete(next.id);
      }
    };
    await walk(source, [source], [], new Set([source.id]));
    return paths;
  }
}
