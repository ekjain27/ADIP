import type { Confidence, GraphEdge, ReasoningConclusion, ReasoningConflict, ReasoningPath } from "../domain/models.js";
import { dateValue } from "./temporal-reasoning.service.js";

const CONTRADICTS: Readonly<Record<string, string>> = {
  SUPPLIES: "DOES_NOT_SUPPLY",
  DOES_NOT_SUPPLY: "SUPPLIES",
  PRODUCES: "DOES_NOT_PRODUCE",
  DOES_NOT_PRODUCE: "PRODUCES",
  IS_A: "NOT_IS_A",
  NOT_IS_A: "IS_A",
  AFFECTS: "DOES_NOT_AFFECT",
  DOES_NOT_AFFECT: "AFFECTS"
};

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;

export class ConflictDetectionService {
  detect(paths: readonly ReasoningPath[], conclusions: readonly ReasoningConclusion[]): readonly ReasoningConflict[] {
    const conflicts: ReasoningConflict[] = [];
    const uniqueEdges = [...new Map(paths.flatMap((path) => path.edges).map((edge) => [edge.id, edge])).values()];
    for (const edge of uniqueEdges) {
      for (const other of uniqueEdges) {
        if (edge.id >= other.id) {
          continue;
        }
        const samePair = edge.sourceNodeId === other.sourceNodeId && edge.targetNodeId === other.targetNodeId;
        if (samePair && CONTRADICTS[edge.type] === other.type) {
          conflicts.push(this.conflict("CONTRADICTORY_RELATIONSHIP", [edge.sourceNodeId, edge.targetNodeId], [edge.id, other.id], "Contradictory relationships were found on the same ordered node pair.", 0.9));
        }
        if (samePair && CONTRADICTS[edge.type] === other.type && this.overlaps(edge, other)) {
          conflicts.push(this.conflict("TEMPORAL_OVERLAP", [edge.sourceNodeId, edge.targetNodeId], [edge.id, other.id], "Contradictory relationships are valid during overlapping time intervals.", 0.95));
        }
        if (samePair && edge.type === other.type && Math.abs((edge.confidence ?? 1) - (other.confidence ?? 1)) >= 0.5) {
          conflicts.push(this.conflict("CONFIDENCE_DISAGREEMENT", [edge.sourceNodeId, edge.targetNodeId], [edge.id, other.id], "Equivalent relationships have materially different confidence values.", 0.7));
        }
        if (samePair && ((edge.type === "IS_A" && other.type === "NOT_IS_A") || (edge.type === "NOT_IS_A" && other.type === "IS_A"))) {
          conflicts.push(this.conflict("ONTOLOGY_MISMATCH", [edge.sourceNodeId, edge.targetNodeId], [edge.id, other.id], "Ontology hierarchy contains incompatible inheritance assertions.", 0.9));
        }
        if (edge.sourceNodeId === other.targetNodeId && edge.targetNodeId === other.sourceNodeId && edge.type === other.type) {
          conflicts.push(this.conflict("CIRCULAR_DEPENDENCY", [edge.sourceNodeId, edge.targetNodeId], [edge.id, other.id], "A circular dependency was found across reciprocal relationships.", 0.8));
        }
      }
    }
    for (const conclusion of conclusions) {
      const opposite = conclusions.find(
        (candidate) =>
          candidate.id !== conclusion.id &&
          candidate.sourceNodeId === conclusion.sourceNodeId &&
          candidate.targetNodeId === conclusion.targetNodeId &&
          CONTRADICTS[conclusion.relationshipType] === candidate.relationshipType
      );
      if (opposite) {
        conflicts.push(this.conflict("CONTRADICTORY_RELATIONSHIP", [conclusion.sourceNodeId, conclusion.targetNodeId], [], "Inferred conclusions contradict each other.", 0.8));
      }
    }
    return [...new Map(conflicts.map((conflict) => [conflict.id, conflict])).values()];
  }

  private overlaps(left: GraphEdge, right: GraphEdge): boolean {
    const leftStart = left.validFrom ? dateValue(left.validFrom) : Number.NEGATIVE_INFINITY;
    const leftEnd = left.validTo ? dateValue(left.validTo) : Number.POSITIVE_INFINITY;
    const rightStart = right.validFrom ? dateValue(right.validFrom) : Number.NEGATIVE_INFINITY;
    const rightEnd = right.validTo ? dateValue(right.validTo) : Number.POSITIVE_INFINITY;
    return leftStart <= rightEnd && rightStart <= leftEnd;
  }

  private conflict(
    type: ReasoningConflict["type"],
    nodeIds: readonly string[],
    edgeIds: readonly string[],
    description: string,
    confidence: Confidence
  ): ReasoningConflict {
    return {
      id: stableId("conflict", [type, ...nodeIds, ...edgeIds]),
      type,
      severity: confidence >= 0.9 ? "high" : confidence >= 0.75 ? "medium" : "low",
      nodeIds,
      edgeIds,
      description,
      confidence
    };
  }
}
