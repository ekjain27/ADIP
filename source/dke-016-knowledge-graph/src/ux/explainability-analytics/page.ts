import type { ExplainabilityAnalyticsSnapshot, FeatureImportanceItem, SummaryCard } from "./types.js";

export function renderExplainabilityAnalyticsDashboard(snapshot: ExplainabilityAnalyticsSnapshot): string {
  return `
    <section class="ux-xai" aria-labelledby="xai-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-004</p>
          <h1 id="xai-title">Explainability & Analytics Dashboard</h1>
          <div class="ux-workspace-meta">
            <span>${escapeHtml(snapshot.summary.decisionId)}</span>
            <span>Confidence ${Math.round(snapshot.summary.confidence * 100)}%</span>
            <span>Analyzed ${escapeHtml(formatTimestamp(snapshot.summary.lastAnalysisAt))}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(toTitle(snapshot.summary.status))}</span>
      </header>
      <section class="ux-workspace-actions"><button type="button">Generate Explanation</button><button type="button">Refresh Analytics</button><button type="button">Export Report</button></section>
      <section class="ux-grid ux-xai-summary">${snapshot.summary.cards.map(renderSummaryCard).join("")}</section>
      <section class="ux-workspace-grid">
        <article class="ux-panel ux-context-panel"><h2>Decision Reasoning</h2>${renderReasoning(snapshot)}</article>
        <article class="ux-panel ux-context-panel"><h2>Feature Importance</h2><div class="ux-feature-list">${snapshot.featureImportance.map(renderFeature).join("")}</div></article>
        <article class="ux-panel ux-context-panel"><h2>Analytics Dashboard</h2><div class="ux-analytics-grid">${snapshot.analytics.map((group) => `<section><h3>${escapeHtml(group.title)}</h3>${group.metrics.map(renderSummaryCard).join("")}</section>`).join("")}</div></article>
        <article class="ux-panel"><h2>Explainability Timeline</h2><ol class="ux-timeline">${snapshot.timeline.map((event) => `<li data-status="complete"><div><strong>${escapeHtml(event.title)}</strong><span>${escapeHtml(formatTimestamp(event.timestamp))}</span><p>${escapeHtml(event.detail)}</p></div><span class="ux-activity-badge">${escapeHtml(toTitle(event.type))}</span></li>`).join("")}</ol></article>
        <article class="ux-panel"><h2>Recommendation Summary</h2><dl class="ux-inspector-list"><div><dt>Primary</dt><dd>${escapeHtml(snapshot.recommendation.primaryRecommendation)}</dd></div><div><dt>Alternative</dt><dd>${escapeHtml(snapshot.recommendation.alternativeRecommendation)}</dd></div><div><dt>Confidence</dt><dd>${Math.round(snapshot.recommendation.confidence * 100)}%</dd></div><div><dt>Reason</dt><dd>${escapeHtml(snapshot.recommendation.reason)}</dd></div><div><dt>Business Impact</dt><dd>${escapeHtml(snapshot.recommendation.businessImpact)}</dd></div></dl></article>
      </section>
    </section>
  `;
}

function renderReasoning(snapshot: ExplainabilityAnalyticsSnapshot): string {
  const groups = [["Top Factors", snapshot.reasoning.topFactors], ["Positive Factors", snapshot.reasoning.positiveFactors], ["Negative Factors", snapshot.reasoning.negativeFactors], ["Risk Factors", snapshot.reasoning.riskFactors], ["Constraints", snapshot.reasoning.constraints]] as const;
  return `<div class="ux-reasoning-grid">${groups.map(([title, items]) => `<section><h3>${title}</h3><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>`).join("")}<section><h3>Decision Path Summary</h3><p>${escapeHtml(snapshot.reasoning.decisionPathSummary)}</p></section></div>`;
}

function renderFeature(item: FeatureImportanceItem): string {
  return `<section class="ux-feature-row"><div><strong>${escapeHtml(item.feature)}</strong><span>${escapeHtml(item.impact)} impact - ${escapeHtml(item.direction)}</span></div><div class="ux-feature-bar"><span style="width: ${Math.round(item.weight * 100)}%"></span></div><strong>${Math.round(item.confidence * 100)}%</strong></section>`;
}

function renderSummaryCard(card: SummaryCard): string {
  return `<article class="ux-card ux-status-card"><span class="ux-status-pill">${escapeHtml(card.status)}</span><h3>${escapeHtml(card.title)}</h3><strong>${escapeHtml(card.value)}</strong><p>${escapeHtml(card.detail)}</p></article>`;
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true }).format(date).replace(" am", " AM").replace(" pm", " PM");
}

function toTitle(value: string): string {
  return value.replaceAll("-", " ").replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}
