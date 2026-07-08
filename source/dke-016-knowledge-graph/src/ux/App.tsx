import { useEffect, useMemo, useState } from "react";
import type { Dispatch, ReactNode, SetStateAction } from "react";
import {
  createBackendStatusClient,
  createAdministrationUserManagementClient,
  createDashboardViewModel,
  createDecisionWorkspaceClient,
  createDocumentationGenerationClient,
  createEnterpriseIntegrationClient,
  createExplainabilityAnalyticsClient,
  createKnowledgeGraphProvenanceClient,
  ENTERPRISE_SHELL_CSS,
  findNavigationEntry,
  getAdministrationSnapshot,
  getDecisionWorkspaceSnapshot,
  getDocumentationGenerationSnapshot,
  getEnterpriseIntegrationSnapshot,
  getExplainabilityAnalyticsSnapshot,
  getKnowledgeGraphSnapshot,
  toHashRoute,
  UX_ROADMAP_NAVIGATION,
  type ApiEndpointOverview,
  type AdministrationRole,
  type AdministrationSnapshot,
  type AdministrationUser,
  type AdministrationUserManagementClient,
  type AuditLogEntry,
  type BackendStatusClient,
  type DashboardViewModel,
  type DecisionAlternative,
  type DecisionHistoryItem,
  type DecisionWorkspaceClient,
  type DecisionWorkspaceSnapshot,
  type DocumentationGenerationClient,
  type DocumentationGenerationSnapshot,
  type EnterpriseIntegrationClient,
  type EnterpriseIntegrationSnapshot,
  type GeneratedAsset,
  type GeneratedDocument,
  type GenerationActivity,
  type ExplainabilityAnalyticsClient,
  type ExplainabilityAnalyticsSnapshot,
  type ExplainabilityTimelineEvent,
  type EvaluationResult,
  type FeatureImportanceItem,
  type GraphFilters,
  type IntegrationActivity,
  type IntegrationConnector,
  type KnowledgeGraphProvenanceClient,
  type KnowledgeGraphSnapshot,
  type NavigationEntry,
  type RankingResult,
  type ShellTheme,
  type SummaryCard,
  type UxGraphEdge,
  type UxGraphNode,
  type WebhookConfiguration,
  type WorkspaceTimelineEvent,
} from "./index.js";
import { getPreviewRoutePath } from "./previewRouting.js";

const PREVIEW_CSS = `
  * { box-sizing: border-box; }
  body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  button { font: inherit; }
  .ux-preview-toolbar { position: fixed; z-index: 10; right: 20px; bottom: 20px; display: flex; gap: 8px; }
  .ux-preview-toolbar button { border: 1px solid #8a94a6; border-radius: 6px; background: #ffffff; color: #17202a; padding: 8px 12px; cursor: pointer; }
  .ux-preview-toolbar button[aria-pressed="true"] { background: #2f6bff; border-color: #2f6bff; color: #ffffff; }
`;

interface AppProps {
  readonly backendStatusClient?: BackendStatusClient;
  readonly administrationClient?: AdministrationUserManagementClient;
  readonly decisionWorkspaceClient?: DecisionWorkspaceClient;
  readonly documentationGenerationClient?: DocumentationGenerationClient;
  readonly enterpriseIntegrationClient?: EnterpriseIntegrationClient;
  readonly knowledgeGraphClient?: KnowledgeGraphProvenanceClient;
  readonly explainabilityClient?: ExplainabilityAnalyticsClient;
}

export function App({ backendStatusClient, administrationClient, decisionWorkspaceClient, documentationGenerationClient, enterpriseIntegrationClient, knowledgeGraphClient, explainabilityClient }: AppProps = {}) {
  const [routePath, setRoutePath] = useState(() => getPreviewRoutePath(window.location.pathname, window.location.hash));
  const [theme, setTheme] = useState<ShellTheme>("light");
  const [dashboard, setDashboard] = useState<DashboardViewModel | null>(null);
  const [administration, setAdministration] = useState<AdministrationSnapshot | null>(null);
  const [workspace, setWorkspace] = useState<DecisionWorkspaceSnapshot | null>(null);
  const [documentationGeneration, setDocumentationGeneration] = useState<DocumentationGenerationSnapshot | null>(null);
  const [enterpriseIntegration, setEnterpriseIntegration] = useState<EnterpriseIntegrationSnapshot | null>(null);
  const [knowledgeGraph, setKnowledgeGraph] = useState<KnowledgeGraphSnapshot | null>(null);
  const [explainability, setExplainability] = useState<ExplainabilityAnalyticsSnapshot | null>(null);
  const backendClient = useMemo(() => backendStatusClient ?? createBackendStatusClient(), [backendStatusClient]);
  const adminClient = useMemo(() => administrationClient ?? createAdministrationUserManagementClient(), [administrationClient]);
  const decisionClient = useMemo(() => decisionWorkspaceClient ?? createDecisionWorkspaceClient(), [decisionWorkspaceClient]);
  const documentationClient = useMemo(() => documentationGenerationClient ?? createDocumentationGenerationClient(), [documentationGenerationClient]);
  const integrationClient = useMemo(() => enterpriseIntegrationClient ?? createEnterpriseIntegrationClient(), [enterpriseIntegrationClient]);
  const kgClient = useMemo(() => knowledgeGraphClient ?? createKnowledgeGraphProvenanceClient(), [knowledgeGraphClient]);
  const xaiClient = useMemo(() => explainabilityClient ?? createExplainabilityAnalyticsClient(), [explainabilityClient]);
  const activeRoute = findNavigationEntry(routePath);

  useEffect(() => {
    let active = true;
    createDashboardViewModel(backendClient).then((viewModel) => {
      if (active) setDashboard(viewModel);
    });
    return () => {
      active = false;
    };
  }, [backendClient]);

  useEffect(() => {
    let active = true;
    getAdministrationSnapshot(adminClient).then((snapshot) => {
      if (active) setAdministration(snapshot);
    });
    return () => {
      active = false;
    };
  }, [adminClient]);

  useEffect(() => {
    let active = true;
    getDecisionWorkspaceSnapshot(decisionClient).then((snapshot) => {
      if (active) setWorkspace(snapshot);
    });
    return () => {
      active = false;
    };
  }, [decisionClient]);

  useEffect(() => {
    let active = true;
    getDocumentationGenerationSnapshot(documentationClient).then((snapshot) => {
      if (active) setDocumentationGeneration(snapshot);
    });
    return () => {
      active = false;
    };
  }, [documentationClient]);

  useEffect(() => {
    let active = true;
    getEnterpriseIntegrationSnapshot(integrationClient).then((snapshot) => {
      if (active) setEnterpriseIntegration(snapshot);
    });
    return () => {
      active = false;
    };
  }, [integrationClient]);

  useEffect(() => {
    let active = true;
    getKnowledgeGraphSnapshot(kgClient).then((snapshot) => {
      if (active) setKnowledgeGraph(snapshot);
    });
    return () => {
      active = false;
    };
  }, [kgClient]);

  useEffect(() => {
    let active = true;
    getExplainabilityAnalyticsSnapshot(xaiClient).then((snapshot) => {
      if (active) setExplainability(snapshot);
    });
    return () => {
      active = false;
    };
  }, [xaiClient]);

  useEffect(() => {
    const handleRouteChange = () => setRoutePath(getPreviewRoutePath(window.location.pathname, window.location.hash));
    window.addEventListener("hashchange", handleRouteChange);
    window.addEventListener("popstate", handleRouteChange);
    return () => {
      window.removeEventListener("hashchange", handleRouteChange);
      window.removeEventListener("popstate", handleRouteChange);
    };
  }, []);

  function navigateTo(entry: NavigationEntry) {
    window.location.hash = toHashRoute(entry.path);
    setRoutePath(entry.path);
  }

  return (
    <>
      <style>{PREVIEW_CSS + ENTERPRISE_SHELL_CSS}</style>
      <div className="ux-shell" data-theme={theme}>
        <aside className="ux-sidebar" aria-label="Primary navigation">
          <div className="ux-brand">
            <span className="ux-brand-mark">DI</span>
            <span>
              <strong>Decision Intelligence</strong>
              <small>Enterprise UX Shell</small>
            </span>
          </div>
          <nav>
            {UX_ROADMAP_NAVIGATION.map((entry) => (
              <button
                className="ux-nav-link"
                type="button"
                aria-current={entry.id === activeRoute.id ? "true" : "false"}
                data-route-id={entry.id}
                data-route-path={entry.path}
                key={entry.id}
                onClick={() => navigateTo(entry)}
              >
                {entry.label}
              </button>
            ))}
          </nav>
        </aside>
        <section className="ux-workspace">
          <header className="ux-topbar">
            <div>
              <span className="ux-route-title">{activeRoute.label}</span>
              <span className="ux-route-subtitle">{activeRoute.uxModule} application layer</span>
            </div>
            <span className="ux-boundary-label">Backend API Boundary</span>
          </header>
          <main className="ux-main">
            {activeRoute.id === "dashboard" ? (
              dashboard ? <DashboardPage viewModel={dashboard} /> : <section className="ux-placeholder">Loading dashboard...</section>
            ) : activeRoute.id === "decision-workspace" ? (
              workspace ? (
                <DecisionWorkspacePage snapshot={workspace} client={decisionClient} onSnapshotChange={setWorkspace} />
              ) : (
                <section className="ux-placeholder">Loading decision workspace...</section>
              )
            ) : activeRoute.id === "knowledge-graph" ? (
              knowledgeGraph ? (
                <KnowledgeGraphExplorerPage snapshot={knowledgeGraph} client={kgClient} onSnapshotChange={setKnowledgeGraph} />
              ) : (
                <section className="ux-placeholder">Loading knowledge graph...</section>
              )
            ) : activeRoute.id === "explainability" ? (
              explainability ? (
                <ExplainabilityAnalyticsPage snapshot={explainability} client={xaiClient} onSnapshotChange={setExplainability} />
              ) : (
                <section className="ux-placeholder">Loading explainability analytics...</section>
              )
            ) : activeRoute.id === "documentation" ? (
              documentationGeneration ? (
                <DocumentationGenerationPage snapshot={documentationGeneration} client={documentationClient} onSnapshotChange={setDocumentationGeneration} />
              ) : (
                <section className="ux-placeholder">Loading documentation generator...</section>
              )
            ) : activeRoute.id === "administration" ? (
              administration ? (
                <AdministrationUserManagementPage snapshot={administration} client={adminClient} onSnapshotChange={setAdministration} />
              ) : (
                <section className="ux-placeholder">Loading administration center...</section>
              )
            ) : activeRoute.id === "platform-integration" ? (
              enterpriseIntegration ? (
                <EnterprisePlatformIntegrationPage snapshot={enterpriseIntegration} client={integrationClient} onSnapshotChange={setEnterpriseIntegration} />
              ) : (
                <section className="ux-placeholder">Loading platform integration console...</section>
              )
            ) : (
              <PlaceholderPage entry={activeRoute} />
            )}
          </main>
        </section>
      </div>
      <div className="ux-preview-toolbar" aria-label="Preview theme controls">
        <button type="button" aria-pressed={theme === "light"} onClick={() => setTheme("light")}>
          Light
        </button>
        <button type="button" aria-pressed={theme === "dark"} onClick={() => setTheme("dark")}>
          Dark
        </button>
      </div>
    </>
  );
}

const KNOWLEDGE_GRAPH_PREFERENCES_KEY = "project1.ux003.graph.preferences.v1";
const DOCUMENTATION_GENERATOR_STATE_KEY = "project1.ux005.generator.snapshot.v1";

