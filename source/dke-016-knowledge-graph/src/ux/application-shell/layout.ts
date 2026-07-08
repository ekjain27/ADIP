import { createBackendStatusClient } from "./platformStatusClient.js";
import { resolveShellRoute } from "./routes.js";
import { toHashRoute, UX_ROADMAP_NAVIGATION } from "./navigation.js";
import type { BackendStatusClient, ShellRenderOptions } from "./types.js";

export async function renderEnterpriseDashboardShell(
  options: ShellRenderOptions = {},
  client: BackendStatusClient = createBackendStatusClient(),
): Promise<string> {
  const theme = options.theme ?? "light";
  const navigationMode = options.navigationMode ?? "path";
  const route = await resolveShellRoute(options.routePath, client);
  const navigation = UX_ROADMAP_NAVIGATION.map((entry) => {
    const current = entry.path === route.path ? "true" : "false";
    const href = navigationMode === "hash" ? toHashRoute(entry.path) : entry.path;
    return `<a class="ux-nav-link" href="${href}" aria-current="${current}" data-route-id="${entry.id}" data-route-path="${entry.path}">${entry.label}</a>`;
  }).join("");

  return `
    <div class="ux-shell" data-theme="${theme}">
      <aside class="ux-sidebar" aria-label="Primary navigation">
        <div class="ux-brand">Decision Intelligence</div>
        <nav>${navigation}</nav>
      </aside>
      <section class="ux-workspace">
        <header class="ux-topbar">
          <span class="ux-route-title">${route.title}</span>
          <span class="ux-boundary-label">Backend API Boundary</span>
        </header>
        <main class="ux-main">${route.contentHtml}</main>
      </section>
    </div>
  `;
}

