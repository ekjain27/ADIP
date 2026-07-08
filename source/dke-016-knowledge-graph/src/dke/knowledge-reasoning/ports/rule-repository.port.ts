import type { ReasoningRule } from "../domain/models.js";

export interface RuleRepositoryPort {
  listRules(): Promise<readonly ReasoningRule[]>;
  getRuleById(id: string): Promise<ReasoningRule | null>;
}
