import type { GraphNode, ReasoningQuery } from "../domain/models.js";

export interface OntologyReasoningPort {
  getAncestors(node: GraphNode, query: ReasoningQuery): Promise<readonly GraphNode[]>;
}
