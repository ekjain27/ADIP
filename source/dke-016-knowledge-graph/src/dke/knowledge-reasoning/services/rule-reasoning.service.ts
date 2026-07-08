import type { ReasoningConclusion, ReasoningPath, ReasoningRule } from "../domain/models.js";
import type { RuleRepositoryPort } from "../ports/index.js";
import { ReasoningConfidenceService } from "./reasoning-confidence.service.js";

const stableId = (prefix: string, parts: readonly string[]): string =>
  `${prefix}_${parts.join("_").replace(/[^A-Za-z0-9_-]/g, "_")}`;
const unique = <T>(values: readonly T[]): T[] => [...new Set(values)];

export class RuleReasoningService {
  constructor(
    private readonly rules: RuleRepositoryPort,
    private readonly confidence: ReasoningConfidenceService
  ) {}

  async infer(paths: readonly ReasoningPath[]): Promise<readonly ReasoningConclusion[]> {
    const rules = (await this.rules.listRules()).filter((rule) => rule.enabled !== false);
    const conclusions: ReasoningConclusion[] = [];
    for (const path of paths) {
      for (const rule of rules) {
        if (!this.matches(rule, path)) {
          continue;
        }
        const source = path.nodes[0];
        const target = path.nodes[path.nodes.length - 1];
        conclusions.push({
          id: stableId("conclusion", [path.id, rule.id]),
          sourceNodeId: source.id,
          targetNodeId: target.id,
          relationshipType: rule.then.relationshipType,
          confidence: this.confidence.calculateFinalConfidence({
            pathConfidence: path.confidence,
            ruleModifier: rule.confidenceModifier,
            evidenceConfidence: this.confidence.evidenceConfidence(path.edges),
            temporalValidity: path.temporalValidity
          }),
          ruleId: rule.id,
          pathId: path.id,
          evidenceIds: unique(path.edges.flatMap((edge) => edge.evidenceIds ?? [])),
          summary: `${source.canonicalName} ${rule.then.relationshipType} ${target.canonicalName} inferred by ${rule.name}.`
        });
      }
    }
    return conclusions;
  }

  private matches(rule: ReasoningRule, path: ReasoningPath): boolean {
    const source = path.nodes[0];
    const target = path.nodes[path.nodes.length - 1];
    return (
      rule.when.path.length === path.relationshipTypes.length &&
      rule.when.path.every((type, index) => type === path.relationshipTypes[index]) &&
      (!rule.when.sourceType || rule.when.sourceType === source.type) &&
      (!rule.when.targetType || rule.when.targetType === target.type)
    );
  }
}
