import {
  createBackendStatusClient,
  createAdministrationUserManagementClient,
  createDecisionWorkspaceClient,
  createDocumentationGenerationClient,
  createEnterpriseIntegrationClient,
  createExplainabilityAnalyticsClient,
  createKnowledgeGraphProvenanceClient,
  createDashboardViewModel,
  ENTERPRISE_SHELL_CSS,
  getPreviewNavigationHash,
  getPreviewRoutePath,
  getRouteMap,
  renderEnterpriseDashboardShell,
  resolveShellRoute,
  UX_ROADMAP_NAVIGATION,
  type BackendStatusClient,
  type AdministrationUserManagementClient,
  type DecisionWorkspaceClient,
  type DocumentationGenerationClient,
  type EnterpriseIntegrationClient,
  type ExplainabilityAnalyticsClient,
  type KnowledgeGraphProvenanceClient,
  ADMINISTRATION_STORAGE_KEY,
  DECISION_WORKSPACE_STORAGE_KEY,
  ENTERPRISE_INTEGRATION_STORAGE_KEY,
  PROVENANCE_TIMELINE_STORAGE_KEY,
} from "../index.js";

type TestCase = { name: string; run: () => Promise<void> | void };

const tests: TestCase[] = [];

function test(name: string, run: TestCase["run"]): void {
  tests.push({ name, run });
}

function assert(condition: unknown, message: string): void {
  if (!condition) throw new Error(message);
}

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (actual !== expected) throw new Error(`${message}. Expected ${String(expected)}, got ${String(actual)}.`);
}

function installMockLocalStorage(seed: Record<string, string> = {}): { restore: () => void; storage: Storage } {
  const previous = Object.getOwnPropertyDescriptor(globalThis, "localStorage");
  const values = new Map(Object.entries(seed));
  const storage: Storage = {
    get length() {
      return values.size;
    },
    clear() {
      values.clear();
    },
    getItem(key: string) {
      return values.get(key) ?? null;
    },
    key(index: number) {
      return [...values.keys()][index] ?? null;
    },
    removeItem(key: string) {
      values.delete(key);
    },
    setItem(key: string, value: string) {
      values.set(key, value);
    },
  };
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: storage });
  return {
    storage,
    restore() {
      if (previous) Object.defineProperty(globalThis, "localStorage", previous);
      else Reflect.deleteProperty(globalThis, "localStorage");
    },
  };
}

test("shell renders successfully", async () => {
  const html = await renderEnterpriseDashboardShell();
  assert(html.includes("ux-shell"), "Shell container should render.");
  assert(html.includes("ux-sidebar"), "Sidebar should render.");
  assert(html.includes("ux-topbar"), "Top header should render.");
  assert(html.includes("ux-main"), "Main content area should render.");
});

test("navigation entries render", async () => {
  const html = await renderEnterpriseDashboardShell();
  for (const entry of UX_ROADMAP_NAVIGATION) {
    assert(html.includes(`data-route-id="${entry.id}"`), `Navigation entry should render: ${entry.id}`);
    assert(html.includes(entry.label), `Navigation label should render: ${entry.label}`);
  }
});

test("dashboard status cards render", async () => {
  const dashboard = await createDashboardViewModel(createBackendStatusClient());
  assertEqual(dashboard.statusCards.length, 10, "Dashboard should expose all official status cards.");
  const html = await renderEnterpriseDashboardShell();
  assert(html.includes("Backend Platform"), "Backend status card should render.");
  assert(html.includes("Commercial Release"), "Commercial release status card should render.");
  assert(html.includes("606 / 606"), "Regression baseline should render.");
  assert(html.includes("v1.0.2-backend-complete"), "Current release tags should render.");
});

test("architecture mechanism cards render", async () => {
  const dashboard = await createDashboardViewModel(createBackendStatusClient());
  assertEqual(dashboard.mechanisms.length, 8, "Dashboard should expose all frozen architecture mechanisms.");
  const html = await renderEnterpriseDashboardShell();
  assert(html.includes("Decision Provenance Graph"), "Provenance mechanism should render.");
  assert(html.includes("Enterprise Decision Orchestration Fabric"), "Enterprise orchestration mechanism should render.");
});

test("API adapter boundary exists", async () => {
  const calls: string[] = [];
  const client: BackendStatusClient = {
    async getPlatformStatus() {
      calls.push("getPlatformStatus");
      return createBackendStatusClient().getPlatformStatus();
    },
  };
  await renderEnterpriseDashboardShell({}, client);
  assertEqual(calls.join(","), "getPlatformStatus", "Shell should obtain dashboard data through the backend status client.");
});