function getSafeLocalStorage(): Storage | null {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

function saveGraphPreferences(filters: GraphFilters, selectedNodeId: string, selectedEdgeId: string): void {
  const storage = getSafeLocalStorage();
  if (!storage) return;
  try {
    storage.setItem(KNOWLEDGE_GRAPH_PREFERENCES_KEY, JSON.stringify({ filters, selectedNodeId, selectedEdgeId }));
  } catch {
    // Preferences are optional UX preview state.
  }
}

function loadGraphPreferences(): { readonly filters: GraphFilters; readonly selectedNodeId?: string; readonly selectedEdgeId?: string } | null {
  const storage = getSafeLocalStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(KNOWLEDGE_GRAPH_PREFERENCES_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<{ filters: GraphFilters; selectedNodeId: string; selectedEdgeId: string }>;
    if (!parsed.filters) return null;
    const { nodeType, relationshipType, confidenceRange, governanceStatus, timePeriod, provenanceSource } = parsed.filters;
    if ([nodeType, relationshipType, confidenceRange, governanceStatus, timePeriod, provenanceSource].some((value) => typeof value !== "string")) return null;
    return {
      filters: parsed.filters,
      selectedNodeId: typeof parsed.selectedNodeId === "string" ? parsed.selectedNodeId : undefined,
      selectedEdgeId: typeof parsed.selectedEdgeId === "string" ? parsed.selectedEdgeId : undefined,
    };
  } catch {
    return null;
  }
}

function saveDocumentationGeneratorState(state: { readonly generatedPackage: "documentation" | "patent" | "research" | null; readonly previewTitle: string; readonly previewDetails: readonly string[] }): void {
  const storage = getSafeLocalStorage();
  if (!storage) return;
  try {
    storage.setItem(DOCUMENTATION_GENERATOR_STATE_KEY, JSON.stringify(state));
  } catch {
    // Generated preview state is optional UX demo state.
  }
}

function loadDocumentationGeneratorState(): { readonly generatedPackage: "documentation" | "patent" | "research" | null; readonly previewTitle: string; readonly previewDetails: readonly string[] } | null {
  const storage = getSafeLocalStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(DOCUMENTATION_GENERATOR_STATE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<{ generatedPackage: "documentation" | "patent" | "research" | null; previewTitle: string; previewDetails: string[] }>;
    if (!(parsed.generatedPackage === "documentation" || parsed.generatedPackage === "patent" || parsed.generatedPackage === "research" || parsed.generatedPackage === null)) return null;
    if (typeof parsed.previewTitle !== "string" || !Array.isArray(parsed.previewDetails) || !parsed.previewDetails.every((item) => typeof item === "string")) return null;
    return { generatedPackage: parsed.generatedPackage, previewTitle: parsed.previewTitle, previewDetails: parsed.previewDetails };
  } catch {
    return null;
  }
}

function confidenceMatches(value: number, range: string): boolean {
  const [min, max] = range.split("-").map(Number);
  if (Number.isNaN(min) || Number.isNaN(max)) return true;
  return value >= min && value <= max;
}

function getGraphReferenceTime(snapshot: KnowledgeGraphSnapshot): number {
  const timestamps = [...snapshot.edges.map((edge) => Date.parse(edge.timestamp)), ...snapshot.timeline.map((event) => Date.parse(event.timestamp))]
    .filter((value) => !Number.isNaN(value));
  return timestamps.length > 0 ? Math.max(...timestamps) : Date.now();
}

function timePeriodMatches(timestamp: string, period: string, referenceTime: number): boolean {
  if (period === "all") return true;
  const parsed = Date.parse(timestamp);
  if (Number.isNaN(parsed)) return true;
  const windowMs = period === "last-7d" ? 7 * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
  return referenceTime - parsed <= windowMs;
}

function nodeTimeMatches(node: UxGraphNode, snapshot: KnowledgeGraphSnapshot, filters: GraphFilters, referenceTime: number): boolean {
  if (filters.timePeriod === "all") return true;
  const relatedEdges = snapshot.edges.filter((edge) => edge.sourceNodeId === node.id || edge.targetNodeId === node.id);
  if (relatedEdges.length === 0) return true;
  return relatedEdges.some((edge) => timePeriodMatches(edge.timestamp, filters.timePeriod, referenceTime));
}

function provenanceSourceMatchesNode(node: UxGraphNode, filters: GraphFilters): boolean {
  return filters.provenanceSource === "all" || node.sourceModule === filters.provenanceSource;
}

function provenanceSourceMatchesEdge(edge: UxGraphEdge, snapshot: KnowledgeGraphSnapshot, filters: GraphFilters): boolean {
  if (filters.provenanceSource === "all") return true;
  const source = snapshot.nodes.find((node) => node.id === edge.sourceNodeId);
  const target = snapshot.nodes.find((node) => node.id === edge.targetNodeId);
  const provenanceEvent = snapshot.timeline.find((event) => event.id === edge.provenanceReference);
  return source?.sourceModule === filters.provenanceSource || target?.sourceModule === filters.provenanceSource || provenanceEvent?.sourceModule === filters.provenanceSource;
}

function filterKnowledgeGraph(snapshot: KnowledgeGraphSnapshot, filters: GraphFilters): { readonly nodes: readonly UxGraphNode[]; readonly edges: readonly UxGraphEdge[] } {
  const referenceTime = getGraphReferenceTime(snapshot);
  const nodes = snapshot.nodes.filter((node) =>
    (filters.nodeType === "all" || node.type === filters.nodeType)
    && confidenceMatches(node.confidence, filters.confidenceRange)
    && (filters.governanceStatus === "all" || node.governanceStatus === filters.governanceStatus)
    && provenanceSourceMatchesNode(node, filters)
    && nodeTimeMatches(node, snapshot, filters, referenceTime),
  );
  const visibleNodeIds = new Set(nodes.map((node) => node.id));
  const edges = snapshot.edges.filter((edge) =>
    visibleNodeIds.has(edge.sourceNodeId)
    && visibleNodeIds.has(edge.targetNodeId)
    && (filters.relationshipType === "all" || edge.relationshipType === filters.relationshipType)
    && confidenceMatches(edge.confidence, filters.confidenceRange)
    && timePeriodMatches(edge.timestamp, filters.timePeriod, referenceTime)
    && provenanceSourceMatchesEdge(edge, snapshot, filters),
  );
  return { nodes, edges };
}

function EnterprisePlatformIntegrationPage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: EnterpriseIntegrationSnapshot;
  client: EnterpriseIntegrationClient;
  onSnapshotChange: Dispatch<SetStateAction<EnterpriseIntegrationSnapshot | null>>;
}) {
  const [runningAction, setRunningAction] = useState<string | null>(null);
  const [selectedConnectorId, setSelectedConnectorId] = useState(snapshot.connectors[0]?.id ?? "");
  const [selectedWebhookId, setSelectedWebhookId] = useState(snapshot.webhooks[0]?.id ?? "");
  const [endpointRefreshCount, setEndpointRefreshCount] = useState(0);
  const [endpointLastRefreshedAt, setEndpointLastRefreshedAt] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState("Integration console ready");
  const [configExport, setConfigExport] = useState<{ href: string; filename: string } | null>(null);
  const [apiMapExport, setApiMapExport] = useState<{ href: string; filename: string } | null>(null);
  const visibleActivity = getVisibleIntegrationActivity(snapshot.activity);
  const selectedConnector = snapshot.connectors.find((connector) => connector.id === selectedConnectorId) ?? snapshot.connectors[0];
  const connectionSummary = getConnectionTestSummary(snapshot.connectors);
  const endpointSummary = getEndpointRefreshSummary(snapshot.apiEndpoints, endpointRefreshCount, endpointLastRefreshedAt);

  async function runIntegrationAction(actionId: string, loadingLabel: string, completeLabel: string, run: () => Promise<EnterpriseIntegrationSnapshot>) {
    setRunningAction(actionId);
    setLastAction(loadingLabel);
    try {
      const next = mergeEnterpriseIntegrationSnapshot(await run(), snapshot);
      setRunningAction(null);
      if (actionId.startsWith("test-connector-")) setSelectedConnectorId(actionId.replace("test-connector-", ""));
      if (actionId.startsWith("test-webhook-")) setSelectedWebhookId(actionId.replace("test-webhook-", ""));
      if (actionId === "refresh-endpoints") {
        setEndpointRefreshCount((count) => count + 1);
        setEndpointLastRefreshedAt(next.summary.lastSyncAt);
      }
      setLastAction(getIntegrationActionMessage(actionId, completeLabel, next.summary.lastSyncAt));
      onSnapshotChange(next);
    } catch {
      setRunningAction(null);
      setLastAction(`${completeLabel} failed safely. Backend integration logic remains authoritative.`);
    }
  }

  async function exportIntegrationConfig() {
    setRunningAction("export-config");
    setLastAction("Exporting integration config...");
    try {
      const next = mergeEnterpriseIntegrationSnapshot(await client.exportConfig(), snapshot);
      setConfigExport({ href: `data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(next, null, 2))}`, filename: "ux-007-integration-config.json" });
      setRunningAction(null);
      setLastAction(`Config exported at ${formatTimestamp(next.summary.lastSyncAt)}`);
      onSnapshotChange(next);
    } catch {
      setRunningAction(null);
      setLastAction("Config export failed safely.");
    }
  }

  async function exportApiMap() {
    setRunningAction("export-api-map");
    setLastAction("Exporting API map...");
    try {
      const next = mergeEnterpriseIntegrationSnapshot(await client.exportApiMap(), snapshot);
      setApiMapExport({ href: `data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(next.apiEndpoints, null, 2))}`, filename: "ux-007-api-map.json" });
      setRunningAction(null);
      setLastAction(`API map exported at ${formatTimestamp(next.summary.lastSyncAt)}`);
      onSnapshotChange(next);
    } catch {
      setRunningAction(null);
      setLastAction("API map export failed safely.");
    }
  }

  return (
    <section className="ux-integration" aria-labelledby="integration-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-007</p>
          <h1 id="integration-title">Enterprise Platform Integration Console</h1>
          <div className="ux-workspace-meta">
            <span>Integration Status {formatStatusLabel(snapshot.summary.integrationStatus)}</span>
            <span>{snapshot.summary.activeEnvironment}</span>
            <span>Last Sync {formatTimestamp(snapshot.summary.lastSyncAt)}</span>
            <span>{snapshot.summary.releaseVersion}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(snapshot.summary.integrationStatus)}</span>
      </header>

      <section className="ux-workspace-actions" aria-label="Integration actions">
        <button type="button" data-action-id="sync-integrations" disabled={runningAction === "sync-integrations"} onClick={() => void runIntegrationAction("sync-integrations", "Syncing integrations...", "Integrations synced", () => client.syncIntegrations())}>{runningAction === "sync-integrations" ? "Syncing integrations..." : "Sync Integrations"}</button>
        <button type="button" data-action-id="test-connections" disabled={runningAction === "test-connections"} onClick={() => void runIntegrationAction("test-connections", "Testing connections...", "Connections tested", () => client.testConnections())}>{runningAction === "test-connections" ? "Testing connections..." : "Test Connections"}</button>
        <button type="button" data-action-id="refresh-endpoints" disabled={runningAction === "refresh-endpoints"} onClick={() => void runIntegrationAction("refresh-endpoints", "Refreshing endpoints...", "Endpoints refreshed", () => client.refreshEndpoints())}>{runningAction === "refresh-endpoints" ? "Refreshing endpoints..." : "Refresh Endpoints"}</button>
        <button type="button" data-action-id="export-config" disabled={runningAction === "export-config"} onClick={() => void exportIntegrationConfig()}>{runningAction === "export-config" ? "Exporting config..." : "Export Config"}</button>
        <button type="button" data-action-id="export-api-map" disabled={runningAction === "export-api-map"} onClick={() => void exportApiMap()}>{runningAction === "export-api-map" ? "Exporting API map..." : "Export API Map"}</button>
      </section>

      <section className="ux-action-status">
        <span>{lastAction}</span>
        {selectedConnector ? <span>Selected connector {selectedConnector.name}: {formatStatusLabel(selectedConnector.status)}, {selectedConnector.latencyMs} ms, checked {formatTimestamp(selectedConnector.lastCheckedAt)}</span> : null}
        {configExport ? <a data-action-id="download-config" href={configExport.href} download={configExport.filename}>Download config JSON</a> : null}
        {apiMapExport ? <a data-action-id="download-api-map" href={apiMapExport.href} download={apiMapExport.filename}>Download API map JSON</a> : null}
      </section>

      <section className="ux-workspace-grid">
        <article className="ux-panel ux-context-panel">
          <h2>Connector Management</h2>
          <section className="ux-action-status" aria-label="Connection test summary">
            <span>Connection Test Summary</span>
            <span>Total connectors {connectionSummary.total}</span>
            <span>Passed {connectionSummary.passed}</span>
            <span>Failed {connectionSummary.failed}</span>
            <span>Disabled {connectionSummary.disabled}</span>
            <span>Average latency {connectionSummary.averageLatencyMs} ms</span>
            <span>Tested at {connectionSummary.testedAt ? formatTimestamp(connectionSummary.testedAt) : "Not tested this session"}</span>
          </section>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead><tr><th>Connector</th><th>Status</th><th>Endpoint</th><th>Auth</th><th>Latency</th><th>Last Checked</th><th>Test Result</th><th>Actions</th></tr></thead>
              <tbody>{snapshot.connectors.map((connector) => <IntegrationConnectorRow client={client} connector={connector} key={connector.id} onAction={runIntegrationAction} />)}</tbody>
            </table>
          </div>
        </article>

        {selectedConnector ? <article className="ux-panel">
          <h2>Connector Details</h2>
          <dl className="ux-inspector-list">
            <ContextItem label="Connector">{selectedConnector.name}</ContextItem>
            <ContextItem label="Endpoint">{selectedConnector.endpoint}</ContextItem>
            <ContextItem label="Auth Type">{selectedConnector.authMode}</ContextItem>
            <ContextItem label="Status">{formatStatusLabel(selectedConnector.status)}</ContextItem>
            <ContextItem label="Latency">{selectedConnector.latencyMs} ms</ContextItem>
            <ContextItem label="Last Checked">{formatTimestamp(selectedConnector.lastCheckedAt)}</ContextItem>
            <ContextItem label="Authentication Result">{selectedConnector.authenticationResult ?? "Run the row-level Test action to validate authentication through the UX adapter."}</ContextItem>
            <ContextItem label="Endpoint Validation">{selectedConnector.endpointValidation ?? "Run the row-level Test action to validate the endpoint map entry."}</ContextItem>
            <ContextItem label="Adapter Handshake">{selectedConnector.adapterHandshake ?? "Run the row-level Test action to complete the local adapter handshake check."}</ContextItem>
            <ContextItem label="Last Test Result">{selectedConnector.testResult ?? "No connector test has been run for this connector."}</ContextItem>
            <ContextItem label="Description">{selectedConnector.detail}</ContextItem>
            <ContextItem label="Production Readiness Note">UX-007 displays adapter-owned connector state only. Real integration checks remain backend-owned.</ContextItem>
          </dl>
        </article> : null}

        <article className="ux-panel ux-context-panel">
          <h2>API Endpoint Overview</h2>
          <section className="ux-action-status" aria-label="Endpoint refresh summary">
            <span>Endpoint Refresh Summary</span>
            <span>Endpoint count {endpointSummary.count}</span>
            <span>Methods available {endpointSummary.methods}</span>
            <span>Snapshot version {endpointSummary.version}</span>
            <span>Refreshed at {endpointSummary.refreshedAt ? formatTimestamp(endpointSummary.refreshedAt) : "Not refreshed this session"}</span>
          </section>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead><tr><th>Name</th><th>Method</th><th>Path</th><th>Service</th><th>Status</th><th>Version</th><th>Refresh State</th></tr></thead>
              <tbody>{snapshot.apiEndpoints.map((endpoint) => <tr className={endpointRefreshCount > 0 ? "ux-refreshed-row" : undefined} key={endpoint.id}><td>{endpoint.name}</td><td>{endpoint.method}</td><td>{endpoint.path}</td><td>{endpoint.service}</td><td>{formatStatusLabel(endpoint.status)}</td><td>{endpoint.version}</td><td>{endpointRefreshCount > 0 ? "Refreshed" : "Current snapshot"}</td></tr>)}</tbody>
            </table>
          </div>
        </article>

        <article className="ux-panel ux-context-panel">
          <h2>Webhook Configuration</h2>
          <section className="ux-workspace-actions">
            <button type="button" data-action-id="add-webhook" disabled={runningAction === "add-webhook"} onClick={() => void runIntegrationAction("add-webhook", "Adding webhook...", "Webhook added", () => client.addWebhook())}>{runningAction === "add-webhook" ? "Adding webhook..." : "Add Webhook"}</button>
          </section>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead><tr><th>Webhook</th><th>Event</th><th>Target</th><th>Status</th><th>Retry</th><th>Last Delivery</th><th>Test Result</th><th>Actions</th></tr></thead>
              <tbody>{snapshot.webhooks.map((webhook) => <WebhookRow client={client} isSelected={webhook.id === selectedWebhookId} key={webhook.id} onAction={runIntegrationAction} webhook={webhook} />)}</tbody>
            </table>
          </div>
        </article>

        <article className="ux-panel">
          <h2>Deployment & Environment</h2>
          <dl className="ux-inspector-list">
            <ContextItem label="Environment">{snapshot.deployment.environment}</ContextItem>
            <ContextItem label="Release Tag">{snapshot.deployment.releaseTag}</ContextItem>
            <ContextItem label="Runtime">{snapshot.deployment.runtime}</ContextItem>
            <ContextItem label="Build Status">{snapshot.deployment.buildStatus}</ContextItem>
            <ContextItem label="Monitoring Mode">{snapshot.deployment.monitoringMode}</ContextItem>
            <ContextItem label="Regression Baseline">{snapshot.deployment.regressionBaseline}</ContextItem>
            <ContextItem label="Commercial Readiness">{snapshot.deployment.commercialReadiness}</ContextItem>
          </dl>
        </article>

        <article className="ux-panel ux-context-panel">
          <h2>Integration Activity Log</h2>
          <ol className="ux-timeline">
            {visibleActivity.map((event) => (
              <li data-status={event.severity} key={event.id}>
                <div>
                  <strong>{event.action}</strong>
                  <span>{formatTimestamp(event.timestamp)}</span>
                  <p>{event.connector} - {event.result}</p>
                </div>
                <span className="ux-activity-badge">{formatStatusLabel(event.severity)}</span>
              </li>
            ))}
          </ol>
        </article>

        <article className="ux-panel ux-boundary-panel">
          <h2>Backend Boundary</h2>
          <p>Connector, API endpoint, webhook, deployment, and activity data are consumed through EnterpriseIntegrationClient. Real platform integration logic stays outside the UI.</p>
        </article>
      </section>
    </section>
  );
}

