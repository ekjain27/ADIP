import type { ExplanationTrace, MissingLinkSuggestion, ReasoningConclusion, ReasoningConflict, ReasoningPath } from "../domain/models.js";

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;
const unique = <T>(values: readonly T[]): T[] => [...new Set(values)];

export class ReasoningExplanationService {
  create(input: {
    paths: readonly ReasoningPath[];
    conclusions: readonly ReasoningConclusion[];
    conflicts: readonly ReasoningConflict[];
    suggestions: readonly MissingLinkSuggestion[];
  }): ExplanationTrace {
    const evidenceIds = unique(input.paths.flatMap((path) => path.edges.flatMap((edge) => edge.evidenceIds ?? [])));
    const appliedRuleIds = unique(input.conclusions.flatMap((conclusion) => (conclusion.ruleId ? [conclusion.ruleId] : [])));
    const confidenceEvolution = input.conclusions.length ? input.conclusions.map((conclusion) => conclusion.confidence) : input.paths.map((path) => path.confidence);
    return {
      id: stableId("explanation", [...input.paths.map((path) => path.id), ...input.conclusions.map((conclusion) => conclusion.id)]),
      summary: `Evaluated ${input.paths.length} path(s), produced ${input.conclusions.length} conclusion(s), detected ${input.conflicts.length} conflict(s), and suggested ${input.suggestions.length} missing link(s).`,
      appliedRuleIds,
      evidenceIds,
      confidenceEvolution,
      steps: [
        ...input.paths.map((path, index) => ({
          id: stableId("step_path", [String(index), path.id]),
          kind: "path" as const,
          description: `Found path ${path.nodes.map((node) => node.canonicalName).join(" -> ")} with confidence ${path.confidence.toFixed(4)}.`,
          outputConfidence: path.confidence,
          evidenceIds: unique(path.edges.flatMap((edge) => edge.evidenceIds ?? []))
        })),
        ...input.conclusions.map((conclusion) => ({
          id: stableId("step_rule", [conclusion.id]),
          kind: conclusion.ruleId ? ("rule" as const) : ("ontology" as const),
          description: conclusion.summary,
          outputConfidence: conclusion.confidence,
          evidenceIds: conclusion.evidenceIds
        })),
        ...input.conflicts.map((conflict) => ({
          id: stableId("step_conflict", [conflict.id]),
          kind: "conflict" as const,
          description: conflict.description,
          outputConfidence: conflict.confidence,
          evidenceIds: []
        })),
        ...input.suggestions.map((suggestion) => ({
          id: stableId("step_missing", [suggestion.id]),
          kind: "missing-link" as const,
          description: suggestion.reason,
          outputConfidence: suggestion.confidence,
          evidenceIds: []
        }))
      ]
    };
  }
}
