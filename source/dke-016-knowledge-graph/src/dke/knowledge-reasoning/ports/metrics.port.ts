import type { ReasoningMetrics } from "../domain/models.js";

export interface MetricsPort {
  increment(metric: keyof ReasoningMetrics, value?: number): void;
  observe(metric: keyof ReasoningMetrics, value: number): void;
  snapshot(): ReasoningMetrics;
}
