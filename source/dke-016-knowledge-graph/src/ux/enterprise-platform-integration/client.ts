import type { ApiEndpointOverview, DeploymentEnvironment, EnterpriseIntegrationClient, EnterpriseIntegrationSnapshot, IntegrationActivity, IntegrationConnector, IntegrationSummary, WebhookConfiguration } from "./types.js";

const initialTimestamp = new Date().toISOString();
export const ENTERPRISE_INTEGRATION_STORAGE_KEY = "project1.ux007.integration.snapshot.v1";

function minutesBefore(timestamp: string, minutes: number): string {
  return new Date(Date.parse(timestamp) - minutes * 60 * 1000).toISOString();
}

const baseSummary: IntegrationSummary = {
  integrationStatus: "ready",
  activeEnvironment: "Production Preview",
  lastSyncAt: initialTimestamp,
  releaseVersion: "v1.0.2-backend-complete",
};

const baseConnectors: readonly IntegrationConnector[] = [
  { id: "CONN-BACKEND-API", name: "Backend API", status: "healthy", endpoint: "/api/platform/status", authMode: "Service token", latencyMs: 42, lastCheckedAt: minutesBefore(initialTimestamp, 4), detail: "Backend platform boundary adapter" },
  { id: "CONN-KG", name: "Knowledge Graph Service", status: "healthy", endpoint: "/api/knowledge-graph", authMode: "Service token", latencyMs: 57, lastCheckedAt: minutesBefore(initialTimestamp, 9), detail: "Graph and provenance API surface" },
  { id: "CONN-DIE", name: "Decision Engine", status: "healthy", endpoint: "/api/decision-engine", authMode: "Mutual TLS", latencyMs: 64, lastCheckedAt: minutesBefore(initialTimestamp, 13), detail: "Decision evaluation and ranking backend" },
  { id: "CONN-XAI", name: "Explainability Service", status: "enabled", endpoint: "/api/explainability", authMode: "Service token", latencyMs: 51, lastCheckedAt: minutesBefore(initialTimestamp, 18), detail: "Explainability analytics outputs" },
  { id: "CONN-DOC", name: "Documentation Service", status: "enabled", endpoint: "/api/documentation", authMode: "Signed request", latencyMs: 73, lastCheckedAt: minutesBefore(initialTimestamp, 22), detail: "Documentation, patent, and research generation API" },
  { id: "CONN-GOV", name: "Governance Service", status: "healthy", endpoint: "/api/governance", authMode: "Policy token", latencyMs: 49, lastCheckedAt: minutesBefore(initialTimestamp, 27), detail: "Governance controls and approval state" },
  { id: "CONN-MON", name: "Monitoring Service", status: "healthy", endpoint: "/api/monitoring", authMode: "Read-only token", latencyMs: 38, lastCheckedAt: minutesBefore(initialTimestamp, 31), detail: "Decision health and telemetry surface" },
  { id: "CONN-WEBHOOK", name: "External Webhook", status: "disabled", endpoint: "https://integrations.example.com/decision-events", authMode: "HMAC", latencyMs: 0, lastCheckedAt: minutesBefore(initialTimestamp, 52), detail: "Outbound event delivery integration" },
];

const deterministicLatency: Record<string, number> = {
  "CONN-BACKEND-API": 0,
  "CONN-KG": 115,
  "CONN-DIE": 122,
  "CONN-XAI": 108,
  "CONN-DOC": 98,
  "CONN-GOV": 112,
  "CONN-MON": 84,
  "CONN-WEBHOOK": 0,
};

function getConnectorTestDetails(connector: IntegrationConnector, disabled: boolean): Pick<IntegrationConnector, "authenticationResult" | "endpointValidation" | "adapterHandshake" | "testResult"> {
  if (disabled) {
    return {
      authenticationResult: "Not executed while connector is disabled.",
      endpointValidation: "Endpoint validation skipped until connector is enabled.",
      adapterHandshake: "Adapter handshake not attempted.",
      testResult: "Connector disabled. Enable before testing.",
    };
  }
  return {
    authenticationResult: `${connector.authMode} accepted by local adapter contract.`,
    endpointValidation: `${connector.endpoint} validated against configured UX-007 endpoint map.`,
    adapterHandshake: `${connector.name} adapter handshake completed.`,
    testResult: `${connector.name} connection test passed against local adapter configuration.`,
  };
}