function IntegrationConnectorRow({ client, connector, onAction }: { client: EnterpriseIntegrationClient; connector: IntegrationConnector; onAction: (actionId: string, loadingLabel: string, completeLabel: string, run: () => Promise<EnterpriseIntegrationSnapshot>) => Promise<void> }) {
  return (
    <tr>
      <td><strong>{connector.name}</strong><span>{connector.detail}</span></td>
      <td>{formatStatusLabel(connector.status)}</td>
      <td>{connector.endpoint}</td>
      <td>{connector.authMode}</td>
      <td>{connector.latencyMs} ms</td>
      <td>{formatTimestamp(connector.lastCheckedAt)}</td>
      <td>{connector.testStatus ? formatStatusLabel(connector.testStatus) : "Not tested"}<span>{connector.testResult ?? "No test result yet."}</span></td>
      <td>
        <button type="button" data-action-id={`test-connector-${connector.id}`} onClick={() => void onAction(`test-connector-${connector.id}`, "Testing connector...", "Connector tested", () => client.testConnector(connector.id))}>Test</button>
        <button type="button" data-action-id={`toggle-connector-${connector.id}`} onClick={() => void onAction(`toggle-connector-${connector.id}`, "Updating connector...", "Connector toggled", () => client.toggleConnector(connector.id))}>{connector.status === "disabled" ? "Enable" : "Disable"}</button>
      </td>
    </tr>
  );
}

function WebhookRow({ client, isSelected, onAction, webhook }: { client: EnterpriseIntegrationClient; isSelected: boolean; onAction: (actionId: string, loadingLabel: string, completeLabel: string, run: () => Promise<EnterpriseIntegrationSnapshot>) => Promise<void>; webhook: WebhookConfiguration }) {
  return (
    <tr aria-selected={isSelected} className={isSelected ? "ux-selected-row" : undefined}>
      <td>{webhook.id}</td>
      <td>{webhook.eventType}</td>
      <td>{webhook.targetUrl}</td>
      <td>{formatStatusLabel(webhook.status)}</td>
      <td>{webhook.retryPolicy}</td>
      <td>{formatTimestamp(webhook.lastDeliveryAt)}</td>
      <td>{webhook.testStatus ? formatStatusLabel(webhook.testStatus) : "Not tested"}<span>{webhook.lastTestedAt ? formatTimestamp(webhook.lastTestedAt) : "No webhook test yet."}</span><span>{webhook.deliveryResult ?? "Awaiting local adapter webhook test."}</span></td>
      <td>
        <button type="button" data-action-id={`test-webhook-${webhook.id}`} onClick={() => void onAction(`test-webhook-${webhook.id}`, "Testing webhook...", "Webhook tested", () => client.testWebhook(webhook.id))}>Test Webhook</button>
        <button type="button" data-action-id={`toggle-webhook-${webhook.id}`} onClick={() => void onAction(`toggle-webhook-${webhook.id}`, "Updating webhook...", "Webhook toggled", () => client.toggleWebhook(webhook.id))}>{webhook.status === "enabled" ? "Disable" : "Enable"}</button>
      </td>
    </tr>
  );
}

function getIntegrationActionMessage(actionId: string, completeLabel: string, timestamp: string): string {
  if (actionId === "sync-integrations") return `Integrations synced. Integration snapshot synced from current local adapter state. Updated ${formatTimestamp(timestamp)}`;
  if (actionId === "test-connections") return `Connections tested against current v1.0.0 adapter configuration. Updated ${formatTimestamp(timestamp)}`;
  if (actionId === "refresh-endpoints") return `Endpoints refreshed. API endpoints refreshed from current platform integration snapshot. Updated ${formatTimestamp(timestamp)}`;
  return `${completeLabel} at ${formatTimestamp(timestamp)}`;
}

function getConnectionTestSummary(connectors: readonly IntegrationConnector[]): { readonly total: number; readonly passed: number; readonly failed: number; readonly disabled: number; readonly averageLatencyMs: number; readonly testedAt: string | null } {
  const tested = connectors.filter((connector) => connector.testStatus);
  const passed = connectors.filter((connector) => connector.testStatus === "passed").length;
  const failed = connectors.filter((connector) => connector.testStatus === "failed").length;
  const disabled = connectors.filter((connector) => connector.testStatus === "disabled" || connector.status === "disabled").length;
  const latencyConnectors = tested.filter((connector) => connector.testStatus === "passed");
  const averageLatencyMs = latencyConnectors.length > 0 ? Math.round(latencyConnectors.reduce((total, connector) => total + connector.latencyMs, 0) / latencyConnectors.length) : 0;
  const testedAt = tested.length > 0 ? tested.reduce((latest, connector) => Date.parse(connector.lastCheckedAt) > Date.parse(latest) ? connector.lastCheckedAt : latest, tested[0].lastCheckedAt) : null;
  return { total: connectors.length, passed, failed, disabled, averageLatencyMs, testedAt };
}

function getEndpointRefreshSummary(apiEndpoints: readonly ApiEndpointOverview[], refreshCount: number, refreshedAt: string | null): { readonly count: number; readonly methods: string; readonly version: number; readonly refreshedAt: string | null } {
  return {
    count: apiEndpoints.length,
    methods: [...new Set(apiEndpoints.map((endpoint) => endpoint.method))].join(", "),
    version: refreshCount,
    refreshedAt,
  };
}

function AdministrationUserManagementPage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: AdministrationSnapshot;
  client: AdministrationUserManagementClient;
  onSnapshotChange: Dispatch<SetStateAction<AdministrationSnapshot | null>>;
}) {
  const [runningAction, setRunningAction] = useState<string | null>(null);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [roleSelection, setRoleSelection] = useState(snapshot.roles[0]?.role ?? "Decision Admin");
  const [lastAction, setLastAction] = useState("Administration ready");
  const [auditExport, setAuditExport] = useState<{ href: string; filename: string } | null>(null);
  const [showAddUserDialog, setShowAddUserDialog] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string | null>(null);
  const visibleAudit = getVisibleAuditLog(snapshot.auditLog);

  async function runAdminAction(
    actionId: string,
    loadingLabel: string,
    completeLabel: string,
    run: () => Promise<AdministrationSnapshot>,
    reconcile: (next: AdministrationSnapshot, current: AdministrationSnapshot) => AdministrationSnapshot = mergeAdministrationSnapshot,
  ) {
    setRunningAction(actionId);
    setLastAction(loadingLabel);
    try {
      const next = await run();
      setRunningAction(null);
      setShowAddUserDialog(false);
      setLastAction(`${completeLabel} at ${formatTimestamp(next.summary.lastSyncAt)}`);
      onSnapshotChange(reconcile(next, snapshot));
    } catch {
      setRunningAction(null);
      setLastAction(`${completeLabel} failed safely. Backend security logic remains authoritative.`);
    }
  }

  async function exportAuditLog() {
    setRunningAction("export-audit-log");
    setLastAction("Exporting audit log...");
    try {
      const next = await client.exportAuditLog();
      const mergedAudit = mergeAuditLog(next.auditLog, snapshot.auditLog);
      setAuditExport({ href: `data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(mergedAudit, null, 2))}`, filename: "ux-006-audit-log.json" });
      setRunningAction(null);
      setLastAction(`Audit log exported at ${formatTimestamp(next.summary.lastSyncAt)}`);
      onSnapshotChange(mergeAdministrationSnapshot({ ...next, auditLog: mergedAudit }, snapshot));
    } catch {
      setRunningAction(null);
      setLastAction("Audit log export failed safely.");
    }
  }

  async function refreshAdministration() {
    setRunningAction("refresh-administration");
    setLastAction("Refreshing administration...");
    try {
      const refreshed = typeof client.refreshAdministration === "function" ? await client.refreshAdministration() : await getAdministrationSnapshot(client);
      const next = mergeAdministrationSnapshot(refreshed, snapshot);
      const selectedStillExists = selectedUserId && next.users.some((user) => user.id === selectedUserId);
      setSelectedUserId(selectedStillExists ? selectedUserId : next.users[0]?.id ?? "");
      setRefreshCount((count) => count + 1);
      setLastRefreshedAt(refreshed.summary.lastSyncAt);
      setRunningAction(null);
      setLastAction(`Administration snapshot refreshed from current local data. Updated ${formatTimestamp(refreshed.summary.lastSyncAt)}`);
      onSnapshotChange(next);
    } catch {
      setRunningAction(null);
      setLastAction("Administration refresh failed safely. Backend security logic remains authoritative.");
    }
  }

  async function removeSelectedUser() {
    if (!selectedUser) {
      setLastAction("Select a user to remove.");
      return;
    }
    if (selectedUser.id === "USR-001") {
      setLastAction("Default administrator cannot be removed.");
      return;
    }
    const adminUsers = snapshot.users.filter((user) => user.role.toLowerCase().includes("admin"));
    if (selectedUser.role.toLowerCase().includes("admin") && adminUsers.length <= 1) {
      setLastAction("At least one administrator must remain.");
      return;
    }
    const confirmed = typeof window === "undefined" || typeof window.confirm !== "function"
      ? true
      : window.confirm(`Remove user ${selectedUser.name}? This action cannot be undone.`);
    if (!confirmed) {
      setLastAction("Remove user canceled");
      return;
    }
    setRunningAction("remove-user");
    setLastAction(`Removing ${selectedUser.name}...`);
    try {
      const next = typeof client.removeUser === "function"
        ? await client.removeUser(selectedUser.id)
        : removeAdministrationUserLocally(snapshot, selectedUser);
      const removedIndex = snapshot.users.findIndex((user) => user.id === selectedUser.id);
      const remainingInCurrentOrder = snapshot.users.filter((user) => user.id !== selectedUser.id);
      const nextSelected = remainingInCurrentOrder[removedIndex]?.id ?? remainingInCurrentOrder[removedIndex - 1]?.id ?? next.users[0]?.id ?? "";
      setSelectedUserId(nextSelected);
      setRunningAction(null);
      setLastAction(`User removed: ${selectedUser.id} ${selectedUser.name}`);
      onSnapshotChange(reconcileAdministrationRemoval(next, snapshot, selectedUser.id));
    } catch {
      setRunningAction(null);
      setLastAction("Remove user failed safely. Backend security logic remains authoritative.");
    }
  }

  function viewUser(user: AdministrationUser) {
    setSelectedUserId(user.id);
    setLastAction(`Viewing ${user.name}`);
  }

  const selectedUser = snapshot.users.find((user) => user.id === selectedUserId);

  return (
    <section className="ux-admin" aria-labelledby="admin-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-006</p>
          <h1 id="admin-title">Administration & User Management Center</h1>
          <div className="ux-workspace-meta">
            <span>System Status {formatStatusLabel(snapshot.summary.systemStatus)}</span>
            <span>{snapshot.summary.activeOrganization}</span>
            <span>Users {snapshot.users.length}</span>
            <span>Last Sync {formatTimestamp(snapshot.summary.lastSyncAt)}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(snapshot.summary.systemStatus)}</span>
      </header>

      <section className="ux-workspace-actions" aria-label="Administration actions">
        <button type="button" data-action-id="sync-administration" disabled={runningAction === "sync-administration"} onClick={() => void runAdminAction("sync-administration", "Syncing administration...", "Administration synced", () => client.syncAdministration())}>{runningAction === "sync-administration" ? "Syncing administration..." : "Sync Administration"}</button>
        <button type="button" data-action-id="add-user" disabled={runningAction === "add-user"} onClick={() => { setShowAddUserDialog(true); setLastAction("Add user dialog opened"); }}>Add User</button>
        <button type="button" data-action-id="remove-user" disabled={runningAction === "remove-user"} onClick={() => void removeSelectedUser()}>{runningAction === "remove-user" ? "Removing user..." : "Remove User"}</button>
        <button type="button" data-action-id="refresh-administration" disabled={runningAction === "refresh-administration"} onClick={() => void refreshAdministration()}>{runningAction === "refresh-administration" ? "Refreshing administration..." : "Refresh"}</button>
        <button type="button" data-action-id="export-audit-log" disabled={runningAction === "export-audit-log"} onClick={() => void exportAuditLog()}>{runningAction === "export-audit-log" ? "Exporting audit log..." : "Export Audit Log"}</button>
      </section>

      <section className="ux-action-status">
        <span>{lastAction}</span>
        {selectedUser ? <span>Selected user {selectedUser.id}</span> : null}
        <span>Snapshot version {refreshCount}</span>
        <span>Last refreshed at {lastRefreshedAt ? formatTimestamp(lastRefreshedAt) : "Not refreshed this session"}</span>
        {auditExport ? <> <a data-action-id="download-audit-log" href={auditExport.href} download={auditExport.filename}>Download audit JSON</a></> : null}
      </section>

      {showAddUserDialog ? (
        <section className="ux-panel ux-admin-dialog" role="dialog" aria-modal="true" aria-labelledby="add-user-title" data-dialog-id="add-user">
          <div>
            <p className="ux-module-label">User Provisioning</p>
            <h2 id="add-user-title">Add User</h2>
            <p>Creates a deterministic UX-006 sample user through AdministrationUserManagementClient. Backend identity and authorization services remain authoritative.</p>
          </div>
          <div className="ux-workspace-actions">
            <button type="button" data-action-id="confirm-add-user" disabled={runningAction === "add-user"} onClick={() => void runAdminAction("add-user", "Adding user...", "User added", () => client.addUser())}>{runningAction === "add-user" ? "Adding user..." : "Confirm Add User"}</button>
            <button type="button" data-action-id="cancel-add-user" disabled={runningAction === "add-user"} onClick={() => { setShowAddUserDialog(false); setLastAction("Add user canceled"); }}>Cancel</button>
          </div>
        </section>
      ) : null}

      <section className="ux-workspace-grid">
        <article className="ux-panel ux-context-panel">
          <h2>User Management</h2>
          <section className="ux-action-status" aria-label="Administration refresh metadata">
            <span>Users {snapshot.users.length}</span>
            <span>Active {snapshot.users.filter((user) => user.status === "active").length}</span>
            <span>Suspended {snapshot.users.filter((user) => user.status === "suspended").length}</span>
            {refreshCount > 0 ? <span>Refreshed</span> : <span>Awaiting refresh</span>}
          </section>
          {selectedUser ? (
            <dl className="ux-inspector-list">
              <ContextItem label="Selected User">{selectedUser.name}</ContextItem>
              <ContextItem label="Selected Role">{selectedUser.role}</ContextItem>
              <ContextItem label="Selected Status">{formatStatusLabel(selectedUser.status)}</ContextItem>
            </dl>
          ) : null}
          <div className="ux-filter-grid">
            <label>Role Selector<select value={roleSelection} onChange={(event) => setRoleSelection(event.currentTarget.value)}>{snapshot.roles.map((role) => <option key={role.role} value={role.role}>{role.role}</option>)}</select></label>
          </div>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead><tr><th>User ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Active</th><th>Actions</th></tr></thead>
              <tbody>{snapshot.users.map((user) => <AdministrationUserRow client={client} isSelected={user.id === selectedUserId} key={user.id} onAction={runAdminAction} onView={viewUser} refreshed={refreshCount > 0} roleSelection={roleSelection} user={user} />)}</tbody>
            </table>
          </div>
        </article>

        <article className="ux-panel">
          <h2>Roles & Permissions</h2>
          <div className="ux-asset-grid">{snapshot.roles.map((role) => <RoleCard role={role} key={role.role} />)}</div>
        </article>
        <article className="ux-panel">
          <h2>Governance Controls</h2>
          <dl className="ux-inspector-list">
            <ContextItem label="Governance Mode">{snapshot.governanceControls.governanceMode}</ContextItem>
            <ContextItem label="Approval Policy">{snapshot.governanceControls.approvalPolicy}</ContextItem>
            <ContextItem label="Compliance Status">{snapshot.governanceControls.complianceStatus}</ContextItem>
            <ContextItem label="Override Policy">{snapshot.governanceControls.overridePolicy}</ContextItem>
            <ContextItem label="Risk Threshold">{snapshot.governanceControls.riskThreshold}</ContextItem>
          </dl>
        </article>
        <article className="ux-panel ux-context-panel">
          <h2>Audit Log</h2>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Resource</th><th>Severity</th><th>Status</th></tr></thead>
              <tbody>{visibleAudit.map((entry) => <tr key={entry.id}><td>{formatTimestamp(entry.timestamp)}</td><td>{entry.user}</td><td>{entry.action}</td><td>{entry.resource}</td><td>{formatStatusLabel(entry.severity)}</td><td>{formatStatusLabel(entry.status)}</td></tr>)}</tbody>
            </table>
          </div>
        </article>
        <article className="ux-panel">
          <h2>System Settings</h2>
          <dl className="ux-inspector-list">
            <ContextItem label="Environment">{snapshot.systemSettings.environment}</ContextItem>
            <ContextItem label="Release Version">{snapshot.systemSettings.releaseVersion}</ContextItem>
            <ContextItem label="Regression Baseline">{snapshot.systemSettings.regressionBaseline}</ContextItem>
            <ContextItem label="Monitoring Mode">{snapshot.systemSettings.monitoringMode}</ContextItem>
            <ContextItem label="Compliance Mode">{snapshot.systemSettings.complianceMode}</ContextItem>
          </dl>
        </article>
        <article className="ux-panel ux-boundary-panel">
          <h2>Backend Boundary</h2>
          <p>Authentication, authorization, governance, and security logic remain in backend services. UX-006 consumes administration outputs through AdministrationUserManagementClient.</p>
        </article>
      </section>
    </section>
  );
}

