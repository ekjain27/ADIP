export interface IntegrationSummary {
  readonly integrationStatus: "ready" | "synced" | "connections-tested" | "config-exported" | "endpoints-refreshed" | "api-map-exported" | "webhook-added" | "connector-updated" | "webhook-updated";
  readonly activeEnvironment: string;
  readonly lastSyncAt: string;
  readonly releaseVersion: string;
}

export interface IntegrationConnector {
  readonly id: string;
  readonly name: string;
  readonly status: "enabled" | "disabled" | "healthy" | "warning";
  readonly endpoint: string;
  readonly authMode: string;
  readonly latencyMs: number;
  readonly lastCheckedAt: string;
  readonly detail: string;
  readonly testStatus?: "passed" | "failed" | "disabled";
  readonly testResult?: string;
  readonly authenticationResult?: string;
  readonly endpointValidation?: string;
  readonly adapterHandshake?: string;
}

export interface ApiEndpointOverview {
  readonly id: string;
  readonly name: string;
  readonly method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  readonly path: string;
  readonly service: string;
  readonly status: "available" | "degraded" | "disabled";
  readonly version: string;
}

export interface WebhookConfiguration {
  readonly id: string;
  readonly eventType: string;
  readonly targetUrl: string;
  readonly status: "enabled" | "disabled" | "testing";
  readonly retryPolicy: string;
  readonly lastDeliveryAt: string;
  readonly lastTestedAt?: string;
  readonly testStatus?: "passed" | "failed" | "disabled";
  readonly deliveryResult?: string;
}

export interface DeploymentEnvironment {
  readonly environment: string;
  readonly releaseTag: string;
  readonly runtime: string;
  readonly buildStatus: string;
  readonly monitoringMode: string;
  readonly regressionBaseline: string;
  readonly commercialReadiness: string;
}

export interface IntegrationActivity {
  readonly id: string;
  readonly timestamp: string;
  readonly action: string;
  readonly connector: string;
  readonly result: string;
  readonly severity: "info" | "warning" | "critical";
}

export interface EnterpriseIntegrationSnapshot {
  readonly summary: IntegrationSummary;
  readonly connectors: readonly IntegrationConnector[];
  readonly apiEndpoints: readonly ApiEndpointOverview[];
  readonly webhooks: readonly WebhookConfiguration[];
  readonly deployment: DeploymentEnvironment;
  readonly activity: readonly IntegrationActivity[];
}

export interface EnterpriseIntegrationClient {
  getIntegrationSummary(): Promise<IntegrationSummary>;
  listConnectors(): Promise<readonly IntegrationConnector[]>;
  listApiEndpoints(): Promise<readonly ApiEndpointOverview[]>;
  listWebhooks(): Promise<readonly WebhookConfiguration[]>;
  getDeploymentEnvironment(): Promise<DeploymentEnvironment>;
  listIntegrationActivity(): Promise<readonly IntegrationActivity[]>;
  syncIntegrations(): Promise<EnterpriseIntegrationSnapshot>;
  testConnections(): Promise<EnterpriseIntegrationSnapshot>;
  exportConfig(): Promise<EnterpriseIntegrationSnapshot>;
  testConnector(connectorId: string): Promise<EnterpriseIntegrationSnapshot>;
  toggleConnector(connectorId: string): Promise<EnterpriseIntegrationSnapshot>;
  refreshEndpoints(): Promise<EnterpriseIntegrationSnapshot>;
  exportApiMap(): Promise<EnterpriseIntegrationSnapshot>;
  addWebhook(): Promise<EnterpriseIntegrationSnapshot>;
  testWebhook(webhookId: string): Promise<EnterpriseIntegrationSnapshot>;
  toggleWebhook(webhookId: string): Promise<EnterpriseIntegrationSnapshot>;
}
