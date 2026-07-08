import type { ReasoningMetrics } from "../domain/models.js";
import type { MetricsPort } from "../ports/index.js";
import { defaultReasoningMetrics } from "../services/index.js";

export class InMemoryMetrics implements MetricsPort {
  private values: ReasoningMetrics = defaultReasoningMetrics();
  private observations: Partial<Record<keyof ReasoningMetrics, number[]>> = {};

  increment(metric: keyof ReasoningMetrics, value = 1): void {
    this.values = { ...this.values, [metric]: this.values[metric] + value };
  }

  observe(metric: keyof ReasoningMetrics, value: number): void {
    const values = [...(this.observations[metric] ?? []), value];
    this.observations = { ...this.observations, [metric]: values };
    this.values = { ...this.values, [metric]: values.reduce((sum, item) => sum + item, 0) / values.length };
  }

  snapshot(): ReasoningMetrics {
    return { ...this.values };
  }
}
