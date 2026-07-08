import type { KnowledgeGraphMetricsSnapshot } from "../domain/index.js";
import type { MetricsPort } from "../ports/index.js";

export class InMemoryMetricsAdapter implements MetricsPort {
  private values: KnowledgeGraphMetricsSnapshot = {
    nodesCreated: 0,
    nodesUpdated: 0,
    edgesCreated: 0,
    evidenceStored: 0,
    duplicatesMerged: 0,
    validationFailures: 0,
    constructionFailures: 0,
    constructionSuccesses: 0,
    averageNodeConfidence: 0,
    averageEdgeConfidence: 0,
  };
  private nodeConfidenceTotal = 0;
  private nodeConfidenceCount = 0;
  private edgeConfidenceTotal = 0;
  private edgeConfidenceCount = 0;

  increment(metric: keyof Omit<KnowledgeGraphMetricsSnapshot, "averageNodeConfidence" | "averageEdgeConfidence">, amount = 1): void {
    this.values[metric] += amount;
  }

  recordNodeConfidence(confidence: number): void {
    this.nodeConfidenceTotal += confidence;
    this.nodeConfidenceCount += 1;
    this.values.averageNodeConfidence = Number((this.nodeConfidenceTotal / this.nodeConfidenceCount).toFixed(4));
  }

  recordEdgeConfidence(confidence: number): void {
    this.edgeConfidenceTotal += confidence;
    this.edgeConfidenceCount += 1;
    this.values.averageEdgeConfidence = Number((this.edgeConfidenceTotal / this.edgeConfidenceCount).toFixed(4));
  }

  snapshot(): KnowledgeGraphMetricsSnapshot {
    return { ...this.values };
  }
}
