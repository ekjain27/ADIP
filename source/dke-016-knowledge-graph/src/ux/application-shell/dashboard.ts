import type { BackendStatusClient, DashboardViewModel } from "./types.js";

export async function createDashboardViewModel(client: BackendStatusClient): Promise<DashboardViewModel> {
  const snapshot = await client.getPlatformStatus();
  return {
    title: "AI Decision Intelligence Platform",
    subtitle: "Enterprise dashboard shell for backend platform visibility.",
    statusCards: snapshot.platformStatus,
    mechanisms: snapshot.mechanisms,
    regressionBaseline: snapshot.regressionBaseline,
    releaseTags: snapshot.releaseTags,
  };
}

export function renderDashboard(viewModel: DashboardViewModel): string {
  const statusCards = viewModel.statusCards
    .map((card) => `<article class="ux-card ux-status-card" data-card-id="${escapeHtml(card.id)}"><span class="ux-status-pill">${escapeHtml(card.status)}</span><h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.detail)}</p></article>`)
    .join("");
  const mechanisms = viewModel.mechanisms
    .map((card) => `<article class="ux-card ux-mechanism-card" data-mechanism-id="${escapeHtml(card.id)}"><h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.description)}</p><small>${escapeHtml(card.backendModule)}</small></article>`)
    .join("");
  const tags = viewModel.releaseTags.map((tag) => `<li>${escapeHtml(tag)}</li>`).join("");

  return `
    <section class="ux-dashboard" aria-labelledby="dashboard-title">
      <header class="ux-page-header">
        <h1 id="dashboard-title">${escapeHtml(viewModel.title)}</h1>
        <p>${escapeHtml(viewModel.subtitle)}</p>
      </header>
      <section class="ux-baseline" aria-label="Regression baseline">
        <strong>${viewModel.regressionBaseline.passing} / ${viewModel.regressionBaseline.total}</strong>
        <span>Regression tests passing</span>
      </section>
      <section class="ux-grid ux-status-grid" aria-label="Platform status">${statusCards}</section>
      <section class="ux-release-tags" aria-label="Current release tags"><h2>Current Release Tags</h2><ul>${tags}</ul></section>
      <section class="ux-grid ux-mechanism-grid" aria-label="Frozen architecture mechanisms"><h2>Frozen Architecture Mechanisms</h2>${mechanisms}</section>
    </section>
  `;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