test("placeholder routes render", async () => {
  const client = createBackendStatusClient();
  for (const entry of UX_ROADMAP_NAVIGATION.filter((item) => item.status === "placeholder")) {
    const route = await resolveShellRoute(entry.path, client);
    assertEqual(route.title, entry.label, `Placeholder route title should match ${entry.id}.`);
    assert(route.contentHtml.includes(`data-ux-module="${entry.uxModule}"`), `Placeholder should identify roadmap module for ${entry.id}.`);
    assert(route.contentHtml.includes(entry.purpose), `Placeholder should render purpose for ${entry.id}.`);
    assert(route.contentHtml.includes("Coming in future UX implementation"), `Placeholder should render future UX message for ${entry.id}.`);
    assert(route.contentHtml.includes("Backend modules are frozen"), `Placeholder should render backend boundary note for ${entry.id}.`);
  }
  assert(getRouteMap().includes("/platform-integration"), "Route map should include platform integration.");
});

test("decision workspace route renders UX-002 workspace sections", async () => {
  const route = await resolveShellRoute("/decision-workspace", createBackendStatusClient(), createDecisionWorkspaceClient());
  assertEqual(route.title, "Decision Workspace", "Decision workspace route title should resolve.");
  assert(route.contentHtml.includes("UX-002"), "Decision workspace should identify UX-002.");
  assert(route.contentHtml.includes("Decision Context"), "Decision context panel should render.");
  assert(route.contentHtml.includes("Alternatives"), "Alternatives panel should render.");
  assert(route.contentHtml.includes("Evaluation Results"), "Evaluation results panel should render.");
  assert(route.contentHtml.includes("Ranking"), "Ranking panel should render.");
  assert(route.contentHtml.includes("Workspace Activity"), "Timeline should render.");
  assert(route.contentHtml.includes("Run Evaluation"), "Run Evaluation action should render.");
  assert(route.contentHtml.includes("Run Ranking"), "Run Ranking action should render.");
});

test("knowledge graph route renders UX-003 explorer sections", async () => {
  const route = await resolveShellRoute("/knowledge-graph", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient());
  assertEqual(route.title, "Knowledge Graph & Provenance", "Knowledge graph route title should resolve.");
  assert(route.contentHtml.includes("UX-003"), "Knowledge graph route should identify UX-003.");
  assert(route.contentHtml.includes("Graph Visualization"), "Graph panel should render.");
  assert(route.contentHtml.includes("Graph Filters"), "Filter panel should render.");
  assert(route.contentHtml.includes("Node Inspector"), "Node inspector should render.");
  assert(route.contentHtml.includes("Edge Inspector"), "Edge inspector should render.");
  assert(route.contentHtml.includes("Provenance Timeline"), "Timeline should render.");
});

test("knowledge graph route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const fallback = createKnowledgeGraphProvenanceClient();
  const client: KnowledgeGraphProvenanceClient = {
    async getGraphSummary() {
      calls.push("getGraphSummary");
      return fallback.getGraphSummary();
    },
    async getGraphData() {
      calls.push("getGraphData");
      return fallback.getGraphData();
    },
    async getProvenanceTimeline() {
      calls.push("getProvenanceTimeline");
      return fallback.getProvenanceTimeline();
    },
    getNodeDetails: (nodeId) => fallback.getNodeDetails(nodeId),
    getEdgeDetails: (edgeId) => fallback.getEdgeDetails(edgeId),
    refreshGraph: () => fallback.refreshGraph(),
    loadDecisionProvenance: (decisionId) => fallback.loadDecisionProvenance(decisionId),
  };
  await resolveShellRoute("/knowledge-graph", createBackendStatusClient(), createDecisionWorkspaceClient(), client);
  assertEqual(calls.join(","), "getGraphSummary,getGraphData,getProvenanceTimeline", "Knowledge graph route should consume data through KnowledgeGraphProvenanceClient.");
});

test("knowledge graph provenance timeline persists after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createKnowledgeGraphProvenanceClient();
    const loaded = await client.loadDecisionProvenance("DEC-2026-001");
    assert(loaded.timeline.some((event) => event.title === "Decision created"), "Load Provenance should create the full provenance event timeline.");
    assert(localStorage.storage.getItem(PROVENANCE_TIMELINE_STORAGE_KEY)?.includes("Recommendation generated"), "Loaded provenance timeline should be saved to localStorage.");

    const recreated = createKnowledgeGraphProvenanceClient();
    const timeline = await recreated.getProvenanceTimeline();
    const summary = await recreated.getGraphSummary();
    assert(timeline.some((event) => event.title === "Evidence linked"), "Client recreation should reload saved provenance timeline.");
    assertEqual(summary.status, "provenance-loaded", "Client recreation should preserve provenance loaded status.");
  } finally {
    localStorage.restore();
  }
});

