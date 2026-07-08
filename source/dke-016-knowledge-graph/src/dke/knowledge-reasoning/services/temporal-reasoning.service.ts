import { TemporalReasoningError } from "../domain/errors.js";
import type { GraphEdge, TemporalReasoningResult } from "../domain/models.js";

export const dateValue = (value: string): number => {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) {
    throw new TemporalReasoningError(`Invalid date value: ${value}`);
  }
  return parsed;
};

export class TemporalReasoningService {
  isEdgeValid(edge: GraphEdge, reasoningDate: string): boolean {
    if (edge.validFrom && edge.validTo && dateValue(edge.validFrom) > dateValue(edge.validTo)) {
      throw new TemporalReasoningError(`Edge ${edge.id} has validFrom after validTo.`);
    }
    const date = dateValue(reasoningDate);
    return (!edge.validFrom || dateValue(edge.validFrom) <= date) && (!edge.validTo || date <= dateValue(edge.validTo));
  }

  evaluate(edges: readonly GraphEdge[], reasoningDate = new Date().toISOString()): TemporalReasoningResult {
    const validEdges: GraphEdge[] = [];
    const rejectedEdges: { edge: GraphEdge; reason: string }[] = [];
    for (const edge of edges) {
      if (this.isEdgeValid(edge, reasoningDate)) {
        validEdges.push(edge);
      } else {
        rejectedEdges.push({ edge, reason: "Relationship is outside the requested reasoningDate." });
      }
    }
    return { reasoningDate, validEdges, rejectedEdges };
  }
}