export const ENTERPRISE_SHELL_CSS = `
  .ux-shell { min-height: 100vh; display: grid; grid-template-columns: 292px minmax(0, 1fr); background: var(--ux-bg); color: var(--ux-fg); }
  .ux-shell[data-theme="light"] { --ux-bg: #f4f6f8; --ux-fg: #18212f; --ux-panel: #ffffff; --ux-panel-strong: #f9fbfd; --ux-border: #d8dee8; --ux-muted: #657184; --ux-accent: #2454d6; --ux-accent-soft: #e8eefc; --ux-success: #14755a; --ux-warn: #8a5a00; --ux-shadow: 0 18px 42px rgba(24, 33, 47, 0.08); }
  .ux-shell[data-theme="dark"] { --ux-bg: #101419; --ux-fg: #f4f7fb; --ux-panel: #1a2028; --ux-panel-strong: #202833; --ux-border: #343f4d; --ux-muted: #a8b3c2; --ux-accent: #7aa2ff; --ux-accent-soft: rgba(122, 162, 255, 0.16); --ux-success: #5fd0a8; --ux-warn: #f0c15f; --ux-shadow: 0 18px 42px rgba(0, 0, 0, 0.32); }
  .ux-sidebar { border-right: 1px solid var(--ux-border); padding: 22px 18px; background: var(--ux-panel); box-shadow: 10px 0 30px rgba(24, 33, 47, 0.04); }
  .ux-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 28px; padding: 8px 6px 18px; border-bottom: 1px solid var(--ux-border); }
  .ux-brand strong { display: block; font-size: 15px; line-height: 1.2; }
  .ux-brand small { display: block; margin-top: 3px; color: var(--ux-muted); font-size: 12px; }
  .ux-brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 38px; height: 38px; border-radius: 8px; background: var(--ux-accent); color: #ffffff; font-weight: 800; letter-spacing: 0; }
  .ux-nav-link { display: block; width: 100%; margin: 2px 0; padding: 11px 12px; color: var(--ux-muted); text-align: left; text-decoration: none; border: 1px solid transparent; border-radius: 8px; background: transparent; cursor: pointer; transition: background 120ms ease, border-color 120ms ease, color 120ms ease; }
  .ux-nav-link:hover { background: var(--ux-panel-strong); color: var(--ux-fg); border-color: var(--ux-border); }
  .ux-nav-link[aria-current="true"] { background: var(--ux-accent-soft); border-color: color-mix(in srgb, var(--ux-accent) 38%, transparent); color: var(--ux-fg); font-weight: 700; box-shadow: inset 3px 0 0 var(--ux-accent); }
  .ux-workspace { min-width: 0; display: flex; flex-direction: column; }
  .ux-topbar { min-height: 72px; display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 14px 32px; border-bottom: 1px solid var(--ux-border); background: color-mix(in srgb, var(--ux-panel) 92%, transparent); backdrop-filter: blur(10px); }
  .ux-route-title { display: block; font-size: 18px; font-weight: 800; }
  .ux-route-subtitle { display: block; margin-top: 3px; color: var(--ux-muted); font-size: 12px; text-transform: uppercase; }
  .ux-boundary-label { flex: 0 0 auto; border: 1px solid var(--ux-border); border-radius: 999px; padding: 7px 11px; color: var(--ux-muted); background: var(--ux-panel-strong); font-size: 12px; font-weight: 700; text-transform: uppercase; }
  .ux-main { padding: 32px; }
  .ux-dashboard { max-width: 1240px; margin: 0 auto; }
  .ux-page-header { display: flex; justify-content: space-between; gap: 24px; margin-bottom: 22px; }
  .ux-page-header h1 { margin: 0; font-size: 30px; line-height: 1.15; }
  .ux-page-header p { margin: 8px 0 0; color: var(--ux-muted); max-width: 680px; }
  .ux-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 18px; }
  .ux-card, .ux-baseline, .ux-release-tags { background: var(--ux-panel); border: 1px solid var(--ux-border); border-radius: 8px; padding: 20px; box-shadow: var(--ux-shadow); }
  .ux-card h3 { margin: 9px 0 8px; font-size: 16px; line-height: 1.25; }
  .ux-card p { margin: 0; color: var(--ux-muted); line-height: 1.5; }
  .ux-status-card { min-height: 150px; border-top: 3px solid var(--ux-success); }
  .ux-status-pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 8px; background: color-mix(in srgb, var(--ux-success) 14%, transparent); color: var(--ux-success); text-transform: uppercase; font-size: 11px; font-weight: 800; }
  .ux-baseline { margin: 20px 0; display: flex; gap: 14px; align-items: baseline; border-left: 4px solid var(--ux-accent); }
  .ux-baseline strong { font-size: 28px; line-height: 1; color: var(--ux-accent); }
  .ux-baseline span { color: var(--ux-muted); font-weight: 700; }
  .ux-release-tags { margin: 20px 0; }
  .ux-release-tags h2, .ux-mechanism-grid h2 { margin: 0 0 14px; font-size: 18px; }
  .ux-release-tags ul { display: flex; flex-wrap: wrap; gap: 10px; padding: 0; margin: 0; list-style: none; }
  .ux-release-tags li { border: 1px solid var(--ux-border); border-radius: 999px; padding: 7px 10px; color: var(--ux-muted); background: var(--ux-panel-strong); font-size: 13px; font-weight: 700; }
  .ux-mechanism-grid { margin-top: 20px; }
  .ux-mechanism-grid h2 { grid-column: 1 / -1; }
  .ux-mechanism-card { min-height: 168px; border-top: 3px solid var(--ux-warn); }
  .ux-mechanism-card small { display: inline-block; margin-top: 14px; color: var(--ux-muted); font-weight: 800; text-transform: uppercase; font-size: 11px; }
  .ux-decision-workspace { max-width: 1320px; margin: 0 auto; }
  .ux-workspace-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 16px; background: var(--ux-panel); border: 1px solid var(--ux-border); border-radius: 8px; padding: 24px; box-shadow: var(--ux-shadow); }
  .ux-workspace-header h1 { margin: 0; font-size: 30px; line-height: 1.15; }
  .ux-workspace-meta { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 12px; color: var(--ux-muted); font-size: 13px; font-weight: 700; }
  .ux-workspace-meta span { border: 1px solid var(--ux-border); border-radius: 999px; padding: 6px 9px; background: var(--ux-panel-strong); }
  .ux-workspace-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
  .ux-workspace-actions button { border: 1px solid var(--ux-border); border-radius: 8px; background: var(--ux-panel); color: var(--ux-fg); padding: 10px 13px; cursor: pointer; font-weight: 800; box-shadow: 0 8px 18px rgba(24, 33, 47, 0.06); }
  .ux-workspace-actions button:hover { border-color: var(--ux-accent); background: var(--ux-accent-soft); }
  .ux-workspace-actions button:nth-last-child(-n + 2) { background: var(--ux-accent); border-color: var(--ux-accent); color: #ffffff; }
  .ux-workspace-actions button:disabled { cursor: progress; opacity: 0.72; box-shadow: none; }
  .ux-action-status { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
  .ux-action-status span { border: 1px solid var(--ux-border); border-radius: 999px; padding: 8px 11px; background: var(--ux-panel); color: var(--ux-muted); font-size: 13px; font-weight: 800; box-shadow: 0 8px 18px rgba(24, 33, 47, 0.05); }
  .ux-action-status [data-status-id="last-action"] { border-color: color-mix(in srgb, var(--ux-accent) 28%, var(--ux-border)); background: var(--ux-accent-soft); color: var(--ux-fg); }
  .ux-workspace-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 18px; }
  .ux-panel { grid-column: span 6; background: var(--ux-panel); border: 1px solid var(--ux-border); border-radius: 8px; padding: 20px; box-shadow: var(--ux-shadow); }
  .ux-panel h2 { margin: 0 0 14px; font-size: 18px; line-height: 1.2; }
  .ux-context-panel, .ux-panel:has(.ux-table-wrap), .ux-panel:has(.ux-result-grid), .ux-panel:has(.ux-ranking-list) { grid-column: 1 / -1; }
  .ux-context-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin: 0; }
  .ux-context-grid div { border: 1px solid var(--ux-border); border-radius: 8px; padding: 14px; background: var(--ux-panel-strong); }
  .ux-context-grid dt { margin-bottom: 6px; color: var(--ux-muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }
  .ux-context-grid dd { margin: 0; line-height: 1.5; }
  .ux-context-grid ul, .ux-result-card ul { margin: 0; padding-left: 18px; }
  .ux-session-list { display: grid; gap: 10px; }
  .ux-session-row { display: grid; grid-template-columns: minmax(160px, 1fr) auto auto auto; gap: 10px; align-items: center; border: 1px solid var(--ux-border); border-radius: 8px; padding: 12px; background: var(--ux-panel-strong); color: var(--ux-muted); font-size: 13px; }
  .ux-session-row strong { color: var(--ux-fg); }
  .ux-table-wrap { overflow-x: auto; border: 1px solid var(--ux-border); border-radius: 8px; }
  .ux-table { width: 100%; min-width: 860px; border-collapse: collapse; }
  .ux-table th, .ux-table td { padding: 13px 14px; border-bottom: 1px solid var(--ux-border); text-align: left; vertical-align: top; }
  .ux-table th { color: var(--ux-muted); background: var(--ux-panel-strong); font-size: 12px; text-transform: uppercase; }
  .ux-table tr.ux-selected-row td { background: var(--ux-accent-soft); box-shadow: inset 3px 0 0 var(--ux-accent); }
  .ux-table tr.ux-refreshed-row td { background: color-mix(in srgb, var(--ux-success) 10%, transparent); box-shadow: inset 3px 0 0 var(--ux-success); }
  .ux-table td span { display: block; margin-top: 4px; color: var(--ux-muted); line-height: 1.45; }
  .ux-result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 14px; }
  .ux-result-snapshot-label { display: inline-flex; margin: -4px 0 14px; border-radius: 999px; padding: 6px 9px; background: var(--ux-panel-strong); color: var(--ux-muted); font-size: 12px; font-weight: 800; }
  .ux-result-card { border: 1px solid var(--ux-border); border-radius: 8px; padding: 16px; background: var(--ux-panel-strong); }
  .ux-result-card header { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }
  .ux-result-card header span { border-radius: 999px; padding: 5px 8px; background: var(--ux-accent-soft); color: var(--ux-fg); font-size: 12px; font-weight: 800; }
  .ux-result-card p { margin: 10px 0 0; color: var(--ux-muted); line-height: 1.45; }
  .ux-ranking-list, .ux-timeline { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
  .ux-ranking-row { display: grid; grid-template-columns: 42px minmax(0, 1fr) auto auto; gap: 14px; align-items: center; border: 1px solid var(--ux-border); border-radius: 8px; padding: 14px; background: var(--ux-panel-strong); }
  .ux-ranking-row h3 { margin: 0; font-size: 15px; }
  .ux-ranking-row p { margin: 4px 0 0; color: var(--ux-muted); line-height: 1.45; }
  .ux-rank-number { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 999px; background: var(--ux-accent); color: #ffffff; font-weight: 900; }
  .ux-timeline li { display: flex; justify-content: space-between; align-items: center; gap: 12px; border-left: 4px solid var(--ux-border); border-radius: 8px; padding: 12px 14px; background: var(--ux-panel-strong); }
  .ux-timeline li[data-status="complete"] { border-left-color: var(--ux-success); }
  .ux-timeline li[data-status="current"] { border-left-color: var(--ux-accent); }
  .ux-timeline div span { display: block; margin-top: 4px; color: var(--ux-muted); }
  .ux-activity-badge { flex: 0 0 auto; border-radius: 999px; padding: 5px 8px; background: var(--ux-accent-soft); color: var(--ux-fg); font-size: 11px; font-weight: 900; text-transform: uppercase; }
  .ux-boundary-panel { grid-column: 1 / -1; border-left: 4px solid var(--ux-accent); }
  .ux-boundary-panel p { margin: 0; color: var(--ux-muted); line-height: 1.5; }
  .ux-kg { max-width: 1320px; margin: 0 auto; }
  .ux-kg-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 18px; }
  .ux-kg-graph-panel, .ux-kg-timeline-panel { grid-column: 1 / -1; }
  .ux-graph-canvas { overflow-x: auto; border: 1px solid var(--ux-border); border-radius: 8px; background: var(--ux-panel-strong); padding: 16px; }
  .ux-graph-canvas svg { width: 100%; min-width: 760px; height: 260px; }
  .ux-graph-edge { stroke: var(--ux-muted); stroke-width: 2; cursor: pointer; }
  .ux-graph-edge.is-provenance-path { stroke: var(--ux-success); stroke-width: 5; }
  .ux-graph-edge.is-selected { stroke: var(--ux-accent); stroke-width: 4; }
  .ux-graph-edge-label, .ux-graph-node-label { fill: var(--ux-muted); font-size: 12px; font-weight: 800; cursor: pointer; }
  .ux-graph-node { fill: var(--ux-panel); stroke: var(--ux-accent); stroke-width: 3; cursor: pointer; }
  .ux-graph-node.is-provenance-path { fill: rgba(22, 163, 74, 0.16); stroke: var(--ux-success); stroke-width: 5; }
  .ux-graph-node.is-selected { fill: var(--ux-accent-soft); stroke-width: 5; }
  .ux-filter-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
  .ux-filter-grid label { display: grid; gap: 6px; color: var(--ux-muted); font-size: 12px; font-weight: 900; text-transform: uppercase; }
  .ux-filter-grid select, .ux-filter-grid span { border: 1px solid var(--ux-border); border-radius: 8px; background: var(--ux-panel-strong); color: var(--ux-fg); padding: 9px 10px; font: inherit; text-transform: none; }
  .ux-inspector-list { display: grid; gap: 10px; margin: 0; }
  .ux-inspector-list div { display: grid; grid-template-columns: 140px minmax(0, 1fr); gap: 10px; border-bottom: 1px solid var(--ux-border); padding-bottom: 9px; }
  .ux-inspector-list dt { color: var(--ux-muted); font-size: 12px; font-weight: 900; text-transform: uppercase; }
  .ux-inspector-list dd { margin: 0; overflow-wrap: anywhere; }
  .ux-timeline p { margin: 6px 0 0; color: var(--ux-muted); line-height: 1.45; }
  .ux-xai { max-width: 1320px; margin: 0 auto; }
  .ux-xai-summary { margin-bottom: 18px; }
  .ux-xai-summary .ux-card strong, .ux-analytics-grid .ux-card strong { display: block; margin: 8px 0; color: var(--ux-accent); font-size: 24px; line-height: 1; }
  .ux-reasoning-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; }
  .ux-reasoning-grid section { border: 1px solid var(--ux-border); border-radius: 8px; padding: 14px; background: var(--ux-panel-strong); }
  .ux-reasoning-grid h3, .ux-analytics-grid h3 { margin: 0 0 10px; font-size: 15px; }
  .ux-reasoning-grid ul { margin: 0; padding-left: 18px; color: var(--ux-muted); line-height: 1.55; }
  .ux-reasoning-grid p { margin: 0; color: var(--ux-muted); line-height: 1.55; }
  .ux-feature-list { display: grid; gap: 12px; }
  .ux-feature-row { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(180px, 2fr) auto; gap: 14px; align-items: center; border: 1px solid var(--ux-border); border-radius: 8px; padding: 14px; background: var(--ux-panel-strong); }
  .ux-feature-row span { display: block; margin-top: 4px; color: var(--ux-muted); }
  .ux-feature-bar { height: 12px; overflow: hidden; border-radius: 999px; background: color-mix(in srgb, var(--ux-muted) 18%, transparent); }
  .ux-feature-bar span { height: 100%; margin: 0; background: var(--ux-accent); }
  .ux-analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 14px; }
  .ux-analytics-grid section { border: 1px solid var(--ux-border); border-radius: 8px; padding: 14px; background: var(--ux-panel-strong); }
  .ux-placeholder { max-width: 820px; margin: 0 auto; background: var(--ux-panel); border: 1px solid var(--ux-border); border-radius: 8px; padding: 34px; box-shadow: var(--ux-shadow); }
  .ux-placeholder h1 { margin: 0 0 12px; font-size: 28px; }
  .ux-module-label { margin: 0 0 10px; color: var(--ux-accent); font-size: 12px; font-weight: 800; text-transform: uppercase; }
  .ux-placeholder-purpose { font-size: 18px; color: var(--ux-muted); line-height: 1.55; }
  .ux-placeholder-message { display: inline-flex; margin-top: 8px; border-radius: 999px; padding: 8px 11px; background: var(--ux-accent-soft); color: var(--ux-fg); font-weight: 800; }
  .ux-boundary-note { border-top: 1px solid var(--ux-border); margin-top: 22px; padding-top: 16px; color: var(--ux-muted); line-height: 1.5; }
  @media (max-width: 900px) { .ux-shell { grid-template-columns: 1fr; } .ux-sidebar { border-right: 0; border-bottom: 1px solid var(--ux-border); } .ux-sidebar nav { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 6px; } .ux-main { padding: 22px; } .ux-panel { grid-column: 1 / -1; } .ux-session-row, .ux-ranking-row, .ux-inspector-list div, .ux-feature-row { grid-template-columns: 1fr; align-items: start; } }
  @media (max-width: 640px) { .ux-topbar { align-items: flex-start; flex-direction: column; padding: 16px 20px; } .ux-main { padding: 18px; } .ux-page-header h1, .ux-workspace-header h1 { font-size: 24px; } .ux-workspace-header { flex-direction: column; padding: 20px; } .ux-baseline { flex-direction: column; gap: 6px; } .ux-release-tags ul { display: grid; } }
`;
