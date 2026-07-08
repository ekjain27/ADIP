import type { GraphNode } from "../domain/index.js";

export interface EntityResolutionPort {
  findDuplicate(candidate: GraphNode, existing: GraphNode[]): Promise<GraphNode | null>;
}
