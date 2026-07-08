import type { ApiEndpointOverview, EnterpriseIntegrationSnapshot, IntegrationActivity, IntegrationConnector, WebhookConfiguration } from "./types.js";

export function renderEnterprisePlatformIntegrationConsole(snapshot: EnterpriseIntegrationSnapshot): string {
  return `
    <section class="ux-integration" aria-labelledby="integration-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-007</p>
          <h1 id="integration-title">Enterprise Platform Integration Console</h1>
          <div class="ux-workspace-meta">
            <span>Integration Status ${escapeHtml(toTitle(snapshot.summary.integrationStatus))}</span>
            <span>${escapeHtml(snapshot.summary.activeEnvironment)}</span>
            <span>Last Sync ${escapeHtml(formatTimestamp(snapshot.summary.lastSyncAt))}</span>
            <span>${escapeHtml(snapshot.summary.releaseVersion)}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(toTitle(snapshot.summary.integrationStatus))}</span>
      </header>
      <section class="ux-workspace-actions"><button type="button">Sync Integrations</button><button type="button">Test Connections</button><button type="button">Export Config</button></section>
      <section class="ux-workspace-grid">
        <article class="ux-panel ux-context-panel"><h2>Connector Management</h2><div class="ux-table-wrap"><table class="ux-table"><thead><tr><th>Connector</th><th>Status</th><th>Endpoint</th><th>Auth</th><th>Latency</th><th>Last Checked</th><th>Actions</th></tr></thead><tbody>${snapshot.connectors.map(renderConnector).join("")}</tbody></table></div></article>
        <article class="ux-panel ux-context-panel"><h2>API Endpoint Overview</h2><section class="ux-workspace-actions"><button type="button">Refresh Endpoints</button><button type="button">Export API Map</button></section><div class="ux-table-wrap"><table class="ux-table"><thead><tr><th>Name</th><th>Method</th><th>Path</th><th>Service</th><th>Status</th><th>Version</th></tr></thead><tbody>${snapshot.apiEndpoints.map(renderEndpoint).join("")}</tbody></table></div></article>
        <article class="ux-panel ux-context-panel"><h2>Webhook Configuration</h2><section class="ux-workspace-actions"><button type="button">Add Webhook</button></section><div class="ux-table-wrap"><table class="ux-table"><thead><tr><th>Webhook</th><th>Event</th><th>Target</th><th>Status</th><th>Retry</th><th>Last Delivery</th><th>Actions</th></tr></thead><tbody>${snapshot.webhooks.map(renderWebhook).join("")}</tbody></table></div></article>
        <article class="ux-panel"><h2>Deployment & Environment</h2><dl class="ux-inspector-list"><dt>Environment</dt><dd>${escapeHtml(snapshot.deployment.environment)}</dd><dt>Release Tag</dt><dd>${escapeHtml(snapshot.deployment.releaseTag)}</dd><dt>Runtime</dt><dd>${escapeHtml(snapshot.deployment.runtime)}</dd><dt>Build Status</dt><dd>${escapeHtml(snapshot.deployment.buildStatus)}</dd><dt>Monitoring Mode</dt><dd>${escapeHtml(snapshot.deployment.monitoringMode)}</dd><dt>Regression Baseline</dt><dd>${escapeHtml(snapshot.deployment.regressionBaseline)}</dd><dt>Commercial Readiness</dt><dd>${escapeHtml(snapshot.deployment.commercialReadiness)}</dd></dl></article>
        <article class="ux-panel ux-context-panel"><h2>Integration Activity Log</h2><ol class="ux-timeline">${visibleActivity(snapshot.activity).map(renderActivity).join("")}</ol></article>
        <article class="ux-panel ux-boundary-panel"><h2>Backend Boundary</h2><p>Enterprise integration status, connectors, API endpoints, webhooks, deployment, and activity are consumed through EnterpriseIntegrationClient. Real integration logic remains outside the UI.</p></article>
      </section>
    </section>
  `;
}

function renderConnector(connector: IntegrationConnector): string {
  return `<tr><td><strong>${escapeHtml(connector.name)}</strong><span>${escapeHtml(connector.detail)}</span></td><td>${escapeHtml(toTitle(connector.status))}</td><td>${escapeHtml(connector.endpoint)}</td><td>${escapeHtml(connector.authMode)}</td><td>${connector.latencyMs} ms</td><td>${escapeHtml(formatTimestamp(connector.lastCheckedAt))}</td><td><button type="button">Test</button><button type="button">Enable/Disable</button><button type="button">View Details</button></td></tr>`;
}

function renderEndpoint(endpoint: ApiEndpointOverview): string {
  return `<tr><td>${escapeHtml(endpoint.name)}</td><td>${escapeHtml(endpoint.method)}</td><td>${escapeHtml(endpoint.path)}</td><td>${escapeHtml(endpoint.service)}</td><td>${escapeHtml(toTitle(endpoint.status))}</td><td>${escapeHtml(endpoint.version)}</td></tr>`;
}

function renderWebhook(webhook: WebhookConfiguration): string {
  return `<tr><td>${escapeHtml(webhook.id)}</td><td>${escapeHtml(webhook.eventType)}</td><td>${escapeHtml(webhook.targetUrl)}</td><td>${escapeHtml(toTitle(webhook.status))}</td><td>${escapeHtml(webhook.retryPolicy)}</td><td>${escapeHtml(formatTimestamp(webhook.lastDeliveryAt))}</td><td><button type="button">Test Webhook</button><button type="button">Enable/Disable</button></td></tr>`;
}

function renderActivity(event: IntegrationActivity): string {
  return `<li data-status="${escapeHtml(event.severity)}"><div><strong>${escapeHtml(event.action)}</strong><span>${escapeHtml(formatTimestamp(event.timestamp))}</span><p>${escapeHtml(event.connector)} - ${escapeHtml(event.result)}</p></div><span class="ux-activity-badge">${escapeHtml(toTitle(event.severity))}</span></li>`;
}

function visibleActivity(activity: readonly IntegrationActivity[]): readonly IntegrationActivity[] {
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