test("knowledge graph provenance timeline falls back safely when storage is invalid", async () => {
  const localStorage = installMockLocalStorage({ [PROVENANCE_TIMELINE_STORAGE_KEY]: "{invalid provenance timeline" });
  try {
    const client = createKnowledgeGraphProvenanceClient();
    const timeline = await client.getProvenanceTimeline();
    const graphData = await client.getGraphData();
    assert(timeline.some((event) => event.title === "Evidence extraction event"), "Invalid saved timeline should fall back to base timeline.");
    assertEqual(graphData.nodes.length, 5, "Invalid saved timeline should not blank the graph.");
  } finally {
    localStorage.restore();
  }
});

test("explainability route renders UX-004 dashboard sections", async () => {
  const route = await resolveShellRoute("/explainability", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient());
  assertEqual(route.title, "Explainability & Analytics", "Explainability route title should resolve.");
  assert(route.contentHtml.includes("UX-004"), "Explainability route should identify UX-004.");
  assert(route.contentHtml.includes("Overall Confidence"), "Summary cards should render.");
  assert(route.contentHtml.includes("Decision Reasoning"), "Reasoning panel should render.");
  assert(route.contentHtml.includes("Feature Importance"), "Feature importance should render.");
  assert(route.contentHtml.includes("Analytics Dashboard"), "Analytics metrics should render.");
  assert(route.contentHtml.includes("Explainability Timeline"), "Timeline should render.");
  assert(route.contentHtml.includes("Recommendation Summary"), "Recommendation summary should render.");
  assert(route.contentHtml.includes("01 Jul 2026, 3:40 PM"), "UX-004 static route should render timestamps in Asia/Kolkata local time.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(route.contentHtml), "UX-004 static route should not render raw ISO timestamps.");
});

test("explainability route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const fallback = createExplainabilityAnalyticsClient();
  const client: ExplainabilityAnalyticsClient = {
    async getExplainabilitySummary() {
      calls.push("getExplainabilitySummary");
      return fallback.getExplainabilitySummary();
    },
    async getDecisionReasoning() {
      calls.push("getDecisionReasoning");
      return fallback.getDecisionReasoning();
    },
    async getFeatureImportance() {
      calls.push("getFeatureImportance");
      return fallback.getFeatureImportance();
    },
    async getAnalyticsMetrics() {
      calls.push("getAnalyticsMetrics");
      return fallback.getAnalyticsMetrics();
    },
    async getRecommendationSummary() {
      calls.push("getRecommendationSummary");
      return fallback.getRecommendationSummary();
    },
    async getTimeline() {
      calls.push("getTimeline");
      return fallback.getTimeline();
    },
    generateExplanation: () => fallback.generateExplanation(),
    refreshAnalytics: () => fallback.refreshAnalytics(),
  };
  await resolveShellRoute("/explainability", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), client);
  assertEqual(calls.join(","), "getExplainabilitySummary,getDecisionReasoning,getFeatureImportance,getAnalyticsMetrics,getRecommendationSummary,getTimeline", "Explainability route should consume data through ExplainabilityAnalyticsClient.");
});

test("documentation route renders UX-005 generator sections", async () => {
  const route = await resolveShellRoute("/documentation", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), createDocumentationGenerationClient());
  assertEqual(route.title, "Documentation / Patent / Research", "Documentation route title should resolve.");
  assert(route.contentHtml.includes("UX-005"), "Documentation route should identify UX-005.");
  assert(route.contentHtml.includes("No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview."), "Documentation route should render the default package placeholder.");
  assert(!route.contentHtml.includes("Documentation Panel"), "Documentation panel should stay hidden before generation.");
  assert(!route.contentHtml.includes("Patent Panel"), "Patent panel should stay hidden before generation.");
  assert(!route.contentHtml.includes("Research Paper Panel"), "Research paper panel should stay hidden before generation.");
  assert(route.contentHtml.includes("Generation Activity"), "Generation activity should render.");
  assert(route.contentHtml.includes("Generate Documentation"), "Generate Documentation action should render.");
  assert(route.contentHtml.includes("Export Package"), "Export Package action should render.");
  assert(/\d{2} [A-Z][a-z]{2} 2026, \d{1,2}:\d{2} [AP]M/.test(route.contentHtml), "UX-005 static route should render readable Asia/Kolkata timestamps.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(route.contentHtml), "UX-005 static route should not render raw ISO timestamps.");
});

