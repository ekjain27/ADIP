import type { GraphEdge, GraphNode, ReasoningPath, ReasoningQuery } from "../domain/models.js";
import type { GraphReadPort } from "../ports/index.js";
import { ReasoningConfidenceService, TemporalReasoningService } from "../services/index.js";

export interface KnowledgeGraphPublicNode {
  id: string;
  type: string;
  canonicalName: string;
  aliases?: readonly string[];
  attributes?: Readonly<Record<string, unknown>>;
  confidence?: number;
  sourceIds?: readonly string[];
  visibility?: {
    hidden?: boolean;
    allowedRoles?: readonly string[];
  };
}

export interface KnowledgeGraphPublicEdge {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  relationType: string;
  weight?: number;
  confidence?: number;
  evidenceConfidence?: number;
  evidenceIds?: readonly string[];
  temporalScope?: {
    validFrom?: string;
    validTo?: string | null;
  };
  visibility?: {
    hidden?: boolean;
    allowedRoles?: readonly string[];
  };
}

export interface KnowledgeGraphReadRepository {
  getNodeById(id: string): Promise<KnowledgeGraphPublicNode | null>;
  getNodeByCanonicalName(canonicalName: string): Promise<KnowledgeGraphPublicNode | null>;
  getNeighbors(nodeId: string): Promise<KnowledgeGraphPublicNode[]>;
  getEdgesBySourceNode(sourceNodeId: string): Promise<KnowledgeGraphPublicEdge[]>;
  getEdgesByTargetNode(targetNodeId: string): Promise<KnowledgeGraphPublicEdge[]>;
}

export interface KnowledgeGraphReadAdapterOptions {
  mapRelationType?: (relationType: string) => string;
}

const defaultRelationMapper = (relationType: string): string => relationType.toUpperCase();

const toReasoningNode = (node: KnowledgeGraphPublicNode): GraphNode => ({
  id: node.id,
  canonicalName: node.canonicalName,
  type: node.type,
  labels: node.aliases,
  properties: node.attributes,
  confidence: node.confidence,
  evidenceIds: node.sourceIds,
  visibility: node.visibility
});

const toReasoningEdge = (edge: KnowledgeGraphPublicEdge, mapRelationType: (relationType: string) => string): GraphEdge => ({
  id: edge.id,
  sourceNodeId: edge.sourceNodeId,
  targetNodeId: edge.targetNodeId,
  type: mapRelationType(edge.relationType),
  confidence: edge.confidence ?? edge.weight,
  evidenceConfidence: edge.evidenceConfidence ?? edge.confidence,
  validFrom: edge.temporalScope?.validFrom,
  validTo: edge.temporalScope?.validTo ?? undefined,
  evidenceIds: edge.evidenceIds,
  visibility: edge.visibility
});

export class KnowledgeGraphReadAdapter implements GraphReadPort {
  private readonly temporal = new TemporalReasoningService();
  private readonly confidence = new ReasoningConfidenceService();
  private readonly mapRelationType: (relationType: string) => string;

  constructor(
    private readonly repository: KnowledgeGraphReadRepository,
    options: KnowledgeGraphReadAdapterOptions = {}
  ) {
    this.mapRelationType = options.mapRelationType ?? defaultRelationMapper;
  }

  async getNodeById(id: string): Promise<GraphNode | null> {
    const node = await this.repository.getNodeById(id);
    return node ? toReasoningNode(node) : null;
  }

  async getNodeByCanonicalName(canonicalName: string): Promise<GraphNode | null> {
    const node = await this.repository.getNodeByCanonicalName(canonicalName);
    return node ? toReasoningNode(node) : null;
  }

  async getNeighbors(nodeId: string): Promise<readonly GraphNode[]> {
    return (await this.repository.getNeighbors(nodeId)).map(toReasoningNode);
  }

  async getEdgesByNodeId(nodeId: string): Promise<readonly GraphEdge[]> {
    const [sourceEdges, targetEdges] = await Promise.all([
      this.repository.getEdgesBySourceNode(nodeId),
      this.repository.getEdgesByTargetNode(nodeId)
    ]);
    return [...new Map([...sourceEdges, ...targetEdges].map((edge) => [edge.id, edge])).values()].map((edge) =>
      toReasoningEdge(edge, this.mapRelationType)
    );
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
    const minConfidence = query.minConfidence ?? 0;
    const walk = async (node: GraphNode, nodes: GraphNode[], edges: GraphEdge[], visited: Set<string>): Promise<void> => {
      if (edges.length >= maxDepth) {
        return;
      }
      for (const edge of (await this.getEdgesByNodeId(node.id)).filter((candidate) => candidate.sourceNodeId === node.id)) {
        if (query.relationshipTypes?.length && !query.relationshipTypes.includes(edge.type)) {
          continue;
        }
        if (query.reasoningDate && !this.temporal.isEdgeValid(edge, query.reasoningDate)) {
          continue;
        }
        const next = await this.getNodeById(edge.targetNodeId);
        if (!next || visited.has(next.id)) {
          continue;
        }
        const nextEdges = [...edges, edge];
        const pathConfidence = this.confidence.calculatePathConfidence(nextEdges);
        if (pathConfidence < minConfidence) {
          continue;
        }
        const nextNodes = [...nodes, next];
        paths.push({
          id: `path_${nextEdges.map((pathEdge) => pathEdge.id).join("_")}`,
          nodes: nextNodes,
          edges: nextEdges,
          relationshipTypes: nextEdges.map((pathEdge) => pathEdge.type),
          confidence: pathConfidence,
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
