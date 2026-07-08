import type { AnalyticsMetricGroup, DecisionReasoning, ExplainabilityAnalyticsClient, ExplainabilityAnalyticsSnapshot, ExplainabilitySummary, ExplainabilityTimelineEvent, FeatureImportanceItem, RecommendationSummary } from "./types.js";

const summary: ExplainabilitySummary = {
  status: "ready",
  lastAnalysisAt: "2026-07-01T10:10:00.000Z",
  decisionId: "DEC-2026-001",
  confidence: 0.91,
  cards: [
    { id: "confidence", title: "Overall Confidence", value: "91%", detail: "Backend explanation confidence.", status: "strong" },
    { id: "stability", title: "Decision Stability", value: "Stable", detail: "Low sensitivity drift.", status: "stable" },
    { id: "quality", title: "Decision Quality", value: "88/100", detail: "Backend evaluation quality score.", status: "strong" },
    { id: "strength", title: "Recommendation Strength", value: "High", detail: "Primary recommendation supported.", status: "strong" },
    { id: "governance", title: "Governance Status", value: "Approved", detail: "Policy gate satisfied.", status: "complete" },
    { id: "completeness", title: "Explainability Completeness", value: "Complete", detail: "All requested explanation sections available.", status: "complete" },
  ],
};

const reasoning: DecisionReasoning = {
  topFactors: ["Governance fit", "Operational readiness", "Regional adoption evidence"],
  positiveFactors: ["Clear policy gates", "Strong rollout checkpoints", "High strategic fit"],
  negativeFactors: ["Regional coordination overhead", "Dependency readiness variance"],
  riskFactors: ["Change-management load", "Support capacity during rollout"],
  constraints: ["Maintain backend freeze", "Approved governance controls", "Two-quarter rollout window"],
  decisionPathSummary: "Backend analysis favors phased regional rollout because it balances impact, governance alignment, and manageable delivery risk.",
};

const featureImportance: readonly FeatureImportanceItem[] = [
  { feature: "Governance fit", weight: 0.25, impact: "High", direction: "positive", confidence: 0.93 },
  { feature: "Operational readiness", weight: 0.22, impact: "High", direction: "positive", confidence: 0.88 },
  { feature: "Time-to-value", weight: 0.2, impact: "Medium", direction: "positive", confidence: 0.84 },
  { feature: "Support load", weight: 0.18, impact: "Medium", direction: "negative", confidence: 0.81 },
  { feature: "Dependency readiness", weight: 0.15, impact: "Medium", direction: "neutral", confidence: 0.79 },
];

const analytics: readonly AnalyticsMetricGroup[] = [
  { id: "evaluation", title: "Evaluation Metrics", metrics: [{ id: "eval-score", title: "Evaluation Score", value: "88", detail: "Selected alternative score.", status: "strong" }] },
  { id: "ranking", title: "Ranking Metrics", metrics: [{ id: "rank", title: "Primary Rank", value: "#1", detail: "Phased rollout is top ranked.", status: "strong" }] },
  { id: "optimization", title: "Optimization Metrics", metrics: [{ id: "tradeoff", title: "Tradeoff Balance", value: "Balanced", detail: "Backend optimization output snapshot.", status: "stable" }] },
  { id: "forecast", title: "Forecast Metrics", metrics: [{ id: "adoption", title: "Adoption Outlook", value: "High", detail: "Forecast output snapshot.", status: "strong" }] },
  { id: "governance", title: "Governance Metrics", metrics: [{ id: "policy", title: "Policy Compliance", value: "Pass", detail: "Governance check output.", status: "complete" }] },
  { id: "performance", title: "Performance Metrics", metrics: [{ id: "latency", title: "Analysis Latency", value: "Nominal", detail: "Backend analytics performance.", status: "stable" }] },
];

