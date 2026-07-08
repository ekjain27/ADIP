import type { GraphEdge, GraphNode, ReasoningPath, ReasoningQuery } from "../domain/models.js";

export interface GraphReadPort {
  getNodeById(id: string): Promise<GraphNode | null>;
  getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null>;
  getNeighbors(nodeId: string): Promise<readonly GraphNode[]>;
  getEdgesByNodeId(nodeId: string): Promise<readonly GraphEdge[]>;
  findPaths(query: ReasoningQuery): Promise<readonly ReasoningPath[]>;
}
