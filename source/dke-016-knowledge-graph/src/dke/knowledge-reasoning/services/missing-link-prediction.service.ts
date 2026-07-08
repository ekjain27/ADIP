import type { MissingLinkSuggestion, ReasoningConclusion, ReasoningQuery } from "../domain/models.js";
import type { GraphReadPort } from "../ports/index.js";
import { canSeeReasoningItem } from "./path-reasoning.service.js";

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;

export class MissingLinkPredictionService {
  constructor(private readonly graph: GraphReadPort) {}

  async suggest(query: ReasoningQuery, conclusions: readonly ReasoningConclusion[], minConfidence = 0.7): Promise<readonly MissingLinkSuggestion[]> {
    const suggestions: MissingLinkSuggestion[] = [];
    for (const conclusion of conclusions) {
      if (conclusion.confidence < minConfidence) {
        continue;
      }
      const directExists = (await this.graph.getEdgesByNodeId(conclusion.sourceNodeId)).some(
        (edge) => edge.targetNodeId === conclusion.targetNodeId && edge.type === conclusion.relationshipType && canSeeReasoningItem(edge, query)
      );
      if (!directExists) {
        suggestions.push({
          id: stableId("missing", [conclusion.sourceNodeId, conclusion.relationshipType, conclusion.targetNodeId]),
          sourceNodeId: conclusion.sourceNodeId,
          targetNodeId: conclusion.targetNodeId,
          relationshipType: conclusion.relationshipType,
          confidence: conclusion.confidence,
          supportingPathIds: conclusion.pathId ? [conclusion.pathId] : [],
          reason: "Strong inferred relationship exists, but no accessible direct edge exists."
        });
      }
    }
    return suggestions;
  }
}