const timeline: readonly ExplainabilityTimelineEvent[] = [
  { id: "created", title: "Decision Created", type: "decision", timestamp: "2026-07-01T08:00:00.000Z", detail: "Decision workspace created." },
  { id: "evaluation", title: "Evaluation Finished", type: "evaluation", timestamp: "2026-07-01T09:05:00.000Z", detail: "Backend evaluation completed." },
  { id: "ranking", title: "Ranking Finished", type: "ranking", timestamp: "2026-07-01T09:20:00.000Z", detail: "Backend ranking completed." },
  { id: "optimization", title: "Optimization", type: "optimization", timestamp: "2026-07-01T09:25:00.000Z", detail: "Backend optimization snapshot attached." },
  { id: "governance", title: "Governance", type: "governance", timestamp: "2026-07-01T09:30:00.000Z", detail: "Policy gate checked." },
  { id: "recommendation", title: "Recommendation", type: "recommendation", timestamp: "2026-07-01T09:35:00.000Z", detail: "Recommendation summary produced." },
  { id: "explainability", title: "Explainability Generated", type: "explainability", timestamp: "2026-07-01T10:10:00.000Z", detail: "Explanation package generated." },
];

const recommendation: RecommendationSummary = {
  primaryRecommendation: "Proceed with phased regional rollout.",
  alternativeRecommendation: "Use pilot-first rollout if risk tolerance decreases.",
  confidence: 0.91,
  reason: "Strongest balance of governance fit, operational readiness, and adoption impact.",
  businessImpact: "Accelerates enterprise adoption while preserving governance controls.",
};

const snapshot: ExplainabilityAnalyticsSnapshot = { summary, reasoning, featureImportance, analytics, timeline, recommendation };

function withSingleTimelineEvent(event: ExplainabilityTimelineEvent, events: readonly ExplainabilityTimelineEvent[]): readonly ExplainabilityTimelineEvent[] {
  return [event, ...events.filter((item) => item.id !== event.id)].slice(0, 8);
}

export class DeterministicExplainabilityAnalyticsClient implements ExplainabilityAnalyticsClient {
  async getExplainabilitySummary(): Promise<ExplainabilitySummary> { return snapshot.summary; }
  async getDecisionReasoning(): Promise<DecisionReasoning> { return snapshot.reasoning; }
  async getFeatureImportance(): Promise<readonly FeatureImportanceItem[]> { return snapshot.featureImportance; }
  async getAnalyticsMetrics(): Promise<readonly AnalyticsMetricGroup[]> { return snapshot.analytics; }
  async getRecommendationSummary(): Promise<RecommendationSummary> { return snapshot.recommendation; }
  async getTimeline(): Promise<readonly ExplainabilityTimelineEvent[]> { return snapshot.timeline; }
  async generateExplanation(): Promise<ExplainabilityAnalyticsSnapshot> {
    const generatedAt = new Date().toISOString();
    return {
      ...snapshot,
      summary: {
        ...snapshot.summary,
        status: "generated",
        lastAnalysisAt: generatedAt,
        cards: snapshot.summary.cards.map((card) => card.id === "completeness" ? { ...card, value: "Regenerated", detail: "Explanation snapshot refreshed through adapter." } : card),
      },
      reasoning: {
        ...snapshot.reasoning,
        decisionPathSummary: "Generated explanation snapshot confirms phased regional rollout remains preferred under the latest adapter response.",
      },
      timeline: withSingleTimelineEvent(
        {
          id: "explanation-generated-action",
          title: "Explanation Generated",
          type: "explainability",
          timestamp: generatedAt,
          detail: "Explanation generated through adapter.",
        },
        snapshot.timeline,
      ),
    };
  }
  async refreshAnalytics(): Promise<ExplainabilityAnalyticsSnapshot> {
    const refreshedAt = new Date().toISOString();
    return {
      ...snapshot,
      summary: { ...snapshot.summary, status: "refreshed", lastAnalysisAt: refreshedAt },
      timeline: withSingleTimelineEvent(
        {
          id: "analytics-refreshed-action",
          title: "Analytics Refreshed",
          type: "analytics",
          timestamp: refreshedAt,
          detail: "Analytics refreshed through adapter.",
        },
        snapshot.timeline,
      ),
    };
  }
}

export function createExplainabilityAnalyticsClient(): ExplainabilityAnalyticsClient {
  return new DeterministicExplainabilityAnalyticsClient();
}

export async function getExplainabilityAnalyticsSnapshot(client: ExplainabilityAnalyticsClient): Promise<ExplainabilityAnalyticsSnapshot> {
  const [summary, reasoning, featureImportance, analytics, recommendation, timeline] = await Promise.all([client.getExplainabilitySummary(), client.getDecisionReasoning(), client.getFeatureImportance(), client.getAnalyticsMetrics(), client.getRecommendationSummary(), client.getTimeline()]);
  return { summary, reasoning, featureImportance, analytics, recommendation, timeline };
}
