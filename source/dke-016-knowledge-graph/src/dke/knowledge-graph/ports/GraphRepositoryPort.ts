import type { GraphEdge, GraphNode } from "../domain/index.js";

export interface GraphRepositoryPort {
  beginTransaction(): Promise<void>;
  commitTransaction(): Promise<void>;
  rollbackTransaction(): Promise<void>;

  createNode(node: GraphNode): Promise<GraphNode>;
  createNodes(nodes: GraphNode[]): Promise<GraphNode[]>;
  getNodeById(id: string): Promise<GraphNode | null>;
  getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null>;
  listNodes(): Promise<GraphNode[]>;
  updateNode(node: GraphNode): Promise<GraphNode>;
  updateNodes(nodes: GraphNode[]): Promise<GraphNode[]>;
  deleteNode(id: string): Promise<void>;
  deleteNodes(ids: string[]): Promise<void>;

  createEdge(edge: GraphEdge): Promise<GraphEdge>;
  createEdges(edges: GraphEdge[]): Promise<GraphEdge[]>;
  getEdgeById(id: string): Promise<GraphEdge | null>;
  listEdges(): Promise<GraphEdge[]>;
  updateEdge(edge: GraphEdge): Promise<GraphEdge>;
  updateEdges(edges: GraphEdge[]): Promise<GraphEdge[]>;
  deleteEdge(id: string): Promise<void>;
  deleteEdges(ids: string[]): Promise<void>;

  getNeighbors(nodeId: string): Promise<GraphNode[]>;
  findPath(sourceNodeId: string, targetNodeId: string): Promise<GraphNode[]>;
  getNodesByAlias(alias: string): Promise<GraphNode[]>;
  getNodesByType(type: string): Promise<GraphNode[]>;
  getEdgesBySourceNode(sourceNodeId: string): Promise<GraphEdge[]>;
  getEdgesByTargetNode(targetNodeId: string): Promise<GraphEdge[]>;
}