test("documentation route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const fallback = createDocumentationGenerationClient();
  const client: DocumentationGenerationClient = {
    async getSummary() {
      calls.push("getSummary");
      return fallback.getSummary();
    },
    async getDocumentation() {
      calls.push("getDocumentation");
      return fallback.getDocumentation();
    },
    async getPatent() {
      calls.push("getPatent");
      return fallback.getPatent();
    },
    async getResearchPaper() {
      calls.push("getResearchPaper");
      return fallback.getResearchPaper();
    },
    async getActivity() {
      calls.push("getActivity");
      return fallback.getActivity();
    },
    generateDocumentation: () => fallback.generateDocumentation(),
    generatePatent: () => fallback.generatePatent(),
    generateResearchPaper: () => fallback.generateResearchPaper(),
    refresh: () => fallback.refresh(),
    exportPackage: () => fallback.exportPackage(),
  };
  await resolveShellRoute("/documentation", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), client);
  assertEqual(calls.join(","), "getSummary,getDocumentation,getPatent,getResearchPaper,getActivity", "Documentation route should consume data through DocumentationGenerationClient.");
});

test("administration route renders UX-006 administration sections", async () => {
  const route = await resolveShellRoute("/administration", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), createDocumentationGenerationClient(), createAdministrationUserManagementClient());
  assertEqual(route.title, "Administration", "Administration route title should resolve.");
  assert(route.contentHtml.includes("UX-006"), "Administration route should identify UX-006.");
  assert(route.contentHtml.includes("Administration & User Management Center"), "Administration header should render.");
  assert(route.contentHtml.includes("User Management"), "User table should render.");
  assert(route.contentHtml.includes("Roles & Permissions"), "Roles panel should render.");
  assert(route.contentHtml.includes("Governance Controls"), "Governance controls should render.");
  assert(route.contentHtml.includes("Audit Log"), "Audit log should render.");
  assert(route.contentHtml.includes("System Settings"), "System settings should render.");
  assert(route.contentHtml.includes("Sync Administration"), "Sync action should render.");
  assert(route.contentHtml.includes("Export Audit Log"), "Export action should render.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(route.contentHtml), "UX-006 static route should not render raw ISO timestamps.");
});

test("administration route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const fallback = createAdministrationUserManagementClient();
  const client: AdministrationUserManagementClient = {
    async getAdministrationSummary() {
      calls.push("getAdministrationSummary");
      return fallback.getAdministrationSummary();
    },
    async listUsers() {
      calls.push("listUsers");
      return fallback.listUsers();
    },
    async listRoles() {
      calls.push("listRoles");
      return fallback.listRoles();
    },
    async getGovernanceControls() {
      calls.push("getGovernanceControls");
      return fallback.getGovernanceControls();
    },
    async getAuditLog() {
      calls.push("getAuditLog");
      return fallback.getAuditLog();
    },
    async getSystemSettings() {
      calls.push("getSystemSettings");
      return fallback.getSystemSettings();
    },
    syncAdministration: () => fallback.syncAdministration(),
    refreshAdministration: () => fallback.refreshAdministration(),
    addUser: () => fallback.addUser(),
    removeUser: (userId) => fallback.removeUser(userId),
    changeUserRole: (userId, role) => fallback.changeUserRole(userId, role),
    toggleUserStatus: (userId) => fallback.toggleUserStatus(userId),
    exportAuditLog: () => fallback.exportAuditLog(),
  };
  await resolveShellRoute("/administration", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), createDocumentationGenerationClient(), client);
  assertEqual(calls.join(","), "getAdministrationSummary,listUsers,listRoles,getGovernanceControls,getAuditLog,getSystemSettings", "Administration route should consume data through AdministrationUserManagementClient.");
});

test("administration client persists added users after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createAdministrationUserManagementClient();
    await client.addUser();
    const refreshedClient = createAdministrationUserManagementClient();
    const users = await refreshedClient.listUsers();
    const auditLog = await refreshedClient.getAuditLog();
    assert(users.some((user) => user.id === "ADMIN-UX-USER-001"), "Added user should survive client recreation.");
    assert(auditLog.some((entry) => entry.action === "User added" && entry.resource === "ADMIN-UX-USER-001"), "Added user audit entry should persist.");
    assert(localStorage.storage.getItem(ADMINISTRATION_STORAGE_KEY)?.includes("ADMIN-UX-USER-001"), "Administration snapshot should be saved to the configured localStorage key.");
  } finally {
    localStorage.restore();
  }
});

test("administration client persists removed users after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createAdministrationUserManagementClient();
    await client.addUser();
    await client.removeUser("ADMIN-UX-USER-001");
    const refreshedClient = createAdministrationUserManagementClient();
    const users = await refreshedClient.listUsers();
    const auditLog = await refreshedClient.getAuditLog();
    assert(!users.some((user) => user.id === "ADMIN-UX-USER-001"), "Removed user should stay removed after client recreation.");
    assert(auditLog.some((entry) => entry.action === "User removed" && entry.resource.includes("ADMIN-UX-USER-001")), "Removed user audit entry should persist.");
    assert(!localStorage.storage.getItem(ADMINISTRATION_STORAGE_KEY)?.includes("\"id\":\"ADMIN-UX-USER-001\""), "Removed user should not remain in persisted users.");
  } finally {
    localStorage.restore();
  }
});

