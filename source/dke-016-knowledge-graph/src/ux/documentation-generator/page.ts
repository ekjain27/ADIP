import type { DocumentationGenerationSnapshot, GenerationActivity } from "./types.js";

export function renderDocumentationGenerationCenter(snapshot: DocumentationGenerationSnapshot): string {
  return `
    <section class="ux-docgen" aria-labelledby="docgen-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-005</p>
          <h1 id="docgen-title">Documentation / Patent / Research Generator</h1>
          <div class="ux-workspace-meta">
            <span>Generator Status ${escapeHtml(toTitle(snapshot.summary.generatorStatus))}</span>
            <span>${escapeHtml(snapshot.summary.currentProject)}</span>
            <span>Last Generation ${escapeHtml(formatTimestamp(snapshot.summary.lastGenerationAt))}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(toTitle(snapshot.summary.generatorStatus))}</span>
      </header>
      <section class="ux-workspace-actions"><button type="button">Generate Documentation</button><button type="button">Generate Patent</button><button type="button">Generate Research Paper</button><button type="button">Refresh</button><button type="button">Export Package</button></section>
      <section class="ux-workspace-grid">
        <article class="ux-panel ux-context-panel"><h2>Package Preview</h2><p>No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview.</p></article>
        <article class="ux-panel ux-context-panel"><h2>Generation Activity</h2><ol class="ux-timeline">${visibleActivity(snapshot.activity).map(renderActivity).join("")}</ol></article>
        <article class="ux-panel ux-boundary-panel"><h2>Backend Boundary</h2><p>Documentation, patent, and research package outputs are consumed through DocumentationGenerationClient. Backend generation logic remains frozen and authoritative.</p></article>
      </section>
    </section>
  `;
}

function renderActivity(event: GenerationActivity): string {
  return `<li data-status="complete"><div><strong>${escapeHtml(event.title)}</strong><span>${escapeHtml(formatTimestamp(event.timestamp))}</span><p>${escapeHtml(event.detail)}</p></div><span class="ux-activity-badge">${escapeHtml(toTitle(event.type))}</span></li>`;
}

function visibleActivity(activity: readonly GenerationActivity[]): readonly GenerationActivity[] {
  return [...activity].sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp)).slice(0, 8);
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
