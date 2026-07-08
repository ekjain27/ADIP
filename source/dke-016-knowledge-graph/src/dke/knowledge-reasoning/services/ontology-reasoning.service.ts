import type { GraphNode, ReasoningConclusion, ReasoningPath, ReasoningQuery } from "../domain/models.js";
import type { GraphReadPort, OntologyReasoningPort } from "../ports/index.js";
import { canSeeReasoningItem } from "./path-reasoning.service.js";
import { TemporalReasoningService } from "./temporal-reasoning.service.js";

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;
const unique = <T>(values: readonly T[]): T[] => [...new Set(values)];

export class OntologyReasoningService implements OntologyReasoningPort {
  constructor(
    private readonly graph: GraphReadPort,
    private readonly temporal: TemporalReasoningService
  ) {}

  async getAncestors(node: GraphNode, query: ReasoningQuery): Promise<readonly GraphNode[]> {
    const ancestors: GraphNode[] = [];
    const visited = new Set<string>([node.id]);
    let frontier: GraphNode[] = [node];
    while (frontier.length) {
      const nextFrontier: GraphNode[] = [];
      for (const current of frontier) {
        for (const edge of await this.graph.getEdgesByNodeId(current.id)) {
          if (
            edge.sourceNodeId !== current.id ||
            edge.type !== "IS_A" ||
            !this.temporal.isEdgeValid(edge, query.reasoningDate ?? new Date().toISOString()) ||
            !canSeeReasoningItem(edge, query)
          ) {
            continue;
          }
          const ancestor = await this.graph.getNodeById(edge.targetNodeId);
          if (!ancestor || visited.has(ancestor.id) || !canSeeReasoningItem(ancestor, query, ancestor.id)) {
            continue;
          }
          visited.add(ancestor.id);
          ancestors.push(ancestor);
          nextFrontier.push(ancestor);
        }
      }
      frontier = nextFrontier;
    }
    return ancestors;
  }

  async inferInheritance(_query: ReasoningQuery, paths: readonly ReasoningPath[]): Promise<readonly ReasoningConclusion[]> {
    return paths
      .filter((path) => path.relationshipTypes.every((type) => type === "IS_A"))
      .map((path) => {
        const source = path.nodes[0];
        const target = path.nodes[path.nodes.length - 1];
        return {
          id: stableId("ontology", [path.id]),
          sourceNodeId: source.id,
          targetNodeId: target.id,
          relationshipType: "INHERITS_FROM",
          confidence: path.confidence,
          pathId: path.id,
          evidenceIds: unique(path.edges.flatMap((edge) => edge.evidenceIds ?? [])),
          summary: `${source.canonicalName} inherits ontology properties from ${target.canonicalName}.`
        };
      });
  }
}