test("administration client refresh preserves added and removed users", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createAdministrationUserManagementClient();
    await client.addUser();
    await client.addUser();
    await client.removeUser("ADMIN-UX-USER-001");
    await client.refreshAdministration();
    const refreshedClient = createAdministrationUserManagementClient();
    const users = await refreshedClient.listUsers();
    assert(!users.some((user) => user.id === "ADMIN-UX-USER-001"), "Refresh should not restore removed users.");
    assert(users.some((user) => user.id === "ADMIN-UX-USER-002"), "Refresh should preserve remaining added users.");
  } finally {
    localStorage.restore();
  }
});

test("administration client persists role changes after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createAdministrationUserManagementClient();
    await client.addUser();
    await client.changeUserRole("ADMIN-UX-USER-001", "Auditor");
    const refreshedClient = createAdministrationUserManagementClient();
    const users = await refreshedClient.listUsers();
    const updatedUser = users.find((user) => user.id === "ADMIN-UX-USER-001");
    assertEqual(updatedUser?.role, "Auditor", "Role change should survive client recreation.");
  } finally {
    localStorage.restore();
  }
});

test("administration client persists status toggles after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createAdministrationUserManagementClient();
    await client.addUser();
    await client.toggleUserStatus("ADMIN-UX-USER-001");
    const refreshedClient = createAdministrationUserManagementClient();
    const users = await refreshedClient.listUsers();
    const updatedUser = users.find((user) => user.id === "ADMIN-UX-USER-001");
    assertEqual(updatedUser?.status, "suspended", "Status toggle should survive client recreation.");
  } finally {
    localStorage.restore();
  }
});

test("administration client falls back safely when localStorage snapshot is invalid", async () => {
  const localStorage = installMockLocalStorage({ [ADMINISTRATION_STORAGE_KEY]: "{invalid administration snapshot" });
  try {
    const client = createAdministrationUserManagementClient();
    const users = await client.listUsers();
    assertEqual(users.length, 3, "Invalid localStorage data should fall back to base users.");
    assert(users.some((user) => user.id === "USR-001"), "Fallback users should remain available.");
  } finally {
    localStorage.restore();
  }
});

test("platform integration route renders UX-007 integration sections", async () => {
  const route = await resolveShellRoute("/platform-integration", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), createDocumentationGenerationClient(), createAdministrationUserManagementClient(), createEnterpriseIntegrationClient());
  assertEqual(route.title, "Platform Integration", "Platform Integration route title should resolve.");
  assert(route.contentHtml.includes("UX-007"), "Platform Integration route should identify UX-007.");
  assert(route.contentHtml.includes("Enterprise Platform Integration Console"), "Integration header should render.");
  assert(route.contentHtml.includes("Connector Management"), "Connector management should render.");
  assert(route.contentHtml.includes("API Endpoint Overview"), "API endpoint overview should render.");
  assert(route.contentHtml.includes("Webhook Configuration"), "Webhook configuration should render.");
  assert(route.contentHtml.includes("Deployment & Environment"), "Deployment environment should render.");
  assert(route.contentHtml.includes("Integration Activity Log"), "Integration activity should render.");
  assert(route.contentHtml.includes("Sync Integrations"), "Sync Integrations action should render.");
  assert(route.contentHtml.includes("Export Config"), "Export Config action should render.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(route.contentHtml), "UX-007 static route should not render raw ISO timestamps.");
});

test("platform integration route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const fallback = createEnterpriseIntegrationClient();
  const client: EnterpriseIntegrationClient = {
    async getIntegrationSummary() {
      calls.push("getIntegrationSummary");
      return fallback.getIntegrationSummary();
    },
    async listConnectors() {
      calls.push("listConnectors");
      return fallback.listConnectors();
    },
    async listApiEndpoints() {
      calls.push("listApiEndpoints");
      return fallback.listApiEndpoints();
    },
    async listWebhooks() {
      calls.push("listWebhooks");
      return fallback.listWebhooks();
    },
    async getDeploymentEnvironment() {
      calls.push("getDeploymentEnvironment");
      return fallback.getDeploymentEnvironment();
    },
    async listIntegrationActivity() {
      calls.push("listIntegrationActivity");
      return fallback.listIntegrationActivity();
    },
    syncIntegrations: () => fallback.syncIntegrations(),
    testConnections: () => fallback.testConnections(),
    exportConfig: () => fallback.exportConfig(),
    testConnector: (connectorId) => fallback.testConnector(connectorId),
    toggleConnector: (connectorId) => fallback.toggleConnector(connectorId),
    refreshEndpoints: () => fallback.refreshEndpoints(),
    exportApiMap: () => fallback.exportApiMap(),
    addWebhook: () => fallback.addWebhook(),
    testWebhook: (webhookId) => fallback.testWebhook(webhookId),
    toggleWebhook: (webhookId) => fallback.toggleWebhook(webhookId),
  };
  await resolveShellRoute("/platform-integration", createBackendStatusClient(), createDecisionWorkspaceClient(), createKnowledgeGraphProvenanceClient(), createExplainabilityAnalyticsClient(), createDocumentationGenerationClient(), createAdministrationUserManagementClient(), client);
  assertEqual(calls.join(","), "getIntegrationSummary,listConnectors,listApiEndpoints,listWebhooks,getDeploymentEnvironment,listIntegrationActivity", "Platform Integration route should consume data through EnterpriseIntegrationClient.");
});

