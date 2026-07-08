import { GraphValidationError, type GraphEdge, type GraphEvidence, type GraphNode } from "../domain/index.js";

export class GraphValidationService {
  validateNode(node: GraphNode): void {
    if (!node.id) throw new GraphValidationError("Node ID is required.");
    if (!node.canonicalName.trim()) throw new GraphValidationError("Node canonicalName cannot be empty.");
    this.assertConfidence(node.confidence, "Node confidence must be between 0 and 1.");
  }

  validateEdge(edge: GraphEdge, allowSelfEdge = false): void {
    if (!edge.sourceNodeId) throw new GraphValidationError("Edge sourceNodeId is required.");
    if (!edge.targetNodeId) throw new GraphValidationError("Edge targetNodeId is required.");
    if (!edge.relationType) throw new GraphValidationError("Edge relationType is required.");
    this.assertConfidence(edge.confidence, "Edge confidence must be between 0 and 1.");
    if (edge.temporalScope?.validFrom && edge.temporalScope.validTo) {
      if (new Date(edge.temporalScope.validTo).getTime() < new Date(edge.temporalScope.validFrom).getTime()) {
        throw new GraphValidationError("Temporal scope validTo cannot be before validFrom.");
      }
    }
    if (!allowSelfEdge && edge.sourceNodeId === edge.targetNodeId) {
      throw new GraphValidationError("Edge cannot connect a node to itself unless allowSelfEdge=true.");
    }
  }

  validateEvidence(evidence: GraphEvidence): void {
    this.assertConfidence(evidence.confidence, "Evidence confidence must be between 0 and 1.");
  }

  private assertConfidence(value: number, message: string): void {
    if (!Number.isFinite(value) || value < 0 || value > 1) throw new GraphValidationError(message);
  }

  validateUniqueIds(nodes: GraphNode[], edges: GraphEdge[]): void {
    this.assertUnique(nodes.map((node) => node.id), "Duplicate node IDs are not allowed.");
    this.assertUnique(edges.map((edge) => edge.id), "Duplicate edge IDs are not allowed.");
  }

  validateEvidenceReferences(edge: GraphEdge, evidenceIds: Set<string>): void {
    for (const evidenceId of edge.evidenceIds) {
      if (!evidenceIds.has(evidenceId)) throw new GraphValidationError(`Missing evidence ID referenced by edge: ${evidenceId}`);
    }
  }

  private assertUnique(ids: string[], message: string): void {
    if (new Set(ids).size !== ids.length) throw new GraphValidationError(message);
  }
}
