import type { Confidence, GraphEdge } from "../domain/models.js";

export const clampConfidence = (value: number): Confidence => Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0));

export class ReasoningConfidenceService {
  calculatePathConfidence(edges: readonly GraphEdge[]): Confidence {
    return edges.length ? clampConfidence(edges.reduce((current, edge) => current * clampConfidence(edge.confidence ?? 1), 1)) : 1;
  }

  evidenceConfidence(edges: readonly GraphEdge[]): Confidence {
    return edges.length ? clampConfidence(edges.reduce((current, edge) => current * clampConfidence(edge.evidenceConfidence ?? 1), 1)) : 1;
  }

  calculateFinalConfidence(input: {
    pathConfidence: Confidence;
    ruleModifier?: Confidence;
    evidenceConfidence?: Confidence;
    temporalValidity?: Confidence;
    conflictPenalty?: Confidence;
  }): Confidence {
    return clampConfidence(
      input.pathConfidence *
        (input.ruleModifier ?? 1) *
        (input.evidenceConfidence ?? 1) *
        (input.temporalValidity ?? 1) *
        (input.conflictPenalty ?? 1)
    );
  }
}