const baseApiEndpoints: readonly ApiEndpointOverview[] = [
  { id: "API-STATUS", name: "Platform Status", method: "GET", path: "/api/platform/status", service: "Backend API", status: "available", version: "v1" },
  { id: "API-SESSIONS", name: "Decision Sessions", method: "GET", path: "/api/decisions/sessions", service: "Decision Engine", status: "available", version: "v1" },
  { id: "API-EVALUATE", name: "Run Evaluation", method: "POST", path: "/api/decisions/evaluate", service: "Decision Engine", status: "available", version: "v1" },
  { id: "API-RANK", name: "Run Ranking", method: "POST", path: "/api/decisions/rank", service: "Decision Engine", status: "available", version: "v1" },
  { id: "API-GRAPH", name: "Graph Data", method: "GET", path: "/api/knowledge-graph/data", service: "Knowledge Graph Service", status: "available", version: "v1" },
  { id: "API-XAI", name: "Generate Explanation", method: "POST", path: "/api/explainability/generate", service: "Explainability Service", status: "available", version: "v1" },
  { id: "API-DOCS", name: "Generate Documentation", method: "POST", path: "/api/documentation/generate", service: "Documentation Service", status: "available", version: "v1" },
  { id: "API-AUDIT", name: "Audit Log", method: "GET", path: "/api/admin/audit", service: "Governance Service", status: "available", version: "v1" },
];

const baseWebhooks: readonly WebhookConfiguration[] = [
  { id: "WH-DECISION-COMPLETE", eventType: "decision.completed", targetUrl: "https://integrations.example.com/decision-complete", status: "enabled", retryPolicy: "3 retries / 15 minutes", lastDeliveryAt: minutesBefore(initialTimestamp, 35) },
  { id: "WH-GOVERNANCE-REVIEW", eventType: "governance.review_requested", targetUrl: "https://integrations.example.com/governance-review", status: "enabled", retryPolicy: "5 retries / 30 minutes", lastDeliveryAt: minutesBefore(initialTimestamp, 64) },
];

const baseDeployment: DeploymentEnvironment = {
  environment: "Production Preview",
  releaseTag: "v1.0.2-backend-complete",
  runtime: "Vite React preview shell",
  buildStatus: "Passing",
  monitoringMode: "Decision health monitoring",
  regressionBaseline: "606 / 606 tests passing",
  commercialReadiness: "Backend complete, UX integration layer active",
};

const baseActivity: readonly IntegrationActivity[] = [
  { id: "INT-ACT-001", timestamp: minutesBefore(initialTimestamp, 7), action: "Integration status loaded", connector: "Platform Integration", result: "Ready", severity: "info" },
  { id: "INT-ACT-002", timestamp: minutesBefore(initialTimestamp, 28), action: "Connector health checked", connector: "Backend API", result: "Healthy", severity: "info" },
  { id: "INT-ACT-003", timestamp: minutesBefore(initialTimestamp, 49), action: "Webhook delivery reviewed", connector: "External Webhook", result: "Configured", severity: "info" },
];