function AdministrationUserRow({ client, isSelected, onAction, onView, refreshed, roleSelection, user }: { client: AdministrationUserManagementClient; isSelected: boolean; onAction: (actionId: string, loadingLabel: string, completeLabel: string, run: () => Promise<AdministrationSnapshot>, reconcile?: (next: AdministrationSnapshot, current: AdministrationSnapshot) => AdministrationSnapshot) => Promise<void>; onView: (user: AdministrationUser) => void; refreshed: boolean; roleSelection: string; user: AdministrationUser }) {
  return (
    <tr aria-selected={isSelected} className={isSelected ? "ux-selected-row" : undefined} data-selected={isSelected ? "true" : "false"} onClick={() => onView(user)}>
      <td>{user.id}</td>
      <td><strong>{user.name}</strong></td>
      <td>{user.email}</td>
      <td>{user.role}</td>
      <td>{formatStatusLabel(user.status)} {refreshed ? <span className="ux-activity-badge">Refreshed</span> : null}</td>
      <td>{formatTimestamp(user.lastActiveAt)}</td>
      <td>
        <button type="button" data-action-id={`view-user-${user.id}`} onClick={() => onView(user)}>View</button>
        <button type="button" data-action-id={`change-role-${user.id}`} onClick={() => void onAction(`change-role-${user.id}`, "Changing role...", "Role changed", () => client.changeUserRole(user.id, roleSelection), (next, current) => updateAdministrationUser(next, current, user.id, { role: roleSelection }))}>Change Role</button>
        <button type="button" data-action-id={`toggle-user-${user.id}`} onClick={() => void onAction(`toggle-user-${user.id}`, "Updating user status...", "User status updated", () => client.toggleUserStatus(user.id), (next, current) => updateAdministrationUser(next, current, user.id, { status: user.status === "active" ? "suspended" : "active" }))}>{user.status === "active" ? "Suspend" : "Activate"}</button>
      </td>
    </tr>
  );
}

function RoleCard({ role }: { role: AdministrationRole }) {
  return <section className="ux-card ux-status-card"><span className="ux-status-pill">{role.accessLevel}</span><h3>{role.role}</h3><strong>{role.permissionCount} permissions</strong><p>{role.governanceScope}</p></section>;
}

type GenerationPreviewItem = {
  readonly id: string;
  readonly title: string;
  readonly status: string;
  readonly version: string;
  readonly lastGeneratedAt: string;
  readonly summary: string;
};

function createGenerationPreviewItem(item: GeneratedDocument | GeneratedAsset, displayTitle = item.title): GenerationPreviewItem {
  return { ...item, title: displayTitle };
}

function buildGenerationPreview(item: GeneratedDocument | GeneratedAsset, displayTitle = item.title): { readonly title: string; readonly details: readonly string[]; readonly payload: GenerationPreviewItem } {
  const payload = createGenerationPreviewItem(item, displayTitle);
  return {
    title: payload.title,
    payload,
    details: [
      `Title: ${payload.title}`,
      `ID: ${payload.id}`,
      `Version: ${payload.version}`,
      `Status: ${payload.status}`,
      `Last Generated: ${formatTimestamp(payload.lastGeneratedAt)}`,
      `Summary: ${payload.summary}`,
    ],
  };
}

function getGenerationPreviewForAction(actionId: string, snapshot: DocumentationGenerationSnapshot, currentPreviewTitle: string): { readonly title: string; readonly details: readonly string[] } | null {
  if (actionId === "generate-documentation") return buildGenerationPreview(snapshot.documentation[0]);
  if (actionId === "generate-patent") return buildGenerationPreview(snapshot.patent[0]);
  if (actionId === "generate-research") return buildGenerationPreview(snapshot.researchPaper[0]);
  if (actionId === "refresh-docgen" && currentPreviewTitle !== "No preview selected") {
    const selectedTitle = currentPreviewTitle.replace("Preview ready: ", "");
    const documentItem = snapshot.documentation.find((item) => item.title === selectedTitle);
    if (documentItem) return buildGenerationPreview(documentItem);
    const patentItem = snapshot.patent.find((item) => item.title === selectedTitle);
    if (patentItem) return buildGenerationPreview(patentItem);
    const researchItem = snapshot.researchPaper.find((item) => item.title === selectedTitle);
    if (researchItem) return buildGenerationPreview(researchItem);
  }
  return null;
}

function getGenerationActionMessage(actionId: string, completeLabel: string, timestamp: string): string {
  if (actionId === "generate-documentation") return `Documentation package generated from existing DOC modules. Updated ${formatTimestamp(timestamp)}`;
  if (actionId === "generate-patent") return `Patent package generated from existing PAT modules. Updated ${formatTimestamp(timestamp)}`;
  if (actionId === "generate-research") return `Research paper package generated from existing RP modules. Updated ${formatTimestamp(timestamp)}`;
  if (actionId === "refresh-docgen") return `Generator refreshed. Choose a package type to generate preview again. Updated ${formatTimestamp(timestamp)}`;
  return `${completeLabel} at ${formatTimestamp(timestamp)}`;
}

function DocumentationGenerationPage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: DocumentationGenerationSnapshot;
  client: DocumentationGenerationClient;
  onSnapshotChange: Dispatch<SetStateAction<DocumentationGenerationSnapshot | null>>;
}) {
  const savedGeneratorState = useMemo(() => loadDocumentationGeneratorState(), []);
  const [runningAction, setRunningAction] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState("Documentation generator ready");
  const [generatedPackage, setGeneratedPackage] = useState<"documentation" | "patent" | "research" | null>(savedGeneratorState?.generatedPackage ?? null);
  const [previewTitle, setPreviewTitle] = useState(savedGeneratorState?.previewTitle ?? "No preview selected");
  const [previewDetails, setPreviewDetails] = useState<readonly string[]>(savedGeneratorState?.previewDetails ?? []);
  const [downloadPackage, setDownloadPackage] = useState<{ href: string; filename: string } | null>(null);
  const visibleActivity = getVisibleGenerationActivity(snapshot.activity);

  async function runGeneration(actionId: string, loadingLabel: string, completeLabel: string, run: () => Promise<DocumentationGenerationSnapshot>, previewOverride?: { readonly item: GeneratedDocument | GeneratedAsset; readonly category: "documentation" | "patent" | "research" }) {
    setRunningAction(actionId);
    setLastAction(loadingLabel);
    try {
      const next = await run();
      setRunningAction(null);
      if (actionId === "refresh-docgen") {
        setGeneratedPackage(null);
        setPreviewTitle("No preview selected");
        setPreviewDetails([]);
        saveDocumentationGeneratorState({ generatedPackage: null, previewTitle: "No preview selected", previewDetails: [] });
        setLastAction(getGenerationActionMessage(actionId, completeLabel, next.summary.lastGenerationAt));
        onSnapshotChange({ ...next, activity: mergeGenerationActivity(next.activity, snapshot.activity) });
        return;
      }
      const generatedPreview = previewOverride ? buildGenerationPreview(previewOverride.item) : getGenerationPreviewForAction(actionId, next, previewTitle);
      if (generatedPreview) {
        setPreviewTitle(`Preview ready: ${generatedPreview.title}`);
        setPreviewDetails(generatedPreview.details);
      }
      const nextGeneratedPackage = previewOverride?.category ?? (actionId === "generate-documentation" ? "documentation" : actionId === "generate-patent" ? "patent" : actionId === "generate-research" ? "research" : generatedPackage);
      setGeneratedPackage(nextGeneratedPackage);
      saveDocumentationGeneratorState({
        generatedPackage: nextGeneratedPackage,
        previewTitle: generatedPreview ? `Preview ready: ${generatedPreview.title}` : previewTitle,
        previewDetails: generatedPreview ? generatedPreview.details : previewDetails,
      });
      setLastAction(getGenerationActionMessage(actionId, completeLabel, next.summary.lastGenerationAt));
      onSnapshotChange({ ...next, activity: mergeGenerationActivity(next.activity, snapshot.activity) });
    } catch {
      setRunningAction(null);
      setLastAction(`${completeLabel} failed safely. Backend generation logic was not moved into the UI.`);
    }
  }

  function previewAsset(item: GeneratedDocument | GeneratedAsset, category: "documentation" | "patent" | "research", displayTitle = item.title) {
    const preview = buildGenerationPreview(item, displayTitle);
    setGeneratedPackage(category);
    setPreviewTitle(`Preview ready: ${displayTitle}`);
    setPreviewDetails(preview.details);
    saveDocumentationGeneratorState({ generatedPackage: category, previewTitle: `Preview ready: ${displayTitle}`, previewDetails: preview.details });
    setLastAction(`Preview opened for ${displayTitle}`);
  }

  function downloadAsset(title: string, payload: unknown) {
    const report = JSON.stringify(payload, null, 2);
    setDownloadPackage({ href: `data:application/json;charset=utf-8,${encodeURIComponent(report)}`, filename: `${title.toLowerCase().replaceAll(" ", "-")}.json` });
    setLastAction(`Download ready for ${title}`);
  }

  async function exportPackage() {
    setRunningAction("export-package");
    setLastAction("Exporting package...");
    try {
      const next = await client.exportPackage();
      const packagePayload = { ...next, exportedAt: next.summary.lastGenerationAt };
      setDownloadPackage({ href: `data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(packagePayload, null, 2))}`, filename: "ux-005-documentation-package.json" });
      setRunningAction(null);
      setLastAction(`Package exported at ${formatTimestamp(next.summary.lastGenerationAt)}`);
      onSnapshotChange({ ...next, activity: mergeGenerationActivity(next.activity, snapshot.activity) });
    } catch {
      setRunningAction(null);
      setLastAction("Package export failed safely.");
    }
  }

  return (
    <section className="ux-docgen" aria-labelledby="docgen-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-005</p>
          <h1 id="docgen-title">Documentation / Patent / Research Generator</h1>
          <div className="ux-workspace-meta">
            <span>Generator Status {formatStatusLabel(snapshot.summary.generatorStatus)}</span>
            <span>{snapshot.summary.currentProject}</span>
            <span>Last Generation {formatTimestamp(snapshot.summary.lastGenerationAt)}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(snapshot.summary.generatorStatus)}</span>
      </header>

      <section className="ux-workspace-actions" aria-label="Documentation generation actions">
        <button type="button" data-action-id="generate-documentation" disabled={runningAction === "generate-documentation"} onClick={() => void runGeneration("generate-documentation", "Generating documentation...", "Documentation generated", () => client.generateDocumentation())}>{runningAction === "generate-documentation" ? "Generating documentation..." : "Generate Documentation"}</button>
        <button type="button" data-action-id="generate-patent" disabled={runningAction === "generate-patent"} onClick={() => void runGeneration("generate-patent", "Generating patent package...", "Patent generated", () => client.generatePatent())}>{runningAction === "generate-patent" ? "Generating patent..." : "Generate Patent"}</button>
        <button type="button" data-action-id="generate-research" disabled={runningAction === "generate-research"} onClick={() => void runGeneration("generate-research", "Generating research paper...", "Research generated", () => client.generateResearchPaper())}>{runningAction === "generate-research" ? "Generating research..." : "Generate Research Paper"}</button>
        <button type="button" data-action-id="refresh-docgen" disabled={runningAction === "refresh-docgen"} onClick={() => void runGeneration("refresh-docgen", "Refreshing generator...", "Generator refreshed", () => client.refresh())}>{runningAction === "refresh-docgen" ? "Refreshing..." : "Refresh"}</button>
        <button type="button" data-action-id="export-package" disabled={runningAction === "export-package"} onClick={() => void exportPackage()}>{runningAction === "export-package" ? "Exporting package..." : "Export Package"}</button>
      </section>

      <section className="ux-action-status">
        <span>{lastAction}</span>
        <span>{previewTitle}</span>
        {generatedPackage ? <span>Generated package selected: {formatStatusLabel(generatedPackage)}</span> : <span>No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview.</span>}
        {downloadPackage ? <> <a data-action-id="download-docgen-package" href={downloadPackage.href} download={downloadPackage.filename}>Download generated JSON</a></> : null}
      </section>

      <section className="ux-workspace-grid">
        {generatedPackage ? null : (
          <article className="ux-panel ux-context-panel">
            <h2>Package Preview</h2>
            <p>No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview.</p>
          </article>
        )}
        {generatedPackage ? <GeneratedPackagePanel generatedPackage={generatedPackage} previewDetails={previewDetails} previewTitle={previewTitle} snapshot={snapshot} onDownload={downloadAsset} onPreview={previewAsset} /> : null}
        <article className="ux-panel ux-context-panel">
          <h2>Generation Activity</h2>
          <ol className="ux-timeline">
            {visibleActivity.map((event) => (
              <li data-status="complete" key={event.id}>
                <div>
                  <strong>{event.title}</strong>
                  <span>{formatTimestamp(event.timestamp)}</span>
                  <p>{event.detail}</p>
                </div>
                <span className="ux-activity-badge">{formatStatusLabel(event.type)}</span>
              </li>
            ))}
          </ol>
        </article>
        <article className="ux-panel ux-boundary-panel">
          <h2>Backend Boundary</h2>
          <p>Documentation, patent, and research outputs are consumed through DocumentationGenerationClient. Backend generation logic remains frozen and authoritative.</p>
        </article>
      </section>
    </section>
  );
}

