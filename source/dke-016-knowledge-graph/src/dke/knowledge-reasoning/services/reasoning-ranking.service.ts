import type { ReasoningPath } from "../domain/models.js";

export class ReasoningRankingService {
  rankPaths(paths: readonly ReasoningPath[]): readonly ReasoningPath[] {
    return [...paths].sort((left, right) => right.confidence - left.confidence || left.edges.length - right.edges.length || left.id.localeCompare(right.id));
  }
}
