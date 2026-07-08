import type { RelationshipConfidenceFactors } from "../domain/index.js";

export class GraphConfidenceService {
  relationshipConfidence(factors: RelationshipConfidenceFactors): number {
    const score =
      factors.sourceReliability *
      factors.extractionConfidence *
      factors.ontologyMatch *
      factors.temporalValidity *
      factors.crossSourceAgreement;
    return Math.max(0, Math.min(1, Number(score.toFixed(4))));
  }
}
