import type { ReasoningRule } from "../domain/models.js";
import type { RuleRepositoryPort } from "../ports/index.js";

export class InMemoryRuleRepository implements RuleRepositoryPort {
  private readonly rules: Map<string, ReasoningRule>;

  constructor(rules: readonly ReasoningRule[] = []) {
    this.rules = new Map(rules.map((rule) => [rule.id, rule]));
  }

  async listRules(): Promise<readonly ReasoningRule[]> {
    return [...this.rules.values()];
  }

  async getRuleById(id: string): Promise<ReasoningRule | null> {
    return this.rules.get(id) ?? null;
  }
}

export const createDefaultRules = (): readonly ReasoningRule[] => [
  {
    id: "rule_supplies_produces_affects",
    name: "Supplier production impact",
    when: { path: ["SUPPLIES", "PRODUCES"] },
    then: { relationshipType: "AFFECTS" },
    confidenceModifier: 0.95,
    enabled: true
  }
];
