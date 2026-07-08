import type { KnowledgeGraphMetricsSnapshot } from "../domain/index.js";

export interface MetricsPort {
  increment(metric: keyof Omit<KnowledgeGraphMetricsSnapshot, "averageNodeConfidence" | "averageEdgeConfidence">, amount?: number): void;
  recordNodeConfidence(confidence: number): void;
  recordEdgeConfidence(confidence: number): void;
  snapshot(): KnowledgeGraphMetricsSnapshot;
}
