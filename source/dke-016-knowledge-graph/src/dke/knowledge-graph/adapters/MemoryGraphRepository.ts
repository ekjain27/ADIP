import type { EvidenceRepositoryPort, GraphRepositoryPort } from "../ports/index.js";
import { EdgeNotFoundError, GraphRepositoryError, NodeNotFoundError, type GraphEdge, type GraphEvidence, type GraphNode } from "../domain/index.js";

interface Snapshot {
  nodes: Map<string, GraphNode>;
  edges: Map<string, GraphEdge>;
  evidence: Map<string, GraphEvidence>;
}

export class MemoryGraphRepository implements GraphRepositoryPort, EvidenceRepositoryPort {
  private readonly nodes = new Map<string, GraphNode>();
  private readonly edges = new Map<string, GraphEdge>();
  private readonly evidence = new Map<string, GraphEvidence>();
  private transactionSnapshot: Snapshot | null = null;

  async beginTransaction(): Promise<void> {
    if (this.transactionSnapshot) throw new GraphRepositoryError("Transaction already active.");
    this.transactionSnapshot = {
      nodes: new Map(this.nodes),
      edges: new Map(this.edges),
      evidence: new Map(this.evidence),
    };
  }

  async commitTransaction(): Promise<void> {
    this.transactionSnapshot = null;
  }

  async rollbackTransaction(): Promise<void> {
    if (!this.transactionSnapshot) return;
    this.nodes.clear();
    this.edges.clear();
    this.evidence.clear();
    for (const [key, value] of this.transactionSnapshot.nodes) this.nodes.set(key, value);
    for (const [key, value] of this.transactionSnapshot.edges) this.edges.set(key, value);
    for (const [key, value] of this.transactionSnapshot.evidence) this.evidence.set(key, value);
    this.transactionSnapshot = null;
  }

  async createNode(node: GraphNode): Promise<GraphNode> {
    this.nodes.set(node.id, node);
    return node;
  }

  async createNodes(nodes: GraphNode[]): Promise<GraphNode[]> {
    for (const node of nodes) this.nodes.set(node.id, node);
    return nodes;
  }

  async getNodeById(id: string): Promise<GraphNode | null> {
    return this.nodes.get(id) ?? null;
  }

  async getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    const normalized = canonicalName.trim().toLocaleLowerCase();
    return [...this.nodes.values()].find((node) => node.canonicalName.trim().toLocaleLowerCase() === normalized) ?? null;
  }

  async listNodes(): Promise<GraphNode[]> {
    return [...this.nodes.values()];
  }

  async updateNode(node: GraphNode): Promise<GraphNode> {
    if (!this.nodes.has(node.id)) throw new NodeNotFoundError(`Node not found: ${node.id}`);
    this.nodes.set(node.id, node);
    return node;
  }

  async updateNodes(nodes: GraphNode[]): Promise<GraphNode[]> {
    for (const node of nodes) await this.updateNode(node);
    return nodes;
  }

  async deleteNode(id: string): Promise<void> {
    this.nodes.delete(id);
    for (const edge of [...this.edges.values()]) {
      if (edge.sourceNodeId === id || edge.targetNodeId === id) this.edges.delete(edge.id);
    }
  }

  async deleteNodes(ids: string[]): Promise<void> {
    for (const id of ids) await this.deleteNode(id);
  }

  async createEdge(edge: GraphEdge): Promise<GraphEdge> {
    this.edges.set(edge.id, edge);
    return edge;
  }

  async createEdges(edges: GraphEdge[]): Promise<GraphEdge[]> {
    for (const edge of edges) this.edges.set(edge.id, edge);
    return edges;
  }

  async getEdgeById(id: string): Promise<GraphEdge | null> {
    return this.edges.get(id) ?? null;
  }

  async listEdges(): Promise<GraphEdge[]> {
    return [...this.edges.values()];
  }

  async updateEdge(edge: GraphEdge): Promise<GraphEdge> {
    if (!this.edges.has(edge.id)) throw new EdgeNotFoundError(`Edge not found: ${edge.id}`);
    this.edges.set(edge.id, edge);
    return edge;
  }

  async updateEdges(edges: GraphEdge[]): Promise<GraphEdge[]> {
    for (const edge of edges) await this.updateEdge(edge);
    return edges;
  }

  async deleteEdge(id: string): Promise<void> {
    this.edges.delete(id);
  }

  async deleteEdges(ids: string[]): Promise<void> {
    for (const id of ids) await this.deleteEdge(id);
  }

  async getNeighbors(nodeId: string): Promise<GraphNode[]> {
    const ids = new Set<string>();
    for (const edge of this.edges.values()) {
      if (edge.sourceNodeId === nodeId) ids.add(edge.targetNodeId);
      if (edge.targetNodeId === nodeId) ids.add(edge.sourceNodeId);
    }
    return [...ids].map((id) => this.nodes.get(id)).filter((node): node is GraphNode => Boolean(node));
  }

  async findPath(sourceNodeId: string, targetNodeId: string): Promise<GraphNode[]> {
    if (!this.nodes.has(sourceNodeId) || !this.nodes.has(targetNodeId)) return [];
    const queue: string[][] = [[sourceNodeId]];
    const visited = new Set<string>([sourceNodeId]);
    while (queue.length > 0) {
      const path = queue.shift()!;
      const current = path[path.length - 1];
      if (current === targetNodeId) return path.map((id) => this.nodes.get(id)).filter((node): node is GraphNode => Boolean(node));
      const neighbors = await this.getNeighbors(current);
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor.id)) {
          visited.add(neighbor.id);
          queue.push([...path, neighbor.id]);
        }
      }
    }
    return [];
  }

  async getNodesByAlias(alias: string): Promise<GraphNode[]> {
    const normalized = alias.trim().toLocaleLowerCase();
    return [...this.nodes.values()].filter((node) => node.aliases.some((item) => item.trim().toLocaleLowerCase() === normalized));
  }

  async getNodesByType(type: string): Promise<GraphNode[]> {
    return [...this.nodes.values()].filter((node) => node.type === type);
  }

  async getEdgesBySourceNode(sourceNodeId: string): Promise<GraphEdge[]> {
    return [...this.edges.values()].filter((edge) => edge.sourceNodeId === sourceNodeId);
  }

  async getEdgesByTargetNode(targetNodeId: string): Promise<GraphEdge[]> {
    return [...this.edges.values()].filter((edge) => edge.targetNodeId === targetNodeId);
  }

  async createEvidence(evidence: GraphEvidence): Promise<GraphEvidence> {
    this.evidence.set(evidence.id, evidence);
    return evidence;
  }

  async getEvidenceById(id: string): Promise<GraphEvidence | null> {
    return this.evidence.get(id) ?? null;
  }

  async listEvidence(): Promise<GraphEvidence[]> {
    return [...this.evidence.values()];
  }
}