test("platform integration client persists added webhooks after client recreation", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createEnterpriseIntegrationClient();
    await client.addWebhook();
    const refreshedClient = createEnterpriseIntegrationClient();
    const webhooks = await refreshedClient.listWebhooks();
    assert(webhooks.some((webhook) => webhook.id === "WH-UX-007-001"), "Added webhook should survive client recreation.");
    assert(localStorage.storage.getItem(ENTERPRISE_INTEGRATION_STORAGE_KEY)?.includes("WH-UX-007-001"), "Integration snapshot should be saved to the configured localStorage key.");
  } finally {
    localStorage.restore();
  }
});

test("platform integration sync and endpoint refresh preserve added webhooks", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createEnterpriseIntegrationClient();
    await client.addWebhook();
    await client.syncIntegrations();
    let refreshedClient = createEnterpriseIntegrationClient();
    let webhooks = await refreshedClient.listWebhooks();
    assert(webhooks.some((webhook) => webhook.id === "WH-UX-007-001"), "Sync Integrations should not delete added webhook.");
    await refreshedClient.refreshEndpoints();
    refreshedClient = createEnterpriseIntegrationClient();
    webhooks = await refreshedClient.listWebhooks();
    assert(webhooks.some((webhook) => webhook.id === "WH-UX-007-001"), "Refresh Endpoints should not delete added webhook.");
  } finally {
    localStorage.restore();
  }
});

test("decision workspace client persists and loads saved frontend decisions", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createDecisionWorkspaceClient();
    const first = await client.createDraftWorkspace?.();
    const second = await client.createDraftWorkspace?.();
    if (!first) throw new Error("First draft workspace should be created.");
    if (!second) throw new Error("Second draft workspace should be created.");
    assertEqual(first.summary.decisionId, "DEC-UX-DRAFT-001", "First draft should use deterministic ID.");
    assertEqual(second.summary.decisionId, "DEC-UX-DRAFT-002", "Second draft should use deterministic ID.");
    assert(localStorage.storage.getItem(DECISION_WORKSPACE_STORAGE_KEY)?.includes("DEC-UX-DRAFT-002"), "Decision workspace snapshots should be saved to localStorage.");

    const recreated = createDecisionWorkspaceClient();
    const history = await recreated.listSavedDecisionWorkspaces?.();
    if (!history) throw new Error("Recreated client should list saved decision history.");
    assertEqual(history.length, 2, "Decision history should remember both saved frontend decisions.");
    assertEqual(history[0].decisionId, "DEC-UX-DRAFT-002", "Decision history should list newest decisions first.");
    assertEqual(history[1].decisionId, "DEC-UX-DRAFT-001", "Decision history should preserve older generated decisions.");
    const loadedFirst = await recreated.loadDecisionWorkspace?.();
    const loadedSecond = await recreated.loadDecisionWorkspace?.();
    if (!loadedFirst) throw new Error("Recreated client should load the first saved draft.");
    if (!loadedSecond) throw new Error("Recreated client should load the second saved draft.");
    assertEqual(loadedFirst.summary.decisionId, "DEC-UX-DRAFT-001", "Load Decision should cycle saved draft snapshots after client recreation.");
    assertEqual(loadedFirst.summary.status, "loaded", "Loaded saved draft should use loaded status.");
    assertEqual(loadedSecond.summary.decisionId, "DEC-UX-DRAFT-002", "Load Decision should continue cycling saved draft snapshots.");
  } finally {
    localStorage.restore();
  }
});