function GeneratedPackagePanel({
  generatedPackage,
  onDownload,
  onPreview,
  previewDetails,
  previewTitle,
  snapshot,
}: {
  generatedPackage: "documentation" | "patent" | "research";
  onDownload: (title: string, payload: unknown) => void;
  onPreview: (item: GeneratedDocument | GeneratedAsset, category: "documentation" | "patent" | "research", displayTitle?: string) => void;
  previewDetails: readonly string[];
  previewTitle: string;
  snapshot: DocumentationGenerationSnapshot;
}) {
  const packageItems = getGeneratedPackageItems(snapshot, generatedPackage);
  return (
    <article className="ux-panel ux-context-panel">
      <h2>Generated Package</h2>
      <div className="ux-doc-list">
        {packageItems.map(({ displayTitle, item }) => (
          <section className="ux-session-row" key={`${generatedPackage}-${item.id}`}>
            <strong>{displayTitle}</strong>
            <span>{formatStatusLabel(item.status)}</span>
            <span>{item.version}</span>
            <span>{formatTimestamp(item.lastGeneratedAt)}</span>
            <button type="button" data-action-id={`preview-${generatedPackage}-${item.id}`} onClick={() => onPreview(item, generatedPackage, displayTitle)}>Preview</button>
            <button type="button" data-action-id={`download-${generatedPackage}-${item.id}`} onClick={() => onDownload(displayTitle, createGenerationPreviewItem(item, displayTitle))}>Download</button>
          </section>
        ))}
      </div>
      <section className="ux-panel ux-boundary-panel">
        <h3>Package Item Preview</h3>
        <strong>{previewTitle}</strong>
        {previewDetails.length > 0 ? (
          <ul>{previewDetails.map((detail) => <li key={detail}>{detail}</li>)}</ul>
        ) : (
          <p>Select Preview to display structured DOC/PAT/RP package content.</p>
        )}
      </section>
    </article>
  );
}

function getGeneratedPackageItems(snapshot: DocumentationGenerationSnapshot, generatedPackage: "documentation" | "patent" | "research"): readonly { readonly displayTitle: string; readonly item: GeneratedDocument | GeneratedAsset }[] {
  if (generatedPackage === "documentation") {
    return snapshot.documentation.map((item) => ({ displayTitle: item.title, item }));
  }
  if (generatedPackage === "research") {
    return snapshot.researchPaper.map((item) => ({ displayTitle: item.title, item }));
  }
  const patentDraft = snapshot.patent.find((item) => item.id === "patent-draft");
  const claims = snapshot.patent.find((item) => item.id === "patent-claims");
  const novelty = snapshot.patent.find((item) => item.id === "patent-prior-art") ?? snapshot.patent.find((item) => item.id === "patent-figures");
  return [
    patentDraft ? { displayTitle: "Patent Draft", item: patentDraft } : null,
    claims ? { displayTitle: "Claims", item: claims } : null,
    novelty ? { displayTitle: "Novelty Analysis", item: novelty } : null,
  ].filter((item): item is { readonly displayTitle: string; readonly item: GeneratedAsset } => item !== null);
}

function ExplainabilityAnalyticsPage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: ExplainabilityAnalyticsSnapshot;
  client: ExplainabilityAnalyticsClient;
  onSnapshotChange: Dispatch<SetStateAction<ExplainabilityAnalyticsSnapshot | null>>;
}) {
  const [actionState, setActionState] = useState<"ready" | "generating" | "refreshing" | "exporting" | "exported">("ready");
  const [lastAction, setLastAction] = useState("Explainability ready");
  const [exportedReport, setExportedReport] = useState<{ href: string; filename: string } | null>(null);
  const [explanationGenerated, setExplanationGenerated] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);
  const [analyticsLastRefreshedAt, setAnalyticsLastRefreshedAt] = useState<string | null>(null);
  const [analyticsRefreshNotice, setAnalyticsRefreshNotice] = useState("Analytics snapshot ready.");

  async function generateExplanation() {
    try {
      setActionState("generating");
      setLastAction("Generating explanation...");
      const next = await client.generateExplanation();
      setActionState("ready");
      setExplanationGenerated(true);
      setLastAction(`Explanation completed. Explanation generated from current decision snapshot. Last generated ${formatTimestamp(next.summary.lastAnalysisAt)}`);
      onSnapshotChange({ ...next, timeline: mergeExplainabilityTimeline(next.timeline, snapshot.timeline) });
    } catch {
      setActionState("ready");
      setLastAction("Explanation failed");
    }
  }

  async function refreshAnalytics() {
    try {
      setActionState("refreshing");
      setLastAction("Refreshing analytics...");
      const previousAnalytics = JSON.stringify(snapshot.analytics);
      const next = await client.refreshAnalytics();
      const nextRefreshCount = refreshCount + 1;
      const analyticsUnchanged = previousAnalytics === JSON.stringify(next.analytics);
      setActionState("ready");
      setRefreshCount(nextRefreshCount);
      setAnalyticsLastRefreshedAt(next.summary.lastAnalysisAt);
      setAnalyticsRefreshNotice(analyticsUnchanged ? "Values unchanged after adapter snapshot reload." : "Updated from adapter snapshot.");
      setLastAction(`Current v1.0.0 adapter snapshot reloaded. No external enterprise data source is connected. Snapshot version ${nextRefreshCount}. Last refreshed ${formatTimestamp(next.summary.lastAnalysisAt)}`);
      onSnapshotChange({ ...next, reasoning: snapshot.reasoning, timeline: mergeExplainabilityTimeline(next.timeline, snapshot.timeline) });
    } catch {
      setActionState("ready");
      setLastAction("Analytics refresh failed");
    }
  }

  function exportReport() {
    setActionState("exporting");
    const exportedAt = getNextExplainabilityActionTimestamp(snapshot.summary.lastAnalysisAt);
    const nextSnapshot: ExplainabilityAnalyticsSnapshot = {
      ...snapshot,
      summary: { ...snapshot.summary, status: "exported", lastAnalysisAt: exportedAt },
      timeline: appendExplainabilityActivity(snapshot.timeline, "report-exported", "Report Exported", "recommendation", exportedAt, "Current UX explainability report exported as JSON."),
    };
    const report = JSON.stringify(nextSnapshot, null, 2);
    const filename = `${snapshot.summary.decisionId}-explainability-report.json`;
    setExportedReport({ href: `data:application/json;charset=utf-8,${encodeURIComponent(report)}`, filename });
    if (typeof document !== "undefined") {
      const blob = new Blob([report], { type: "application/json" });
      const url = typeof URL.createObjectURL === "function" ? URL.createObjectURL(blob) : "";
      const isJsdom = typeof window !== "undefined" && window.navigator.userAgent.toLowerCase().includes("jsdom");
      if (url && !isJsdom) {
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = filename;
        anchor.dataset.exportReport = "true";
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        if (typeof URL.revokeObjectURL === "function") URL.revokeObjectURL(url);
      }
    }
    onSnapshotChange(nextSnapshot);
    setActionState("exported");
    setLastAction(`Report exported at ${formatTimestamp(exportedAt)}`);
  }

  const visibleTimeline = getVisibleExplainabilityTimeline(snapshot.timeline);

  return (
    <section className="ux-xai" aria-labelledby="xai-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-004</p>
          <h1 id="xai-title">Explainability & Analytics Dashboard</h1>
          <div className="ux-workspace-meta">
            <span>{snapshot.summary.decisionId}</span>
            <span>Confidence {Math.round(snapshot.summary.confidence * 100)}%</span>
            <span>Analyzed {formatTimestamp(snapshot.summary.lastAnalysisAt)}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(snapshot.summary.status)}</span>
      </header>
      <section className="ux-workspace-actions">
        <button type="button" data-action-id="generate-explanation" disabled={actionState === "generating"} onClick={() => void generateExplanation()}>{actionState === "generating" ? "Generating explanation..." : "Generate Explanation"}</button>
        <button type="button" data-action-id="refresh-analytics" disabled={actionState === "refreshing"} onClick={() => void refreshAnalytics()}>{actionState === "refreshing" ? "Refreshing analytics..." : "Refresh Analytics"}</button>
        <button type="button" data-action-id="export-report" disabled={actionState === "exporting"} onClick={exportReport}>{actionState === "exporting" ? "Exporting report..." : "Export Report"}</button>
      </section>
      <section className="ux-action-status">
        <span>{lastAction}</span>
        <span>Snapshot version {refreshCount}</span>
        {exportedReport ? <> <a data-action-id="download-export-report" href={exportedReport.href} download={exportedReport.filename}>Download JSON report</a></> : null}
      </section>
      <section className="ux-grid ux-xai-summary">{snapshot.summary.cards.map((card) => <SummaryCardView card={card} key={card.id} />)}</section>
      <section className="ux-workspace-grid">
        <article className="ux-panel ux-context-panel"><h2>Decision Reasoning</h2><ReasoningPanel generated={explanationGenerated} snapshot={snapshot} /></article>
        <article className="ux-panel ux-context-panel"><h2>Feature Importance</h2><div className="ux-feature-list">{snapshot.featureImportance.map((item) => <FeatureBar item={item} key={item.feature} />)}</div></article>
        <AnalyticsDashboardPanel lastRefreshedAt={analyticsLastRefreshedAt} notice={analyticsRefreshNotice} refreshCount={refreshCount} snapshot={snapshot} />
        <article className="ux-panel"><h2>Explainability Timeline</h2><ol className="ux-timeline">{visibleTimeline.map((event) => <li data-status="complete" key={event.id}><div><strong>{event.title}</strong><span>{formatTimestamp(event.timestamp)}</span><p>{event.detail}</p></div><span className="ux-activity-badge">{formatStatusLabel(event.type)}</span></li>)}</ol></article>
        <article className="ux-panel"><h2>Recommendation Summary</h2><dl className="ux-inspector-list"><ContextItem label="Primary">{snapshot.recommendation.primaryRecommendation}</ContextItem><ContextItem label="Alternative">{snapshot.recommendation.alternativeRecommendation}</ContextItem><ContextItem label="Confidence">{Math.round(snapshot.recommendation.confidence * 100)}%</ContextItem><ContextItem label="Reason">{snapshot.recommendation.reason}</ContextItem><ContextItem label="Business Impact">{snapshot.recommendation.businessImpact}</ContextItem></dl></article>
      </section>
    </section>
  );
}

function AnalyticsDashboardPanel({
  lastRefreshedAt,
  notice,
  refreshCount,
  snapshot,
}: {
  lastRefreshedAt: string | null;
  notice: string;
  refreshCount: number;
  snapshot: ExplainabilityAnalyticsSnapshot;
}) {
  return (
    <article className="ux-panel ux-context-panel">
      <div className="ux-section-heading">
        <h2>Analytics Dashboard</h2>
        <span className="ux-status-pill">Snapshot version {refreshCount}</span>
      </div>
      <section className="ux-action-status" aria-label="Analytics refresh metadata">
        <span data-status-id="last-action">Last refreshed {lastRefreshedAt ? formatTimestamp(lastRefreshedAt) : "Not refreshed this session"}</span>
        <span>{notice}</span>
      </section>
      <div className="ux-analytics-grid">
        {snapshot.analytics.map((group) => (
          <section data-refresh-version={refreshCount} key={group.id}>
            <h3>{group.title}</h3>
            {group.metrics.map((card) => <SummaryCardView card={card} key={card.id} />)}
            {refreshCount > 0 ? <span className="ux-activity-badge">Updated from snapshot</span> : null}
          </section>
        ))}
      </div>
    </article>
  );
}

