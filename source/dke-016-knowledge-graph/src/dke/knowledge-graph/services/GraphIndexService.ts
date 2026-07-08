import type { GraphEdge, GraphNode } from "../domain/index.js";
import type { GraphRepositoryPort } from "../ports/index.js";

export class GraphIndexService {
  constructor(private readonly graphRepository: GraphRepositoryPort) {}

  getNodeById(nodeId: string): Promise<GraphNode | null> {
    return this.graphRepository.getNodeById(nodeId);
  }

  getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    return this.graphRepository.getNodeByCanonicalName(canonicalName);
  }

  getNodesByAlias(alias: string): Promise<GraphNode[]> {
    return this.graphRepository.getNodesByAlias(alias);
  }

  getNodesByType(type: string): Promise<GraphNode[]> {
    return this.graphRepository.getNodesByType(type);
  }

  getEdgesBySourceNode(sourceNodeId: string): Promise<GraphEdge[]> {
    return this.graphRepository.getEdgesBySourceNode(sourceNodeId);
  }

  getEdgesByTargetNode(targetNodeId: string): Promise<GraphEdge[]> {
    return this.graphRepository.getEdgesByTargetNode(targetNodeId);
  }

  getNeighbors(nodeId: string): Promise<GraphNode[]> {
    return this.graphRepository.getNeighbors(nodeId);
  }

  findPath(sourceNodeId: string, targetNodeId: string): Promise<GraphNode[]> {
    return this.graphRepository.findPath(sourceNodeId, targetNodeId);
  }
}
