import { GraphReadError, ReasoningValidationError } from "../domain/errors.js";
import type { Confidence, GraphEdge, GraphNode, ReasoningPath, ReasoningQuery } from "../domain/models.js";
import type { GraphReadPort } from "../ports/index.js";
import { ReasoningConfidenceService } from "./reasoning-confidence.service.js";
import { TemporalReasoningService } from "./temporal-reasoning.service.js";

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;

export const canSeeReasoningItem = (
  item: Pick<GraphNode | GraphEdge, "visibility" | "evidenceIds">,
  query: ReasoningQuery,
  nodeId?: string
): boolean => {
  if (nodeId && query.visibility?.allowedNodeIds && !query.visibility.allowedNodeIds.includes(nodeId)) {
    return false;
  }
  if (item.visibility?.hidden) {
    return false;
  }
  const allowedRoles = item.visibility?.allowedRoles;
  if (allowedRoles?.length) {
    const roles = query.visibility?.roles ?? [];
    if (!allowedRoles.some((role) => roles.includes(role))) {
      return false;
    }
  }
  const evidenceIds = item.evidenceIds ?? [];
  if (query.visibility?.allowedEvidenceIds && evidenceIds.length) {
    return evidenceIds.some((id) => query.visibility?.allowedEvidenceIds?.includes(id));
  }
  return true;
};

export class PathReasoningService {
  constructor(
    private readonly graph: GraphReadPort,
    private readonly temporal: TemporalReasoningService,
    private readonly confidence: ReasoningConfidenceService
  ) {}

  async findPaths(query: ReasoningQuery): Promise<readonly ReasoningPath[]> {
    const source = await this.resolveSource(query);
    const maxDepth = query.maxDepth ?? 4;
    const minConfidence = query.minConfidence ?? 0;
    if (maxDepth < 1) {
      throw new ReasoningValidationError("maxDepth must be at least 1.");
    }
    if (maxDepth > 12) {
      throw new ReasoningValidationError("maxDepth must be 12 or less.");
    }
    const paths: ReasoningPath[] = [];
    await this.walk(source, query, maxDepth, minConfidence, [source], [], new Set([source.id]), paths);
    return paths;
  }

  private async resolveSource(query: ReasoningQuery): Promise<GraphNode> {
    const node = query.sourceNodeId
      ? await this.graph.getNodeById(query.sourceNodeId)
      : query.sourceCanonicalName
        ? await this.graph.getNodeByCanonicalName(query.sourceCanonicalName)
        : null;
    if (!node) {
      throw new GraphReadError("Reasoning source node was not found.");
    }
    if (!canSeeReasoningItem(node, query, node.id)) {
      throw new GraphReadError("Reasoning source node is not accessible.");
    }
    return node;
  }

  private async walk(
    current: GraphNode,
    query: ReasoningQuery,
    maxDepth: number,
    minConfidence: Confidence,
    nodes: GraphNode[],
    edges: GraphEdge[],
    visited: Set<string>,
    paths: ReasoningPath[]
  ): Promise<void> {
    if (edges.length >= maxDepth) {
      return;
    }
    const outgoing = await this.graph.getEdgesByNodeId(current.id);
    for (const edge of outgoing) {
      if (edge.sourceNodeId !== current.id || !canSeeReasoningItem(edge, query)) {
        continue;
      }
      if (query.relationshipTypes?.length && !query.relationshipTypes.includes(edge.type)) {
        continue;
      }
      if (!this.temporal.isEdgeValid(edge, query.reasoningDate ?? new Date().toISOString())) {
        continue;
      }
      const next = await this.graph.getNodeById(edge.targetNodeId);
      if (!next || !canSeeReasoningItem(next, query, next.id) || visited.has(next.id)) {
        continue;
      }
      const nextEdges = [...edges, edge];
      const pathConfidence = this.confidence.calculatePathConfidence(nextEdges);
      if (pathConfidence < minConfidence) {
        continue;
      }
      const nextNodes = [...nodes, next];
      const path: ReasoningPath = {
        id: stableId("path", nextEdges.map((pathEdge) => pathEdge.id)),
        nodes: nextNodes,
        edges: nextEdges,
        relationshipTypes: nextEdges.map((pathEdge) => pathEdge.type),
        confidence: pathConfidence,
        temporalValidity: 1
      };
      if ((!query.targetNodeId || query.targetNodeId === next.id) && (!query.targetCanonicalName || query.targetCanonicalName === next.canonicalName)) {
        paths.push(path);
      }
      visited.add(next.id);
      await this.walk(next, query, maxDepth, minConfidence, nextNodes, nextEdges, visited, paths);
      visited.delete(next.id);
    }
  }
}