function SummaryCardView({ card }: { card: SummaryCard }) {
  return <article className="ux-card ux-status-card"><span className="ux-status-pill">{card.status}</span><h3>{card.title}</h3><strong>{card.value}</strong><p>{card.detail}</p></article>;
}

function ReasoningPanel({ generated, snapshot }: { generated: boolean; snapshot: ExplainabilityAnalyticsSnapshot }) {
  if (!generated) {
    return <p>No explanation generated yet. Click Generate Explanation to reveal rationale, governance explanation, sensitivity notes, and recommendation explanation from the current adapter snapshot.</p>;
  }
  const groups = [["Top Factors", snapshot.reasoning.topFactors], ["Positive Factors", snapshot.reasoning.positiveFactors], ["Negative Factors", snapshot.reasoning.negativeFactors], ["Risk Factors", snapshot.reasoning.riskFactors], ["Constraints", snapshot.reasoning.constraints]] as const;
  return <div className="ux-reasoning-grid">{groups.map(([title, items]) => <section key={title}><h3>{title}</h3><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></section>)}<section><h3>Decision Path Summary</h3><p>{snapshot.reasoning.decisionPathSummary}</p></section></div>;
}

function FeatureBar({ item }: { item: FeatureImportanceItem }) {
  return <section className="ux-feature-row"><div><strong>{item.feature}</strong><span>{item.impact} impact - {item.direction}</span></div><div className="ux-feature-bar"><span style={{ width: `${Math.round(item.weight * 100)}%` }} /></div><strong>{Math.round(item.confidence * 100)}%</strong></section>;
}

function KnowledgeGraphExplorerPage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: KnowledgeGraphSnapshot;
  client: KnowledgeGraphProvenanceClient;
  onSnapshotChange: Dispatch<SetStateAction<KnowledgeGraphSnapshot | null>>;
}) {
  const [selectedNodeId, setSelectedNodeId] = useState(snapshot.nodes[0]?.id ?? "");
  const [selectedEdgeId, setSelectedEdgeId] = useState(snapshot.edges[0]?.id ?? "");
  const [filters, setFilters] = useState<GraphFilters>(snapshot.filters);
  const [lastGraphAction, setLastGraphAction] = useState("Graph explorer ready");
  const [highlightedProvenanceNodeIds, setHighlightedProvenanceNodeIds] = useState<readonly string[]>([]);
  const [highlightedProvenanceEdgeIds, setHighlightedProvenanceEdgeIds] = useState<readonly string[]>([]);
  const [graphRefreshVersion, setGraphRefreshVersion] = useState(0);
  const [selectedEdgeSelectedAt, setSelectedEdgeSelectedAt] = useState<string | undefined>(undefined);
  const [provenanceLoadedAt, setProvenanceLoadedAt] = useState<string | undefined>(undefined);
  const filteredGraph = useMemo(() => filterKnowledgeGraph(snapshot, filters), [snapshot, filters]);
  const selectedNode = filteredGraph.nodes.find((node) => node.id === selectedNodeId);
  const selectedEdge = filteredGraph.edges.find((edge) => edge.id === selectedEdgeId);

  function restoreDefaultGraph(nextSnapshot: KnowledgeGraphSnapshot, message: string) {
    const visibleFilters: GraphFilters = { ...nextSnapshot.filters, nodeType: "all", relationshipType: "all", governanceStatus: "all", timePeriod: "all", provenanceSource: "all" };
    setFilters(visibleFilters);
    setSelectedNodeId(nextSnapshot.nodes[0]?.id ?? "");
    setSelectedEdgeId(nextSnapshot.edges[0]?.id ?? "");
    setSelectedEdgeSelectedAt(undefined);
    setProvenanceLoadedAt(undefined);
    setHighlightedProvenanceNodeIds([]);
    setHighlightedProvenanceEdgeIds([]);
    saveGraphPreferences(visibleFilters, nextSnapshot.nodes[0]?.id ?? "", nextSnapshot.edges[0]?.id ?? "");
    setLastGraphAction(message);
    onSnapshotChange(nextSnapshot);
  }

  useEffect(() => {
    if (filteredGraph.nodes.length > 0 && !filteredGraph.nodes.some((node) => node.id === selectedNodeId)) {
      setSelectedNodeId(filteredGraph.nodes[0].id);
    }
    if (filteredGraph.nodes.length === 0 && selectedNodeId) setSelectedNodeId("");
    if (filteredGraph.edges.length > 0 && selectedEdgeId && !filteredGraph.edges.some((edge) => edge.id === selectedEdgeId)) {
      setSelectedEdgeId(filteredGraph.edges[0].id);
    }
    if (filteredGraph.edges.length === 0 && selectedEdgeId) setSelectedEdgeId("");
  }, [filteredGraph.edges, filteredGraph.nodes, selectedEdgeId, selectedNodeId]);

  async function refreshGraph() {
    const next = await client.refreshGraph();
    const refreshedGraph = filterKnowledgeGraph(next, filters);
    if (refreshedGraph.nodes.length === 0) {
      restoreDefaultGraph(next, "Graph refreshed from current adapter snapshot.");
      return;
    }
    setSelectedNodeId(refreshedGraph.nodes.some((node) => node.id === selectedNodeId) ? selectedNodeId : refreshedGraph.nodes[0]?.id ?? "");
    setSelectedEdgeId(refreshedGraph.edges.some((edge) => edge.id === selectedEdgeId) ? selectedEdgeId : "");
    setSelectedEdgeSelectedAt(undefined);
    setProvenanceLoadedAt(undefined);
    setHighlightedProvenanceNodeIds([]);
    setHighlightedProvenanceEdgeIds([]);
    setGraphRefreshVersion((current) => current + 1);
    setLastGraphAction("Graph refreshed from current adapter snapshot.");
    onSnapshotChange(next);
  }

  async function loadProvenance() {
    const next = await client.loadDecisionProvenance("DEC-2026-001");
    const visibleFilters: GraphFilters = { ...next.filters, nodeType: "all", relationshipType: "all", governanceStatus: "all", timePeriod: "all", provenanceSource: "all" };
    const provenanceGraph = filterKnowledgeGraph(next, visibleFilters);
    if (provenanceGraph.nodes.length === 0) {
      restoreDefaultGraph(next, "Full provenance path loaded from current graph snapshot.");
      return;
    }
    const provenanceEdgeIds = provenanceGraph.edges.filter((edge) => edge.provenanceReference.startsWith("PROV-")).map((edge) => edge.id);
    const provenanceNodeIds = Array.from(new Set(provenanceGraph.edges
      .filter((edge) => provenanceEdgeIds.includes(edge.id))
      .flatMap((edge) => [edge.sourceNodeId, edge.targetNodeId])));
    setFilters(visibleFilters);
    setSelectedNodeId(provenanceGraph.nodes.find((node) => node.type === "decision")?.id ?? provenanceGraph.nodes[0]?.id ?? "");
    setSelectedEdgeId(provenanceGraph.edges.find((edge) => edge.provenanceReference === "PROV-RNK-001")?.id ?? provenanceGraph.edges[0]?.id ?? "");
    setSelectedEdgeSelectedAt(next.summary.lastRefreshedAt);
    setProvenanceLoadedAt(next.summary.lastRefreshedAt);
    setHighlightedProvenanceNodeIds(provenanceNodeIds);
    setHighlightedProvenanceEdgeIds(provenanceEdgeIds);
    setLastGraphAction(provenanceEdgeIds.length > 1 ? "Full provenance path loaded from current graph snapshot." : "Only partial provenance is available in this snapshot.");
    onSnapshotChange(next);
  }

  function loadPreferences() {
    const preferences = loadGraphPreferences();
    if (!preferences) {
      setLastGraphAction("No saved graph preferences found. Current graph view preserved.");
      return;
    }
    const preferredGraph = filterKnowledgeGraph(snapshot, preferences.filters);
    if (preferredGraph.nodes.length === 0) {
      restoreDefaultGraph(snapshot, "Saved preferences were invalid or too restrictive. Default graph restored.");
      return;
    }
    setFilters(preferences.filters);
    setHighlightedProvenanceNodeIds([]);
    setHighlightedProvenanceEdgeIds([]);
    setSelectedEdgeSelectedAt(undefined);
    setProvenanceLoadedAt(undefined);
    setSelectedNodeId(preferredGraph.nodes.some((node) => node.id === preferences.selectedNodeId) ? preferences.selectedNodeId ?? "" : preferredGraph.nodes[0]?.id ?? "");
    setSelectedEdgeId(preferredGraph.edges.some((edge) => edge.id === preferences.selectedEdgeId) ? preferences.selectedEdgeId ?? "" : preferredGraph.edges[0]?.id ?? "");
    setLastGraphAction("Saved graph preferences loaded.");
  }

  function resetView() {
    restoreDefaultGraph(snapshot, `Graph view reset to default adapter snapshot. Selected node ${snapshot.nodes[0]?.label ?? "none"}.`);
  }

  function updateFilter(name: keyof GraphFilters, value: string) {
    setFilters((current) => {
      const next = { ...current, [name]: value };
      setHighlightedProvenanceNodeIds([]);
      setHighlightedProvenanceEdgeIds([]);
      setSelectedEdgeSelectedAt(undefined);
      setProvenanceLoadedAt(undefined);
      saveGraphPreferences(next, selectedNodeId, selectedEdgeId);
      return next;
    });
    setLastGraphAction("Graph filters applied to current adapter snapshot.");
  }

  function selectNode(nodeId: string) {
    setSelectedNodeId(nodeId);
    saveGraphPreferences(filters, nodeId, selectedEdgeId);
  }

  function selectEdge(edgeId: string) {
    setSelectedEdgeId(edgeId);
    setSelectedEdgeSelectedAt(new Date().toISOString());
    setProvenanceLoadedAt(undefined);
    saveGraphPreferences(filters, selectedNodeId, edgeId);
  }

  return (
    <section className="ux-kg" aria-labelledby="kg-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-003</p>
          <h1 id="kg-title">{snapshot.summary.title}</h1>
          <div className="ux-workspace-meta">
            <span>{snapshot.summary.selectedSource}</span>
            <span>{snapshot.summary.nodeCount} nodes</span>
            <span>{snapshot.summary.edgeCount} edges</span>
            <span>Refreshed {formatTimestamp(snapshot.summary.lastRefreshedAt)}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(snapshot.summary.status)}</span>
      </header>
      <section className="ux-workspace-actions" aria-label="Graph actions">
        <button type="button" data-action-id="refresh-graph" onClick={() => void refreshGraph()}>Refresh Graph</button>
        <button type="button" data-action-id="load-provenance" onClick={() => void loadProvenance()}>Load Provenance</button>
        <button type="button" data-action-id="load-graph-preferences" onClick={loadPreferences}>Load Preferences</button>
        <button type="button" data-action-id="reset-graph-view" onClick={resetView}>Reset View</button>
      </section>
      <section className="ux-action-status">
        <span>{lastGraphAction}</span>
        <span>Visible graph: {filteredGraph.nodes.length} nodes / {filteredGraph.edges.length} edges</span>
        <span data-graph-refresh-version={`refresh-${graphRefreshVersion}`}>Graph refresh {graphRefreshVersion}</span>
      </section>
      <section className="ux-kg-grid">
        <article className="ux-panel ux-kg-graph-panel">
          <h2>Graph Visualization</h2>
          <GraphCanvas nodes={filteredGraph.nodes} edges={filteredGraph.edges} selectedNodeId={selectedNodeId} selectedEdgeId={selectedEdgeId} highlightedNodeIds={highlightedProvenanceNodeIds} highlightedEdgeIds={highlightedProvenanceEdgeIds} onSelectNode={selectNode} onSelectEdge={selectEdge} />
        </article>
        <article className="ux-panel">
          <h2>Graph Filters</h2>
          <GraphFiltersPanel filters={filters} onChange={updateFilter} />
        </article>
        <article className="ux-panel"><NodeInspector node={selectedNode} /></article>
        <article className="ux-panel"><EdgeInspector edge={selectedEdge} nodes={filteredGraph.nodes} selectedAt={selectedEdgeSelectedAt} provenanceLoadedAt={provenanceLoadedAt} /></article>
        <article className="ux-panel ux-kg-timeline-panel">
          <h2>Provenance Timeline</h2>
          <ol className="ux-timeline">
            {snapshot.timeline.map((event) => (
              <li data-status="complete" key={event.id}>
                <div>
                  <strong>{event.title}</strong>
                  <span>{formatTimestamp(event.timestamp)} - {event.sourceModule}</span>
                  <p>{event.detail}</p>
                </div>
                <span className="ux-activity-badge">{formatStatusLabel(event.type)}</span>
              </li>
            ))}
          </ol>
        </article>
      </section>
    </section>
  );
}

