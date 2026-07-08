export interface ExplainabilitySummary {
  readonly status: "ready" | "generated" | "refreshed" | "exported";
  readonly lastAnalysisAt: string;
  readonly decisionId: string;
  readonly confidence: number;
  readonly cards: readonly SummaryCard[];
}

export interface SummaryCard {
  readonly id: string;
  readonly title: string;
  readonly value: string;
  readonly detail: string;
  readonly status: "strong" | "stable" | "review" | "complete";
}

export interface DecisionReasoning {
  readonly topFactors: readonly string[];
  readonly positiveFactors: readonly string[];
  readonly negativeFactors: readonly string[];
  readonly riskFactors: readonly string[];
  readonly constraints: readonly string[];
  readonly decisionPathSummary: string;
}

export interface FeatureImportanceItem {
  readonly feature: string;
  readonly weight: number;
  readonly impact: string;
  readonly direction: "positive" | "negative" | "neutral";
  readonly confidence: number;
}

export interface AnalyticsMetricGroup {
  readonly id: string;
  readonly title: string;
  readonly metrics: readonly SummaryCard[];
}

export interface ExplainabilityTimelineEvent {
  readonly id: string;
  readonly title: string;
  readonly type: "decision" | "evaluation" | "ranking" | "optimization" | "governance" | "recommendation" | "explainability" | "analytics";
  readonly timestamp: string;
  readonly detail: string;
}

export interface RecommendationSummary {
  readonly primaryRecommendation: string;
  readonly alternativeRecommendation: string;
  readonly confidence: number;
  readonly reason: string;
  readonly businessImpact: string;
}

export interface ExplainabilityAnalyticsSnapshot {
  readonly summary: ExplainabilitySummary;
  readonly reasoning: DecisionReasoning;
  readonly featureImportance: readonly FeatureImportanceItem[];
  readonly analytics: readonly AnalyticsMetricGroup[];
  readonly timeline: readonly ExplainabilityTimelineEvent[];
  readonly recommendation: RecommendationSummary;
}

export interface ExplainabilityAnalyticsClient {
  getExplainabilitySummary(): Promise<ExplainabilitySummary>;
  getDecisionReasoning(): Promise<DecisionReasoning>;
  getFeatureImportance(): Promise<readonly FeatureImportanceItem[]>;
  getAnalyticsMetrics(): Promise<readonly AnalyticsMetricGroup[]>;
  getRecommendationSummary(): Promise<RecommendationSummary>;
  getTimeline(): Promise<readonly ExplainabilityTimelineEvent[]>;
  generateExplanation(): Promise<ExplainabilityAnalyticsSnapshot>;
  refreshAnalytics(): Promise<ExplainabilityAnalyticsSnapshot>;
}
