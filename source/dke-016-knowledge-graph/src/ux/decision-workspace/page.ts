import type { DecisionWorkspaceSnapshot } from "./types.js";

export function renderDecisionWorkspace(snapshot: DecisionWorkspaceSnapshot): string {
  const { summary, context } = snapshot;
  const visibleTimeline = getVisibleTimeline(snapshot.timeline);
  return `
    <section class="ux-decision-workspace" aria-labelledby="decision-workspace-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-002</p>
          <h1 id="decision-workspace-title">${escapeHtml(summary.workspaceTitle)}</h1>
          <div class="ux-workspace-meta">
            <span>${escapeHtml(summary.decisionId)}</span>
            <span>${escapeHtml(summary.sessionId)}</span>
            <span>Updated ${escapeHtml(formatTimestamp(summary.updatedAt))}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(formatStatusLabel(summary.status))}</span>
      </header>

      <section class="ux-workspace-actions" aria-label="Decision workspace actions">
        <button type="button">New Decision</button>
        <button type="button">Load Decision</button>
        <button type="button">Run Evaluation</button>
        <button type="button">Run Ranking</button>
      </section>

      <section class="ux-workspace-grid">
        <article class="ux-panel ux-context-panel">
          <h2>Decision Context</h2>
          <dl class="ux-context-grid">
            <div><dt>Objective</dt><dd>${escapeHtml(context.objective)}</dd></div>
            <div><dt>Domain</dt><dd>${escapeHtml(context.domain)}</dd></div>
            <div><dt>Risk Preference</dt><dd>${escapeHtml(context.riskPreference)}</dd></div>
            <div><dt>Governance Mode</dt><dd>${escapeHtml(context.governanceMode)}</dd></div>
            <div><dt>Constraints</dt><dd>${renderList(context.constraints)}</dd></div>
            <div><dt>Stakeholders</dt><dd>${renderList(context.stakeholders)}</dd></div>
          </dl>
        </article>

        <article class="ux-panel">
          <h2>Alternatives</h2>
          <div class="ux-table-wrap">
            <table class="ux-table">
              <thead><tr><th>ID</th><th>Title</th><th>Expected Impact</th><th>Risk</th><th>Status</th></tr></thead>
              <tbody>
                ${snapshot.alternatives.map((item) => `
                  <tr>
                    <td>${escapeHtml(item.id)}</td>
                    <td><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.summary)}</span></td>
                    <td>${escapeHtml(item.expectedImpact)}</td>
                    <td>${escapeHtml(item.riskLevel)}</td>
                    <td>${escapeHtml(item.status)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </article>

        <article class="ux-panel">
          <h2>Evaluation Results</h2>
          <p class="ux-result-snapshot-label">Current backend/fallback result snapshot</p>
          <div class="ux-result-grid">
            ${snapshot.evaluationResults.map((result) => `
              <section class="ux-result-card">
                <header><strong>${escapeHtml(result.alternativeId)}</strong><span>${result.score} score</span><span>${Math.round(result.confidence * 100)}% confidence</span></header>
                <ul>${result.criteria.map((criterion) => `<li>${escapeHtml(criterion.name)}: ${criterion.score} (${Math.round(criterion.weight * 100)}% weight)</li>`).join("")}</ul>
                <p><strong>Strengths:</strong> ${escapeHtml(result.strengths.join(", "))}</p>
                <p><strong>Weaknesses:</strong> ${escapeHtml(result.weaknesses.join(", "))}</p>
                <p><strong>Warnings:</strong> ${escapeHtml(result.warnings.join(", "))}</p>
              </section>
            `).join("")}
          </div>
        </article>

        <article class="ux-panel">
          <h2>Ranking</h2>
          <p class="ux-result-snapshot-label">Current backend/fallback result snapshot</p>
          <div class="ux-ranking-list">
            ${snapshot.rankingResults.map((result) => `
              <section class="ux-ranking-row">
                <span class="ux-rank-number">${result.rank}</span>
                <div>
                  <h3>${escapeHtml(result.alternativeTitle)}</h3>
                  <p>${escapeHtml(result.explanationSummary)}</p>
                </div>
                <strong>${result.score}</strong>
                ${result.recommended ? `<span class="ux-status-pill">Recommended</span>` : ""}
              </section>
            `).join("")}
          </div>
        </article>

        <article class="ux-panel">
          <h2>Workspace Activity</h2>
          <ol class="ux-timeline">
            ${visibleTimeline.map((event) => `
              <li data-status="${escapeHtml(event.status)}">
                <div><strong>${escapeHtml(event.label)}</strong><span>${escapeHtml(formatTimestamp(event.timestamp))}</span></div>
                <span class="ux-activity-badge">${escapeHtml(formatStatusLabel(event.status))}</span>
              </li>
            `).join("")}
          </ol>
        </article>
      </section>
    </section>
  `;
}

function renderList(items: readonly string[]): string {
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(date).replace(" am", " AM").replace(" pm", " PM");
}

function getVisibleTimeline(timeline: readonly DecisionWorkspaceSnapshot["timeline"][number][]): readonly DecisionWorkspaceSnapshot["timeline"][number][] {
  return [...timeline]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function formatStatusLabel(value: string): string {
  return value
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