function GraphCanvas({
  nodes,
  edges,
  selectedNodeId,
  selectedEdgeId,
  highlightedNodeIds,
  highlightedEdgeIds,
  onSelectNode,
  onSelectEdge,
}: {
  nodes: readonly UxGraphNode[];
  edges: readonly UxGraphEdge[];
  selectedNodeId: string;
  selectedEdgeId: string;
  highlightedNodeIds: readonly string[];
  highlightedEdgeIds: readonly string[];
  onSelectNode: (id: string) => void;
  onSelectEdge: (id: string) => void;
}) {
  return (
    <div className="ux-graph-canvas" aria-label="Knowledge graph visualization">
      {nodes.length === 0 ? <p className="ux-placeholder-message">No graph data matches the active filters.</p> : null}
      <svg viewBox="0 0 760 240" role="img" aria-label="Decision provenance graph">
        {edges.map((edge) => {
          const source = nodes.find((node) => node.id === edge.sourceNodeId);
          const target = nodes.find((node) => node.id === edge.targetNodeId);
          if (!source || !target) return null;
          return (
            <g key={edge.id} data-edge-id={edge.id} data-provenance-highlight={highlightedEdgeIds.includes(edge.id) ? "true" : "false"}>
              <line x1={source.x} y1={source.y} x2={target.x} y2={target.y} className={`ux-graph-edge ${edge.id === selectedEdgeId && highlightedEdgeIds.length === 0 ? "is-selected" : ""} ${highlightedEdgeIds.includes(edge.id) ? "is-provenance-path" : ""}`} onClick={() => onSelectEdge(edge.id)} />
              <text x={(source.x + target.x) / 2} y={(source.y + target.y) / 2 - 8} className="ux-graph-edge-label" onClick={() => onSelectEdge(edge.id)}>{edge.label}</text>
            </g>
          );
        })}
        {nodes.map((node) => (
          <g key={node.id} onClick={() => onSelectNode(node.id)} data-node-id={node.id} data-provenance-highlight={highlightedNodeIds.includes(node.id) ? "true" : "false"}>
            <circle cx={node.x} cy={node.y} r="22" className={`ux-graph-node ${node.id === selectedNodeId ? "is-selected" : ""} ${highlightedNodeIds.includes(node.id) ? "is-provenance-path" : ""}`} />
            <text x={node.x} y={node.y + 40} textAnchor="middle" className="ux-graph-node-label">{node.label}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function GraphFiltersPanel({ filters, onChange }: { filters: GraphFilters; onChange: (name: keyof GraphFilters, value: string) => void }) {
  const fields: Array<[keyof GraphFilters, readonly string[]]> = [
    ["nodeType", ["all", "decision", "evidence", "criterion", "governance", "recommendation"]],
    ["relationshipType", ["all", "supports", "derived-from", "governed-by", "ranked-by", "traces-to"]],
    ["confidenceRange", ["0.80-1.00", "0.60-1.00", "0.90-1.00"]],
    ["governanceStatus", ["all", "approved", "review", "pending"]],
    ["timePeriod", ["last-24h", "last-7d", "all"]],
    ["provenanceSource", ["all", "DKE Evidence Audit", "DIE Evaluation", "DIE Governance"]],
  ];
  return <div className="ux-filter-grid">{fields.map(([name, options]) => <label key={name}>{formatStatusLabel(name)}<select data-filter-name={name} value={filters[name]} onChange={(event) => onChange(name, event.currentTarget.value)}>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select></label>)}</div>;
}

function NodeInspector({ node }: { node: UxGraphNode | undefined }) {
  if (!node) return <><h2>Node Inspector</h2><p>No node selected.</p></>;
  return <><h2>Node Inspector</h2><dl className="ux-inspector-list"><ContextItem label="Node ID">{node.id}</ContextItem><ContextItem label="Label">{node.label}</ContextItem><ContextItem label="Type">{node.type}</ContextItem><ContextItem label="Confidence">{Math.round(node.confidence * 100)}%</ContextItem><ContextItem label="Source Module">{node.sourceModule}</ContextItem><ContextItem label="Governance Status">{node.governanceStatus}</ContextItem><ContextItem label="Related Decisions">{node.relatedDecisions.join(", ")}</ContextItem><ContextItem label="Metadata">{Object.entries(node.metadata).map(([key, value]) => `${key}: ${value}`).join("; ")}</ContextItem></dl></>;
}

function EdgeInspector({ edge, nodes, selectedAt, provenanceLoadedAt }: { edge: UxGraphEdge | undefined; nodes: readonly UxGraphNode[]; selectedAt?: string; provenanceLoadedAt?: string }) {
  if (!edge) return <><h2>Edge Inspector</h2><p>No edge selected.</p></>;
  const source = nodes.find((node) => node.id === edge.sourceNodeId)?.label ?? edge.sourceNodeId;
  const target = nodes.find((node) => node.id === edge.targetNodeId)?.label ?? edge.targetNodeId;
  return <><h2>Edge Inspector</h2><dl className="ux-inspector-list"><ContextItem label="Selection Highlight">Blue indicates the selected edge.</ContextItem><ContextItem label="Edge ID">{edge.id}</ContextItem><ContextItem label="Source Node">{source}</ContextItem><ContextItem label="Target Node">{target}</ContextItem><ContextItem label="Relationship">{edge.relationshipType}</ContextItem><ContextItem label="Confidence">{Math.round(edge.confidence * 100)}%</ContextItem><ContextItem label="Provenance Reference">{edge.provenanceReference}</ContextItem><ContextItem label="Source Timestamp">{formatTimestamp(edge.timestamp)}</ContextItem>{selectedAt ? <ContextItem label="Selected At">{formatTimestamp(selectedAt)}</ContextItem> : null}{provenanceLoadedAt ? <ContextItem label="Provenance Loaded At">{formatTimestamp(provenanceLoadedAt)}</ContextItem> : null}</dl></>;
}

function alignEvaluationResultsToAlternatives(
  results: readonly EvaluationResult[],
  alternatives: readonly DecisionAlternative[],
): readonly EvaluationResult[] {
  const byAlternative = new Map(results.map((result) => [result.alternativeId, result]));
  return alternatives.map((alternative, index) => {
    const existing = byAlternative.get(alternative.id);
    if (existing) return existing;
    const score = Math.max(60, 84 - index * 6);
    return {
      alternativeId: alternative.id,
      score,
      confidence: Math.max(0.72, 0.9 - index * 0.04),
      criteria: [
        { name: "Strategic fit", score, weight: 0.3 },
        { name: "Operational readiness", score: Math.max(60, score - 2), weight: 0.25 },
        { name: "Governance fit", score: Math.min(95, score + 3), weight: 0.25 },
        { name: "Time-to-value", score: Math.max(58, score - 4), weight: 0.2 },
      ],
      strengths: [`${alternative.title} is available for backend evaluation review`],
      weaknesses: ["Detailed backend evaluation criteria are pending for this demo option"],
      warnings: ["UI fallback aligns result coverage only; backend decision logic remains authoritative"],
    };
  });
}

function alignRankingResultsToAlternatives(
  results: readonly RankingResult[],
  alternatives: readonly DecisionAlternative[],
): readonly RankingResult[] {
  const byAlternative = new Map(results.map((result) => [result.alternativeId, result]));
  return alternatives.map((alternative, index) => {
    const existing = byAlternative.get(alternative.id);
    return {
      rank: index + 1,
      alternativeId: alternative.id,
      alternativeTitle: alternative.title,
      score: existing?.score ?? Math.max(60, 84 - index * 6),
      explanationSummary: existing?.explanationSummary ?? `${alternative.title} is included in the visible workspace ranking set.`,
      recommended: existing?.recommended ?? index === 0,
    };
  });
}

function DecisionWorkspacePage({
  snapshot,
  client,
  onSnapshotChange,
}: {
  snapshot: DecisionWorkspaceSnapshot;
  client: DecisionWorkspaceClient;
  onSnapshotChange: Dispatch<SetStateAction<DecisionWorkspaceSnapshot | null>>;
}) {
  const { summary, context } = snapshot;
  const [evaluationStatus, setEvaluationStatus] = useState<ActionStatus>("ready");
  const [rankingStatus, setRankingStatus] = useState<ActionStatus>("ready");
  const [workspaceStatus, setWorkspaceStatus] = useState<WorkspaceActionStatus>("idle");
  const [lastAction, setLastAction] = useState<ActionNotice | null>(null);
  const [evaluationRevealed, setEvaluationRevealed] = useState(false);
  const [rankingRevealed, setRankingRevealed] = useState(false);
  const [decisionHistory, setDecisionHistory] = useState<readonly DecisionHistoryItem[]>([]);
  const visibleTimeline = getVisibleTimeline(snapshot.timeline);

  useEffect(() => {
    let active = true;
    async function refreshHistory() {
      if (!client.listSavedDecisionWorkspaces) {
        if (active) setDecisionHistory([]);
        return;
      }
      try {
        const history = await client.listSavedDecisionWorkspaces();
        if (active) setDecisionHistory(history);
      } catch {
        if (active) setDecisionHistory([]);
      }
    }
    void refreshHistory();
    return () => {
      active = false;
    };
  }, [client, snapshot.summary.decisionId, snapshot.summary.updatedAt]);

  async function refreshDecisionHistory() {
    if (!client.listSavedDecisionWorkspaces) {
      setDecisionHistory([]);
      return;
    }
    try {
      setDecisionHistory(await client.listSavedDecisionWorkspaces());
    } catch {
      setDecisionHistory([]);
    }
  }

  async function createNewDecision() {
    setWorkspaceStatus("creating");
    setLastAction({ kind: "info", message: "Creating draft workspace..." });
    try {
      const fallbackClient = createDecisionWorkspaceClient();
      const nextSnapshot = client.createDraftWorkspace
        ? await client.createDraftWorkspace()
        : await fallbackClient.createDraftWorkspace?.();
      if (!nextSnapshot) throw new Error("Draft workspace adapter did not return a snapshot.");
      const completedAt = new Date().toISOString();
      setEvaluationStatus("ready");
      setRankingStatus("ready");
      setEvaluationRevealed(false);
      setRankingRevealed(false);
      setWorkspaceStatus("idle");
      setLastAction({ kind: "success", message: `New decision workspace created at ${formatTimestamp(completedAt)}` });
      onSnapshotChange({
        ...nextSnapshot,
        timeline: appendWorkspaceActivity(nextSnapshot.timeline, "new-decision-action", "New decision workspace created", completedAt, "current"),
      });
      await refreshDecisionHistory();
    } catch {
      setWorkspaceStatus("error");
      setLastAction({ kind: "error", message: "New decision workspace could not be created safely." });
    }
  }

  async function loadDecision(sessionId?: string) {
    setWorkspaceStatus("loading");
    setLastAction({ kind: "info", message: "Loading decision workspace..." });
    try {
      const fallbackClient = createDecisionWorkspaceClient();
      const nextSnapshot = client.loadDecisionWorkspace
        ? await client.loadDecisionWorkspace(sessionId)
        : await fallbackClient.loadDecisionWorkspace?.(sessionId);
      if (!nextSnapshot) throw new Error("Load workspace adapter did not return a snapshot.");
      const completedAt = new Date().toISOString();
      setEvaluationStatus("ready");
      setRankingStatus("ready");
      setEvaluationRevealed(false);
      setRankingRevealed(false);
      setWorkspaceStatus("idle");
      setLastAction({ kind: "success", message: `Decision workspace loaded at ${formatTimestamp(completedAt)}` });
      onSnapshotChange({
        ...nextSnapshot,
        timeline: appendWorkspaceActivity(nextSnapshot.timeline, "load-decision-action", "Decision workspace loaded", completedAt, "current"),
      });
      await refreshDecisionHistory();
    } catch {
      setWorkspaceStatus("error");
      setLastAction({ kind: "error", message: "Decision workspace could not be loaded safely." });
    }
  }

  async function runEvaluation() {
    setEvaluationStatus("running");
    setLastAction({ kind: "info", message: "Running evaluation..." });
    try {
      const evaluationResults = await client.runEvaluation();
      const completedAt = new Date().toISOString();
      setEvaluationStatus("completed");
      setEvaluationRevealed(true);
      setLastAction({ kind: "success", message: `Evaluation completed at ${formatTimestamp(completedAt)}` });
      onSnapshotChange((current) =>
        current
          ? {
              ...current,
              evaluationResults: alignEvaluationResultsToAlternatives(evaluationResults, current.alternatives),
              timeline: appendWorkspaceActivity(current.timeline, "evaluation-action", "Evaluation completed from workspace action", completedAt),
            }
          : current,
      );
    } catch {
      setEvaluationStatus("error");
      setLastAction({ kind: "error", message: "Evaluation failed safely. No backend state was changed by the UI." });
    }
  }

  async function runRanking() {
    setRankingStatus("running");
    setLastAction({ kind: "info", message: "Running ranking..." });
    try {
      const rankingResults = await client.runRanking();
      const completedAt = new Date().toISOString();
      setRankingStatus("completed");
      setRankingRevealed(true);
      setLastAction({ kind: "success", message: `Ranking completed at ${formatTimestamp(completedAt)}` });
      onSnapshotChange((current) =>
        current
          ? {
              ...current,
              rankingResults: alignRankingResultsToAlternatives(rankingResults, current.alternatives),
              timeline: appendWorkspaceActivity(current.timeline, "ranking-action", "Ranking completed from workspace action", completedAt),
            }
          : current,
      );
    } catch {
      setRankingStatus("error");
      setLastAction({ kind: "error", message: "Ranking failed safely. No backend state was changed by the UI." });
    }
  }

  return (
    <section className="ux-decision-workspace" aria-labelledby="decision-workspace-title">
      <header className="ux-workspace-header">
        <div>
          <p className="ux-module-label">UX-002</p>
          <h1 id="decision-workspace-title">{summary.workspaceTitle}</h1>
          <div className="ux-workspace-meta">
            <span>{summary.decisionId}</span>
            <span>{summary.sessionId}</span>
            <span>Updated {formatTimestamp(summary.updatedAt)}</span>
          </div>
        </div>
        <span className="ux-status-pill">{formatStatusLabel(summary.status)}</span>
      </header>

      <section className="ux-workspace-actions" aria-label="Decision workspace actions">
        <button type="button" data-action-id="new-decision" disabled={workspaceStatus === "creating"} onClick={() => void createNewDecision()}>
          {workspaceStatus === "creating" ? "Creating..." : "New Decision"}
        </button>
        <button type="button" data-action-id="load-decision" disabled={workspaceStatus === "loading"} onClick={() => void loadDecision()}>
          {workspaceStatus === "loading" ? "Loading..." : "Load Decision"}
        </button>
        <button type="button" data-action-id="run-evaluation" disabled={evaluationStatus === "running"} onClick={() => void runEvaluation()}>
          {evaluationStatus === "running" ? "Running evaluation..." : "Run Evaluation"}
        </button>
        <button type="button" data-action-id="run-ranking" disabled={rankingStatus === "running"} onClick={() => void runRanking()}>
          {rankingStatus === "running" ? "Running ranking..." : "Run Ranking"}
        </button>
      </section>

      <section className="ux-action-status" aria-label="Decision action status">
        <span data-status-id="evaluation-status">{formatActionStatus("Evaluation", evaluationStatus)}</span>
        <span data-status-id="ranking-status">{formatActionStatus("Ranking", rankingStatus)}</span>
        <span data-status-id="last-action">{lastAction ? lastAction.message : "No workspace action has been run in this preview session."}</span>
      </section>

      <section className="ux-workspace-grid">
        <article className="ux-panel ux-context-panel">
          <h2>Decision Context</h2>
          <dl className="ux-context-grid">
            <ContextItem label="Objective">{context.objective}</ContextItem>
            <ContextItem label="Domain">{context.domain}</ContextItem>
            <ContextItem label="Risk Preference">{context.riskPreference}</ContextItem>
            <ContextItem label="Governance Mode">{context.governanceMode}</ContextItem>
            <ContextItem label="Constraints"><InlineList items={context.constraints} /></ContextItem>
            <ContextItem label="Stakeholders"><InlineList items={context.stakeholders} /></ContextItem>
          </dl>
        </article>

        <article className="ux-panel">
          <h2>Decision Sessions</h2>
          <div className="ux-session-list">
            {snapshot.sessions.map((session) => (
              <section className="ux-session-row" key={session.id}>
                <strong>{session.title}</strong>
                <span>{session.id}</span>
                <span>{session.status}</span>
                <span>{formatTimestamp(session.updatedAt)}</span>
              </section>
            ))}
          </div>
        </article>

        <article className="ux-panel">
          <h2>Decision History</h2>
          {decisionHistory.length > 0 ? (
            <div className="ux-session-list">
              {decisionHistory.map((item) => (
                <section className="ux-session-row" data-history-decision-id={item.decisionId} key={item.decisionId}>
                  <strong>{item.title}</strong>
                  <span>{item.decisionId}</span>
                  <span>{formatStatusLabel(item.status)}</span>
                  <span>{item.domain}</span>
                  <span>{formatTimestamp(item.updatedAt)}</span>
                  <button type="button" data-history-load-id={item.decisionId} onClick={() => void loadDecision(item.sessionId)}>
                    Load
                  </button>
                </section>
              ))}
            </div>
          ) : (
            <p>No saved frontend decision history yet. Create a new decision to save a local UX snapshot.</p>
          )}
        </article>

        <article className="ux-panel">
          <h2>Alternatives</h2>
          <div className="ux-table-wrap">
            <table className="ux-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Expected Impact</th>
                  <th>Risk</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {snapshot.alternatives.map((alternative) => (
                  <tr data-alternative-id={alternative.id} key={alternative.id}>
                    <td>{alternative.id}</td>
                    <td>
                      <strong>{alternative.title}</strong>
                      <span>{alternative.summary}</span>
                    </td>
                    <td>{alternative.expectedImpact}</td>
                    <td>{alternative.riskLevel}</td>
                    <td>{alternative.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="ux-panel">
          <h2>Evaluation Results</h2>
          {evaluationRevealed ? (
            <>
              <p className="ux-result-snapshot-label">Current backend/fallback result snapshot revealed by Run Evaluation</p>
              <div className="ux-result-grid">
                {snapshot.evaluationResults.map((result) => (
                  <EvaluationResultCard result={result} key={result.alternativeId} />
                ))}
              </div>
            </>
          ) : (
            <p>No evaluation run yet. Click Run Evaluation to reveal backend-produced scoring, criteria analysis, strengths, weaknesses, and warnings.</p>
          )}
        </article>

        <article className="ux-panel">
          <h2>Ranking</h2>
          {rankingRevealed ? (
            <>
              <p className="ux-result-snapshot-label">Current backend/fallback result snapshot revealed by Run Ranking</p>
              <div className="ux-ranking-list">
                {snapshot.rankingResults.map((result) => (
                  <section className="ux-ranking-row" data-ranking-id={result.alternativeId} key={result.alternativeId}>
                    <span className="ux-rank-number">{result.rank}</span>
                    <div>
                      <h3>{result.alternativeTitle}</h3>
                      <p>{result.explanationSummary}</p>
                    </div>
                    <strong>{result.score}</strong>
                    {result.recommended ? <span className="ux-status-pill">Recommended</span> : null}
                  </section>
                ))}
              </div>
            </>
          ) : (
            <p>No ranking run yet. Click Run Ranking to reveal backend-produced ranked alternatives and recommendation output.</p>
          )}
        </article>

        <article className="ux-panel">
          <h2>Workspace Activity</h2>
          <ol className="ux-timeline">
            {visibleTimeline.map((event) => (
              <li data-status={event.status} key={event.id}>
                <div>
                  <strong>{event.label}</strong>
                  <span>{formatTimestamp(event.timestamp)}</span>
                </div>
                <span className="ux-activity-badge">{formatStatusLabel(event.status)}</span>
              </li>
            ))}
          </ol>
        </article>

        <article className="ux-panel ux-boundary-panel">
          <h2>Backend Boundary</h2>
          <p>Evaluation and ranking outputs are consumed through DecisionWorkspaceClient. Backend modules remain frozen and authoritative.</p>
        </article>
      </section>
    </section>
  );
}

type ActionStatus = "ready" | "running" | "completed" | "error";
type WorkspaceActionStatus = "idle" | "creating" | "loading" | "error";

interface ActionNotice {
  readonly kind: "info" | "success" | "error";
  readonly message: string;
}

function formatActionStatus(label: "Evaluation" | "Ranking", status: ActionStatus): string {
  if (status === "ready") return `${label} ready`;
  if (status === "running") return `Running ${label.toLowerCase()}...`;
  if (status === "completed") return `${label} completed`;
  return `${label} failed`;
}

function appendWorkspaceActivity(
  timeline: readonly WorkspaceTimelineEvent[],
  id: string,
  label: string,
  timestamp: string,
  status: WorkspaceTimelineEvent["status"] = "complete",
): readonly WorkspaceTimelineEvent[] {
  const nextEvent: WorkspaceTimelineEvent = { id: `${id}-${timestamp}`, label, status, timestamp };
  const deduplicated = timeline.filter((event) => !event.id.startsWith(`${id}-`) && event.label !== label);
  return [nextEvent, ...deduplicated].slice(0, 8);
}

function getVisibleTimeline(timeline: readonly WorkspaceTimelineEvent[]): readonly WorkspaceTimelineEvent[] {
  return [...timeline]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function getVisibleGenerationActivity(activity: readonly GenerationActivity[]): readonly GenerationActivity[] {
  return [...activity]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function mergeGenerationActivity(
  nextActivity: readonly GenerationActivity[],
  currentActivity: readonly GenerationActivity[],
): readonly GenerationActivity[] {
  const seen = new Set<string>();
  const merged: GenerationActivity[] = [];
  for (const event of [...nextActivity, ...currentActivity]) {
    const key = `${event.id}:${event.title}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(event);
  }
  return getVisibleGenerationActivity(merged);
}

function getVisibleAuditLog(auditLog: readonly AuditLogEntry[]): readonly AuditLogEntry[] {
  return [...auditLog]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function mergeAuditLog(nextAuditLog: readonly AuditLogEntry[], currentAuditLog: readonly AuditLogEntry[]): readonly AuditLogEntry[] {
  const seen = new Set<string>();
  const merged: AuditLogEntry[] = [];
  for (const event of [...nextAuditLog, ...currentAuditLog]) {
    const key = `${event.id}:${event.action}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(event);
  }
  return getVisibleAuditLog(merged);
}

function mergeAdministrationUsers(nextUsers: readonly AdministrationUser[], currentUsers: readonly AdministrationUser[]): readonly AdministrationUser[] {
  const merged = new Map<string, AdministrationUser>();
  for (const user of currentUsers) merged.set(user.id, user);
  for (const user of nextUsers) {
    if (!merged.has(user.id)) merged.set(user.id, user);
  }
  return [...merged.values()];
}

function mergeAdministrationSnapshot(next: AdministrationSnapshot, current: AdministrationSnapshot): AdministrationSnapshot {
  return {
    ...next,
    users: mergeAdministrationUsers(next.users, current.users),
    auditLog: mergeAuditLog(next.auditLog, current.auditLog),
  };
}

function reconcileAdministrationRemoval(next: AdministrationSnapshot, current: AdministrationSnapshot, removedUserId: string): AdministrationSnapshot {
  return {
    ...next,
    users: next.users.filter((user) => user.id !== removedUserId),
    auditLog: mergeAuditLog(next.auditLog, current.auditLog),
  };
}

function removeAdministrationUserLocally(snapshot: AdministrationSnapshot, selectedUser: AdministrationUser): AdministrationSnapshot {
  const timestamp = new Date().toISOString();
  const audit: AuditLogEntry = {
    id: `AUD-REMOVE-${selectedUser.id}-${timestamp}`,
    timestamp,
    user: "UX Administrator",
    action: "User removed",
    resource: `${selectedUser.id} ${selectedUser.name}`,
    severity: "warning",
    status: "complete",
  };
  return {
    ...snapshot,
    summary: { ...snapshot.summary, systemStatus: "user-removed", lastSyncAt: timestamp },
    users: snapshot.users.filter((user) => user.id !== selectedUser.id),
    auditLog: [audit, ...snapshot.auditLog],
  };
}

function updateAdministrationUser(
  next: AdministrationSnapshot,
  current: AdministrationSnapshot,
  userId: string,
  updates: Partial<Pick<AdministrationUser, "role" | "status">>,
): AdministrationSnapshot {
  const merged = mergeAdministrationSnapshot(next, current);
  return {
    ...merged,
    users: merged.users.map((user) => user.id === userId ? { ...user, ...updates, lastActiveAt: next.summary.lastSyncAt } : user),
  };
}

function getVisibleIntegrationActivity(activity: readonly IntegrationActivity[]): readonly IntegrationActivity[] {
  return [...activity]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function mergeIntegrationActivity(nextActivity: readonly IntegrationActivity[], currentActivity: readonly IntegrationActivity[]): readonly IntegrationActivity[] {
  const seen = new Set<string>();
  const merged: IntegrationActivity[] = [];
  for (const event of [...nextActivity, ...currentActivity]) {
    const key = `${event.id}:${event.action}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(event);
  }
  return getVisibleIntegrationActivity(merged);
}

function mergeById<T extends { readonly id: string }>(nextItems: readonly T[], currentItems: readonly T[]): readonly T[] {
  const merged = new Map<string, T>();
  for (const item of currentItems) merged.set(item.id, item);
  for (const item of nextItems) merged.set(item.id, item);
  return [...merged.values()];
}

function mergeEnterpriseIntegrationSnapshot(next: EnterpriseIntegrationSnapshot, current: EnterpriseIntegrationSnapshot): EnterpriseIntegrationSnapshot {
  return {
    ...next,
    connectors: mergeById(next.connectors, current.connectors),
    webhooks: mergeById(next.webhooks, current.webhooks),
    activity: mergeIntegrationActivity(next.activity, current.activity),
  };
}

function appendExplainabilityActivity(
  timeline: readonly ExplainabilityTimelineEvent[],
  id: string,
  title: string,
  type: ExplainabilityTimelineEvent["type"],
  timestamp: string,
  detail: string,
): readonly ExplainabilityTimelineEvent[] {
  const nextEvent: ExplainabilityTimelineEvent = { id: `${id}-${timestamp}`, title, type, timestamp, detail };
  const deduplicated = timeline.filter((event) => !event.id.startsWith(`${id}-`) && event.title !== title);
  return getVisibleExplainabilityTimeline([nextEvent, ...deduplicated]);
}

function getVisibleExplainabilityTimeline(timeline: readonly ExplainabilityTimelineEvent[]): readonly ExplainabilityTimelineEvent[] {
  return [...timeline]
    .sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp))
    .slice(0, 8);
}

function mergeExplainabilityTimeline(
  nextTimeline: readonly ExplainabilityTimelineEvent[],
  currentTimeline: readonly ExplainabilityTimelineEvent[],
): readonly ExplainabilityTimelineEvent[] {
  const seen = new Set<string>();
  const merged: ExplainabilityTimelineEvent[] = [];
  for (const event of [...nextTimeline, ...currentTimeline]) {
    const key = `${event.id}:${event.title}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(event);
  }
  return getVisibleExplainabilityTimeline(merged);
}

function getNextExplainabilityActionTimestamp(referenceTimestamp: string): string {
  const now = Date.now();
  const reference = Date.parse(referenceTimestamp);
  if (Number.isNaN(reference) || now > reference) return new Date(now).toISOString();
  return new Date(reference + 5 * 60 * 1000).toISOString();
}

function formatStatusLabel(value: string): string {
  return value
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function ContextItem({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

function InlineList({ items }: { items: readonly string[] }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function EvaluationResultCard({ result }: { result: EvaluationResult }) {
  return (
    <section className="ux-result-card" data-evaluation-id={result.alternativeId}>
      <header>
        <strong>{result.alternativeId}</strong>
        <span>{result.score} score</span>
        <span>{Math.round(result.confidence * 100)}% confidence</span>
      </header>
      <ul>
        {result.criteria.map((criterion) => (
          <li key={criterion.name}>
            {criterion.name}: {criterion.score} ({Math.round(criterion.weight * 100)}% weight)
          </li>
        ))}
      </ul>
      <p>
        <strong>Strengths:</strong> {result.strengths.join(", ")}
      </p>
      <p>
        <strong>Weaknesses:</strong> {result.weaknesses.join(", ")}
      </p>
      <p>
        <strong>Warnings:</strong> {result.warnings.join(", ")}
      </p>
    </section>
  );
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(date).replace(" am", " AM").replace(" pm", " PM");
}

function DashboardPage({ viewModel }: { viewModel: DashboardViewModel }) {
  return (
    <section className="ux-dashboard" aria-labelledby="dashboard-title">
      <header className="ux-page-header">
        <div>
          <p className="ux-module-label">UX-001</p>
          <h1 id="dashboard-title">{viewModel.title}</h1>
          <p>{viewModel.subtitle}</p>
        </div>
      </header>
      <section className="ux-baseline" aria-label="Regression baseline">
        <strong>
          {viewModel.regressionBaseline.passing} / {viewModel.regressionBaseline.total}
        </strong>
        <span>Regression tests passing</span>
      </section>
      <section className="ux-grid ux-status-grid" aria-label="Platform status">
        {viewModel.statusCards.map((card) => (
          <article className="ux-card ux-status-card" data-card-id={card.id} key={card.id}>
            <span className="ux-status-pill">{card.status}</span>
            <h3>{card.title}</h3>
            <p>{card.detail}</p>
          </article>
        ))}
      </section>
      <section className="ux-release-tags" aria-label="Current release tags">
        <h2>Current Release Tags</h2>
        <ul>
          {viewModel.releaseTags.map((tag) => (
            <li key={tag}>{tag}</li>
          ))}
        </ul>
      </section>
      <section className="ux-grid ux-mechanism-grid" aria-label="Frozen architecture mechanisms">
        <h2>Frozen Architecture Mechanisms</h2>
        {viewModel.mechanisms.map((card) => (
          <article className="ux-card ux-mechanism-card" data-mechanism-id={card.id} key={card.id}>
            <h3>{card.title}</h3>
            <p>{card.description}</p>
            <small>{card.backendModule}</small>
          </article>
        ))}
      </section>
    </section>
  );
}

function PlaceholderPage({ entry }: { entry: NavigationEntry }) {
  return (
    <section className="ux-placeholder" aria-label={entry.label} data-ux-module={entry.uxModule}>
      <p className="ux-module-label">{entry.uxModule}</p>
      <h1>{entry.label}</h1>
      <p className="ux-placeholder-purpose">{entry.purpose}</p>
      <p className="ux-placeholder-message">Coming in future UX implementation</p>
      <p className="ux-boundary-note">Backend modules remain frozen. This UI will consume existing backend APIs only.</p>
    </section>
  );
}