function getBrowserStorage(): Storage | null {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

function isIntegrationSummary(value: unknown): value is IntegrationSummary {
  if (!value || typeof value !== "object") return false;
  const summary = value as Partial<IntegrationSummary>;
  return typeof summary.integrationStatus === "string"
    && typeof summary.activeEnvironment === "string"
    && typeof summary.lastSyncAt === "string"
    && typeof summary.releaseVersion === "string";
}

function isIntegrationConnector(value: unknown): value is IntegrationConnector {
  if (!value || typeof value !== "object") return false;
  const connector = value as Partial<IntegrationConnector>;
  return typeof connector.id === "string"
    && typeof connector.name === "string"
    && typeof connector.status === "string"
    && typeof connector.endpoint === "string"
    && typeof connector.authMode === "string"
    && typeof connector.latencyMs === "number"
    && typeof connector.lastCheckedAt === "string"
    && typeof connector.detail === "string";
}

function isWebhookConfiguration(value: unknown): value is WebhookConfiguration {
  if (!value || typeof value !== "object") return false;
  const webhook = value as Partial<WebhookConfiguration>;
  return typeof webhook.id === "string"
    && typeof webhook.eventType === "string"
    && typeof webhook.targetUrl === "string"
    && typeof webhook.status === "string"
    && typeof webhook.retryPolicy === "string"
    && typeof webhook.lastDeliveryAt === "string";
}

function isIntegrationActivity(value: unknown): value is IntegrationActivity {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<IntegrationActivity>;
  return typeof item.id === "string"
    && typeof item.timestamp === "string"
    && typeof item.action === "string"
    && typeof item.connector === "string"
    && typeof item.result === "string"
    && typeof item.severity === "string";
}

function loadStoredSnapshot(): Pick<EnterpriseIntegrationSnapshot, "summary" | "connectors" | "apiEndpoints" | "webhooks" | "activity"> | null {
  const storage = getBrowserStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(ENTERPRISE_INTEGRATION_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<EnterpriseIntegrationSnapshot>;
    if (!isIntegrationSummary(parsed.summary)) return null;
    if (!Array.isArray(parsed.connectors) || !parsed.connectors.every(isIntegrationConnector)) return null;
    if (!Array.isArray(parsed.apiEndpoints)) return null;
    if (!Array.isArray(parsed.webhooks) || !parsed.webhooks.every(isWebhookConfiguration)) return null;
    if (!Array.isArray(parsed.activity) || !parsed.activity.every(isIntegrationActivity)) return null;
    return {
      summary: parsed.summary,
      connectors: parsed.connectors,
      apiEndpoints: parsed.apiEndpoints as readonly ApiEndpointOverview[],
      webhooks: parsed.webhooks,
      activity: parsed.activity,
    };
  } catch {
    return null;
  }
}

function saveStoredSnapshot(snapshot: EnterpriseIntegrationSnapshot): void {
  const storage = getBrowserStorage();
  if (!storage) return;
  try {
    storage.setItem(ENTERPRISE_INTEGRATION_STORAGE_KEY, JSON.stringify({
      summary: snapshot.summary,
      connectors: snapshot.connectors,
      apiEndpoints: snapshot.apiEndpoints,
      webhooks: snapshot.webhooks,
      activity: snapshot.activity,
    }));
  } catch {
    // Persistence is for the UX preview only. Storage failures should not break integration UI actions.
  }
}

function getNextWebhookIndex(webhooks: readonly WebhookConfiguration[]): number {
  return webhooks.reduce((max, webhook) => {
    const match = /^WH-UX-007-(\d+)$/.exec(webhook.id);
    return match ? Math.max(max, Number.parseInt(match[1], 10)) : max;
  }, 0) + 1;
}

function activity(id: string, action: string, connector: string, result: string, severity: IntegrationActivity["severity"] = "info"): IntegrationActivity {
  return { id, timestamp: new Date().toISOString(), action, connector, result, severity };
}

function withActivity(event: IntegrationActivity, events: readonly IntegrationActivity[]): readonly IntegrationActivity[] {
  return [event, ...events.filter((item) => item.id !== event.id)].slice(0, 8);
}

export class DeterministicEnterpriseIntegrationClient implements EnterpriseIntegrationClient {
  private summary = baseSummary;
  private connectors = baseConnectors;
  private apiEndpoints = baseApiEndpoints;
  private webhooks = baseWebhooks;
  private integrationActivity = baseActivity;
  private nextWebhookIndex = 1;

  constructor() {
    const stored = loadStoredSnapshot();
    if (!stored) return;
    this.summary = stored.summary;
    this.connectors = stored.connectors;
    this.apiEndpoints = stored.apiEndpoints;
    this.webhooks = stored.webhooks;
    this.integrationActivity = stored.activity;
    this.nextWebhookIndex = getNextWebhookIndex(stored.webhooks);
  }

  async getIntegrationSummary(): Promise<IntegrationSummary> { return this.summary; }
  async listConnectors(): Promise<readonly IntegrationConnector[]> { return this.connectors; }
  async listApiEndpoints(): Promise<readonly ApiEndpointOverview[]> { return this.apiEndpoints; }
  async listWebhooks(): Promise<readonly WebhookConfiguration[]> { return this.webhooks; }
  async getDeploymentEnvironment(): Promise<DeploymentEnvironment> { return baseDeployment; }
  async listIntegrationActivity(): Promise<readonly IntegrationActivity[]> { return this.integrationActivity; }

  private snapshot(status: IntegrationSummary["integrationStatus"], event: IntegrationActivity): EnterpriseIntegrationSnapshot {
    this.summary = { ...this.summary, integrationStatus: status, lastSyncAt: event.timestamp };
    this.integrationActivity = withActivity(event, this.integrationActivity);
    const next = { summary: this.summary, connectors: this.connectors, apiEndpoints: this.apiEndpoints, webhooks: this.webhooks, deployment: baseDeployment, activity: this.integrationActivity };
    saveStoredSnapshot(next);
    return next;
  }

  async syncIntegrations(): Promise<EnterpriseIntegrationSnapshot> {
    return this.snapshot("synced", activity("INT-ACT-SYNC", "Integrations synced", "Platform Integration", "Sync complete"));
  }

  async testConnections(): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    this.connectors = this.connectors.map((connector) => {
      const disabled = connector.status === "disabled" || connector.id === "CONN-BACKEND-API" || connector.id === "CONN-WEBHOOK";
      const testDetails = getConnectorTestDetails(connector, disabled);
      return {
        ...connector,
        status: disabled ? "disabled" : "healthy",
        latencyMs: disabled ? 0 : deterministicLatency[connector.id] ?? connector.latencyMs,
        lastCheckedAt: timestamp,
        testStatus: disabled ? "disabled" : "passed",
        ...testDetails,
      };
    });
    return this.snapshot("connections-tested", activity("INT-ACT-TEST-CONNECTIONS", "Connections tested", "All connectors", "Connection checks complete"));
  }

  async exportConfig(): Promise<EnterpriseIntegrationSnapshot> {
    return this.snapshot("config-exported", activity("INT-ACT-EXPORT-CONFIG", "Config exported", "Platform Integration", "Configuration package ready"));
  }

  async testConnector(connectorId: string): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    this.connectors = this.connectors.map((connector) => {
      if (connector.id !== connectorId) return connector;
      const disabled = connector.status === "disabled";
      const testDetails = getConnectorTestDetails(connector, disabled);
      return {
        ...connector,
        status: disabled ? "disabled" : "healthy",
        latencyMs: disabled ? 0 : deterministicLatency[connector.id] ?? connector.latencyMs,
        lastCheckedAt: timestamp,
        testStatus: disabled ? "disabled" : "passed",
        ...testDetails,
      };
    });
    return this.snapshot("connections-tested", activity(`INT-ACT-TEST-${connectorId}`, "Connector tested", connectorId, "Connector test complete"));
  }

  async toggleConnector(connectorId: string): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    this.connectors = this.connectors.map((connector) => connector.id === connectorId ? { ...connector, status: connector.status === "disabled" ? "enabled" : "disabled", lastCheckedAt: timestamp } : connector);
    return this.snapshot("connector-updated", activity(`INT-ACT-TOGGLE-${connectorId}`, "Connector toggled", connectorId, "Connector state updated", "warning"));
  }

  async refreshEndpoints(): Promise<EnterpriseIntegrationSnapshot> {
    this.apiEndpoints = this.apiEndpoints.map((endpoint, index) => ({ ...endpoint, version: index === 0 ? "v1.1" : endpoint.version }));
    return this.snapshot("endpoints-refreshed", activity("INT-ACT-REFRESH-ENDPOINTS", "Endpoints refreshed", "API Endpoint Overview", "API map refreshed"));
  }

  async exportApiMap(): Promise<EnterpriseIntegrationSnapshot> {
    return this.snapshot("api-map-exported", activity("INT-ACT-EXPORT-API-MAP", "API map exported", "API Endpoint Overview", "API map package ready"));
  }

  async addWebhook(): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    const index = this.nextWebhookIndex;
    this.nextWebhookIndex += 1;
    const webhook: WebhookConfiguration = { id: `WH-UX-007-${String(index).padStart(3, "0")}`, eventType: "integration.ux_event", targetUrl: `https://integrations.example.com/ux-007-${String(index).padStart(3, "0")}`, status: "enabled", retryPolicy: "3 retries / 15 minutes", lastDeliveryAt: timestamp };
    this.webhooks = [webhook, ...this.webhooks];
    return this.snapshot("webhook-added", activity(`INT-ACT-ADD-${webhook.id}`, "Webhook added", webhook.id, "Webhook configuration added"));
  }

  async testWebhook(webhookId: string): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    this.webhooks = this.webhooks.map((webhook) => webhook.id === webhookId ? {
      ...webhook,
      status: webhook.status === "disabled" ? "disabled" : "enabled",
      lastDeliveryAt: timestamp,
      lastTestedAt: timestamp,
      testStatus: webhook.status === "disabled" ? "disabled" : "passed",
      deliveryResult: webhook.status === "disabled" ? "Webhook disabled. Enable before testing." : "Webhook delivery test completed against local adapter configuration.",
    } : webhook);
    return this.snapshot("webhook-updated", activity(`INT-ACT-TEST-${webhookId}`, "Webhook tested", webhookId, "Webhook test delivery complete"));
  }

  async toggleWebhook(webhookId: string): Promise<EnterpriseIntegrationSnapshot> {
    const timestamp = new Date().toISOString();
    this.webhooks = this.webhooks.map((webhook) => webhook.id === webhookId ? { ...webhook, status: webhook.status === "enabled" ? "disabled" : "enabled", lastDeliveryAt: timestamp } : webhook);
    return this.snapshot("webhook-updated", activity(`INT-ACT-TOGGLE-${webhookId}`, "Webhook toggled", webhookId, "Webhook state updated", "warning"));
  }
}

export function createEnterpriseIntegrationClient(): EnterpriseIntegrationClient {
  return new DeterministicEnterpriseIntegrationClient();
}

export async function getEnterpriseIntegrationSnapshot(client: EnterpriseIntegrationClient): Promise<EnterpriseIntegrationSnapshot> {
  const [summary, connectors, apiEndpoints, webhooks, deployment, activityLog] = await Promise.all([
    client.getIntegrationSummary(),
    client.listConnectors(),
    client.listApiEndpoints(),
    client.listWebhooks(),
    client.getDeploymentEnvironment(),
    client.listIntegrationActivity(),
  ]);
  return { summary, connectors, apiEndpoints, webhooks, deployment, activity: activityLog };
}