test("decision workspace client caps saved frontend decision history", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createDecisionWorkspaceClient();
    for (let index = 0; index < 12; index += 1) {
      await client.createDraftWorkspace?.();
    }
    const history = await client.listSavedDecisionWorkspaces?.();
    if (!history) throw new Error("Decision history should be listable.");
    assertEqual(history.length, 10, "Decision history should be capped to the latest 10 saved frontend decisions.");
    assertEqual(history[0].decisionId, "DEC-UX-DRAFT-012", "Newest saved decision should appear first.");
    assertEqual(history[9].decisionId, "DEC-UX-DRAFT-003", "Oldest retained decision should be the tenth latest unique entry.");
    assert(!localStorage.storage.getItem(DECISION_WORKSPACE_STORAGE_KEY)?.includes("DEC-UX-DRAFT-001"), "Old history entries beyond the cap should not remain persisted.");
  } finally {
    localStorage.restore();
  }
});

test("decision workspace new decisions use meaningfully different demo templates", async () => {
  const localStorage = installMockLocalStorage();
  try {
    const client = createDecisionWorkspaceClient();
    const snapshots = [];
    const evaluationScoreSets = [];
    const rankingRecommendationIds = [];
    const criteriaWeightSets = [];
    for (let index = 0; index < 6; index += 1) {
      const snapshot = await client.createDraftWorkspace?.();
      if (!snapshot) throw new Error("Draft workspace should be created.");
      snapshots.push(snapshot);
      const evaluation = await client.runEvaluation();
      const ranking = await client.runRanking();
      evaluationScoreSets.push(evaluation.map((result) => result.score).join(","));
      criteriaWeightSets.push(evaluation[0]?.criteria.map((criterion) => criterion.weight).join(",") ?? "");
      rankingRecommendationIds.push(ranking.find((result) => result.recommended)?.alternativeId ?? "");
    }

    assertEqual(new Set(snapshots.map((snapshot) => snapshot.summary.decisionId)).size, 6, "Each generated decision should have a unique decision ID.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.summary.workspaceTitle)).size, 6, "Each generated decision should have a distinct title.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.context.objective)).size, 6, "Each generated decision should have a distinct objective.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.context.domain)).size, 6, "Each generated decision should have a distinct domain.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.context.riskPreference)).size, 6, "Each generated decision should have a distinct risk preference.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.context.constraints.join("|"))).size, 6, "Each generated decision should have distinct constraints.");
    assertEqual(new Set(snapshots.map((snapshot) => snapshot.alternatives.map((alternative) => alternative.id).join("|"))).size, 6, "Each generated decision should have distinct option IDs.");
    assertEqual(new Set(evaluationScoreSets).size, 6, "Each generated decision should have distinct evaluation scores.");
    assertEqual(new Set(criteriaWeightSets).size, 6, "Each generated decision should have distinct criteria weights.");
    assertEqual(new Set(rankingRecommendationIds).size, 6, "Each generated decision should have distinct recommended alternatives.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Supply chain optimization"), "Supply chain demo template should exist.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Healthcare resource allocation"), "Healthcare demo template should exist.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Financial risk mitigation"), "Financial risk demo template should exist.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Hiring and workforce planning"), "Workforce planning demo template should exist.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Sustainability investment"), "Sustainability demo template should exist.");
    assert(snapshots.some((snapshot) => snapshot.context.domain === "Customer retention"), "Customer retention demo template should exist.");
  } finally {
    localStorage.restore();
  }
});

test("decision workspace route uses its own UX adapter boundary", async () => {
  const calls: string[] = [];
  const client: DecisionWorkspaceClient = {
    async getWorkspaceSummary() {
      calls.push("getWorkspaceSummary");
      return createDecisionWorkspaceClient().getWorkspaceSummary();
    },
    async listDecisionSessions() {
      calls.push("listDecisionSessions");
      return createDecisionWorkspaceClient().listDecisionSessions();
    },
    async getDecisionContext() {
      calls.push("getDecisionContext");
      return createDecisionWorkspaceClient().getDecisionContext();
    },
    async listAlternatives() {
      calls.push("listAlternatives");
      return createDecisionWorkspaceClient().listAlternatives();
    },
    async runEvaluation() {
      calls.push("runEvaluation");
      return createDecisionWorkspaceClient().runEvaluation();
    },
    async runRanking() {
      calls.push("runRanking");
      return createDecisionWorkspaceClient().runRanking();
    },
    async getWorkspaceTimeline() {
      calls.push("getWorkspaceTimeline");
      return createDecisionWorkspaceClient().getWorkspaceTimeline();
    },
  };
  await resolveShellRoute("/decision-workspace", createBackendStatusClient(), client);
  assertEqual(
    calls.join(","),
    "getWorkspaceSummary,listDecisionSessions,getDecisionContext,listAlternatives,runEvaluation,runRanking,getWorkspaceTimeline",
    "Decision workspace route should consume data through DecisionWorkspaceClient.",
  );
});

test("navigation route rendering changes visible content for each sidebar item", async () => {
  for (const entry of UX_ROADMAP_NAVIGATION) {
    const html = await renderEnterpriseDashboardShell({ routePath: entry.path });
    assert(html.includes(`<span class="ux-route-title">${entry.label}</span>`), `Route title should update for ${entry.id}.`);
    assert(html.includes(`data-route-id="${entry.id}"`), `Navigation item should exist for ${entry.id}.`);
    assert(html.includes(`href="${entry.path}" aria-current="true" data-route-id="${entry.id}"`), `Active navigation state should update for ${entry.id}.`);
    if (entry.id === "dashboard") {
      assert(html.includes("Backend Platform"), "Dashboard should still render status cards.");
    } else if (entry.id === "decision-workspace") {
      assert(html.includes("Decision Context"), "Decision workspace should render UX-002 panels.");
    } else if (entry.id === "knowledge-graph") {
      assert(html.includes("Graph Visualization"), "Knowledge graph should render UX-003 explorer.");
    } else if (entry.id === "explainability") {
      assert(html.includes("Explainability & Analytics Dashboard"), "Explainability should render UX-004 dashboard.");
    } else if (entry.id === "documentation") {
      assert(html.includes("Documentation / Patent / Research Generator"), "Documentation should render UX-005 generator.");
    } else if (entry.id === "administration") {
      assert(html.includes("Administration & User Management Center"), "Administration should render UX-006 center.");
    } else if (entry.id === "platform-integration") {
      assert(html.includes("Enterprise Platform Integration Console"), "Platform Integration should render UX-007 console.");
    } else {
      assert(html.includes(`data-ux-module="${entry.uxModule}"`), `Placeholder content should render for ${entry.id}.`);
    }
  }
});

test("placeholder pages do not call backend status adapter", async () => {
  const calls: string[] = [];
  const client: BackendStatusClient = {
    async getPlatformStatus() {
      calls.push("getPlatformStatus");
      return createBackendStatusClient().getPlatformStatus();
    },
  };
  await renderEnterpriseDashboardShell({ routePath: "/knowledge-graph" }, client);
  assertEqual(calls.length, 0, "Placeholder navigation should not request dashboard backend status.");
});

test("preview hash navigation changes visible page content for sidebar clicks", async () => {
  for (const entry of UX_ROADMAP_NAVIGATION.filter((item) => item.status === "placeholder")) {
    const clickedHash = getPreviewNavigationHash(entry.path);
    const clickedRoute = getPreviewRoutePath("/", clickedHash);
    const html = await renderEnterpriseDashboardShell({ navigationMode: "hash", routePath: clickedRoute });
    assert(html.includes(`href="#${entry.path}"`), `Hash href should render for ${entry.id}.`);
    assert(html.includes(`data-route-path="${entry.path}"`), `Route path data should render for ${entry.id}.`);
    assert(html.includes(`aria-current="true" data-route-id="${entry.id}"`), `Clicked item should become active for ${entry.id}.`);
    assert(html.includes(`data-ux-module="${entry.uxModule}"`), `Clicked route should show ${entry.uxModule}.`);
    assert(html.includes("Coming in future UX implementation"), `Clicked route should show placeholder message for ${entry.id}.`);
  }
});

test("preview hash dashboard navigation returns to dashboard", async () => {
  const clickedRoute = getPreviewRoutePath("/decision-workspace", getPreviewNavigationHash("/"));
  const html = await renderEnterpriseDashboardShell({ navigationMode: "hash", routePath: clickedRoute });
  assert(html.includes('href="#/" aria-current="true" data-route-id="dashboard"'), "Dashboard hash link should become active.");
  assert(html.includes("Backend Platform"), "Dashboard hash navigation should render status cards.");
});

test("direct placeholder refresh paths resolve to placeholders", async () => {
  for (const entry of UX_ROADMAP_NAVIGATION.filter((item) => item.status === "placeholder")) {
    const directRoute = getPreviewRoutePath(entry.path, "");
    const html = await renderEnterpriseDashboardShell({ navigationMode: "hash", routePath: directRoute });
    assert(html.includes(`data-ux-module="${entry.uxModule}"`), `Direct refresh route should render ${entry.uxModule}.`);
  }
});

test("dark and light readiness does not break rendering", async () => {
  const light = await renderEnterpriseDashboardShell({ theme: "light" });
  const dark = await renderEnterpriseDashboardShell({ theme: "dark" });
  assert(light.includes('data-theme="light"'), "Light shell should render theme marker.");
  assert(dark.includes('data-theme="dark"'), "Dark shell should render theme marker.");
  assert(ENTERPRISE_SHELL_CSS.includes('[data-theme="dark"]'), "Dark theme CSS tokens should exist.");
  assert(ENTERPRISE_SHELL_CSS.includes("@media (max-width: 900px)"), "Responsive shell CSS should exist.");
});

for (const item of tests) {
  await item.run();
  console.log(`ok - ${item.name}`);
}
