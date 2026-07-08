import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { App } from "../App.js";
import { createAdministrationUserManagementClient, createDecisionWorkspaceClient, createDocumentationGenerationClient, createEnterpriseIntegrationClient, createExplainabilityAnalyticsClient, createKnowledgeGraphProvenanceClient, type AdministrationUserManagementClient, type DecisionWorkspaceClient, type DocumentationGenerationClient, type EnterpriseIntegrationClient, type ExplainabilityAnalyticsClient, type KnowledgeGraphProvenanceClient } from "../index.js";

type TestCase = { name: string; run: () => Promise<void> | void };

const tests: TestCase[] = [];

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function test(name: string, run: TestCase["run"]): void {
  tests.push({ name, run });
}

function assert(condition: unknown, message: string): void {
  if (!condition) throw new Error(message);
}

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (actual !== expected) throw new Error(`${message}. Expected ${String(expected)}, got ${String(actual)}.`);
}

async function renderApp(props: Parameters<typeof App>[0] = {}): Promise<{ dom: JSDOM; root: Root }> {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', {
    url: "http://127.0.0.1:5173/",
  });
  Object.assign(globalThis, {
    window: dom.window,
    document: dom.window.document,
    HTMLElement: dom.window.HTMLElement,
    Event: dom.window.Event,
    MouseEvent: dom.window.MouseEvent,
  });

  const container = dom.window.document.getElementById("root");
  if (!container) throw new Error("Test root should exist.");
  const root = createRoot(container);
  await act(async () => {
    root.render(<App {...props} />);
  });
  return { dom, root };
}

async function clickRoute(routeId: string): Promise<void> {
  const button = document.querySelector<HTMLButtonElement>(`.ux-nav-link[data-route-id="${routeId}"]`);
  if (!button) throw new Error(`Route button should exist: ${routeId}`);
  await act(async () => {
    button.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
}

function visibleText(): string {
  return document.body.textContent ?? "";
}

function timelineItems(): NodeListOf<HTMLLIElement> {
  return document.querySelectorAll<HTMLLIElement>(".ux-timeline li");
}

function countVisibleOccurrences(value: string): number {
  return (visibleText().match(new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) ?? []).length;
}

function activeRouteId(): string | null {
  return document.querySelector(".ux-nav-link[aria-current=\"true\"]")?.getAttribute("data-route-id") ?? null;
}

function actionButton(actionId: string): HTMLButtonElement {
  const button = document.querySelector<HTMLButtonElement>(`[data-action-id="${actionId}"]`);
  if (!button) throw new Error(`Action button should exist: ${actionId}`);
  return button;
}

function decodedDownloadPayload(): Record<string, unknown> {
  const href = document.querySelector<HTMLAnchorElement>('[data-action-id="download-docgen-package"]')?.href;
  if (!href?.startsWith("data:application/json")) throw new Error("Download payload should be available as JSON data URL.");
  const encoded = href.slice(href.indexOf(",") + 1);
  return JSON.parse(decodeURIComponent(encoded)) as Record<string, unknown>;
}

async function selectGraphFilter(name: string, value: string): Promise<void> {
  const select = document.querySelector<HTMLSelectElement>(`select[data-filter-name="${name}"]`);
  if (!select) throw new Error(`Graph filter should exist: ${name}`);
  await act(async () => {
    select.value = value;
    select.dispatchEvent(new Event("change", { bubbles: true, cancelable: true }));
  });
}

function deferred(): { promise: Promise<void>; resolve: () => void; reject: () => void } {
  let resolve!: () => void;
  let reject!: () => void;
  const promise = new Promise<void>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function installMockDate(initialIso: string): { setNow: (iso: string) => void; restore: () => void } {
  const RealDate = globalThis.Date;
  let fixedTime = new RealDate(initialIso).getTime();
  class MockDate extends RealDate {
    constructor(value?: string | number | Date) {
      if (arguments.length === 0) super(fixedTime);
      else super(value as string);
    }
    static now(): number {
      return fixedTime;
    }
  }
  Object.setPrototypeOf(MockDate, RealDate);
  globalThis.Date = MockDate as DateConstructor;
  return {
    setNow(iso: string) {
      fixedTime = new RealDate(iso).getTime();
    },
    restore() {
      globalThis.Date = RealDate;
    },
  };
}

test("React preview renders dashboard by default", async () => {
  const { root } = await renderApp();
  assert(visibleText().includes("Backend Platform"), "Dashboard status cards should render by default.");
  assert(visibleText().includes("Decision Provenance Graph"), "Dashboard mechanism cards should render by default.");
  assertEqual(activeRouteId(), "dashboard", "Dashboard nav should be active by default.");
  await act(async () => root.unmount());
});

test("React preview sidebar has no remaining placeholders", async () => {
  const { root } = await renderApp();
  await clickRoute("platform-integration");
  assert(!visibleText().includes("Coming in future UX implementation"), "UX-007 should no longer render placeholder copy.");
  assertEqual(activeRouteId(), "platform-integration", "Platform Integration nav should become active.");
  await act(async () => root.unmount());
});

test("React preview explainability dashboard renders and action buttons work", async () => {
  const calls: string[] = [];
  const fallback = createExplainabilityAnalyticsClient();
  const generateRun = deferred();
  const refreshRun = deferred();
  const clock = installMockDate("2026-07-02T12:34:00.000Z");
  const client: ExplainabilityAnalyticsClient = {
    getExplainabilitySummary: () => fallback.getExplainabilitySummary(),
    getDecisionReasoning: () => fallback.getDecisionReasoning(),
    getFeatureImportance: () => fallback.getFeatureImportance(),
    getAnalyticsMetrics: () => fallback.getAnalyticsMetrics(),
    getRecommendationSummary: () => fallback.getRecommendationSummary(),
    getTimeline: () => fallback.getTimeline(),
    async generateExplanation() {
      calls.push("generateExplanation");
      await generateRun.promise;
      return fallback.generateExplanation();
    },
    async refreshAnalytics() {
      calls.push("refreshAnalytics");
      await refreshRun.promise;
      return fallback.refreshAnalytics();
    },
  };
  const { root } = await renderApp({ explainabilityClient: client });
  await clickRoute("explainability");
  let text = visibleText();
  assert(text.includes("UX-004"), "Explainability route should identify UX-004.");
  assert(text.includes("Explainability & Analytics Dashboard"), "Explainability dashboard should render.");
  assert(text.includes("Overall Confidence"), "Summary cards should render.");
  assert(text.includes("Decision Reasoning"), "Decision reasoning panel should render.");
  assert(text.includes("No explanation generated yet"), "Explainability page should start with an explanation placeholder.");
  assert(text.includes("Feature Importance"), "Feature importance should render.");
  assert(text.includes("Analytics Dashboard"), "Analytics metrics should render.");
  assert(text.includes("Snapshot version 0"), "Analytics dashboard should start with a visible snapshot version.");
  assert(text.includes("Last refreshed Not refreshed this session"), "Analytics content should include local refresh metadata.");
  assert(text.includes("Explainability Timeline"), "Timeline should render.");
  assert(text.includes("Recommendation Summary"), "Recommendation summary should render.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Explainability page should not show raw ISO timestamps.");
  assert(text.includes("01 Jul 2026"), "Explainability page should render readable local timestamps.");

  await act(async () => {
    actionButton("generate-explanation").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(actionButton("generate-explanation").disabled, "Generate Explanation should disable while running.");
  assert(visibleText().includes("Generating explanation..."), "Generate Explanation should show loading text.");
  clock.setNow("2026-07-02T12:34:00.000Z");
  generateRun.resolve();
  await act(async () => {
    await generateRun.promise;
  });
  text = visibleText();
  assert(calls.includes("generateExplanation"), "Generate Explanation should call adapter.");
  assert(text.includes("Explanation completed"), "Generate Explanation should update UI.");
  assert(text.includes("Explanation generated from current decision snapshot."), "Generate Explanation should explain the current snapshot source.");
  assert(text.includes("Explanation Generated"), "Generate Explanation should add a timeline event.");
  assert(text.includes("Generated explanation snapshot confirms"), "Generate Explanation should visibly update reasoning.");
  assert(text.includes("Top Factors"), "Generate Explanation should reveal explanation content.");
  assert(text.includes("02 Jul 2026, 6:04 PM"), "Generate Explanation should show mocked current time in Asia/Kolkata format.");
  assert(!text.includes("02 Jul 2026, 10:45 PM"), "Generate Explanation should not use the old hardcoded action timestamp.");
  assert(text.includes("Generated"), "Generate Explanation should update status.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Generate Explanation should not show raw ISO timestamps.");

  await act(async () => {
    actionButton("refresh-analytics").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(actionButton("refresh-analytics").disabled, "Refresh Analytics should disable while running.");
  assert(visibleText().includes("Refreshing analytics..."), "Refresh Analytics should show loading text.");
  clock.setNow("2026-07-02T12:35:00.000Z");
  refreshRun.resolve();
  await act(async () => {
    await refreshRun.promise;
  });
  text = visibleText();
  assert(calls.includes("refreshAnalytics"), "Refresh Analytics should call adapter.");
  assert(text.includes("Analytics refreshed"), "Refresh Analytics should update UI.");
  assert(text.includes("Current v1.0.0 adapter snapshot reloaded. No external enterprise data source is connected."), "Refresh Analytics should be honest about adapter snapshot scope.");
  assert(text.includes("Snapshot version 1"), "Refresh Analytics should show a visible refresh version.");
  assert(text.includes("Last refreshed 02 Jul 2026, 6:05 PM"), "Refresh Analytics should update the analytics content last-refreshed field.");
  assert(text.includes("Values unchanged after adapter snapshot reload."), "Refresh Analytics should clearly report unchanged adapter values.");
  assert(text.includes("Updated from snapshot"), "Refresh Analytics should visibly mark analytics cards as refreshed.");
  assert(text.includes("Refreshed"), "Refresh Analytics should update status.");
  assert(text.includes("Analytics Refreshed"), "Refresh Analytics should add a timeline event.");
  assert(text.includes("Explanation Generated"), "Refresh Analytics should keep the previous explanation timeline event visible.");
  assert(text.includes("Evaluation Metrics"), "Refresh Analytics should keep analytics cards visible.");
  assert(text.includes("Analysis Latency"), "Refresh Analytics should keep metric cards visible.");
  assert(text.includes("Generated explanation snapshot confirms"), "Refresh Analytics should not roll back generated reasoning.");
  assert(text.includes("02 Jul 2026, 6:05 PM"), "Refresh Analytics should show mocked current time in Asia/Kolkata format.");
  assert(!text.includes("02 Jul 2026, 10:50 PM"), "Refresh Analytics should not use the old hardcoded action timestamp.");
  assert(timelineItems().length <= 8, "Explainability timeline should be capped.");

  await act(async () => {
    actionButton("export-report").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Report exported"), "Export Report should update UI.");
  assert(text.includes("Report Exported"), "Export Report should add a timeline event.");
  assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-export-report"]')?.download === "DEC-2026-001-explainability-report.json", "Export Report should expose a downloadable JSON report link.");
  assert(timelineItems().length <= 8, "Export Report should keep timeline capped.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Export Report should not show raw ISO timestamps.");
  assertEqual(activeRouteId(), "explainability", "Explainability nav should be active.");
  await act(async () => root.unmount());
  clock.restore();
});

test("React preview documentation generator renders and action buttons work", async () => {
  const calls: string[] = [];
  const fallback = createDocumentationGenerationClient();
  const client: DocumentationGenerationClient = {
    getSummary: () => fallback.getSummary(),
    getDocumentation: () => fallback.getDocumentation(),
    getPatent: () => fallback.getPatent(),
    getResearchPaper: () => fallback.getResearchPaper(),
    getActivity: () => fallback.getActivity(),
    async generateDocumentation() {
      calls.push("generateDocumentation");
      return fallback.generateDocumentation();
    },
    async generatePatent() {
      calls.push("generatePatent");
      return fallback.generatePatent();
    },
    async generateResearchPaper() {
      calls.push("generateResearchPaper");
      return fallback.generateResearchPaper();
    },
    async refresh() {
      calls.push("refresh");
      return fallback.refresh();
    },
    async exportPackage() {
      calls.push("exportPackage");
      return fallback.exportPackage();
    },
  };
  const { root } = await renderApp({ documentationGenerationClient: client });
  await clickRoute("documentation");
  let text = visibleText();
  assert(text.includes("UX-005"), "Documentation route should identify UX-005.");
  assert(text.includes("Documentation / Patent / Research Generator"), "Documentation generator should render.");
  assert(text.includes("No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview."), "Documentation generator should start with the package placeholder.");
  assert(!text.includes("Documentation Panel"), "Documentation panel should be hidden before generation.");
  assert(!text.includes("Patent Panel"), "Patent panel should be hidden before generation.");
  assert(!text.includes("Research Paper Panel"), "Research paper panel should be hidden before generation.");
  assert(text.includes("Generation Activity"), "Generation activity should render.");
  assert(!text.includes("Architecture Overview:"), "Documentation preview should be empty before generation.");
  assert(!text.includes("Patent Draft"), "Patent cards should be hidden before generation.");
  assert(!text.includes("Abstract"), "Research cards should be hidden before generation.");
  assert(/\d{2} [A-Z][a-z]{2} 2026, \d{1,2}:\d{2} [AP]M/.test(text), "Documentation generator should render readable timestamps.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Documentation generator should not show raw ISO timestamps.");

  await act(async () => {
    actionButton("generate-documentation").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("generateDocumentation"), "Generate Documentation should call adapter.");
  assert(text.includes("Documentation package generated from existing DOC modules."), "Generate Documentation should explain the DOC module source.");
  assert(text.includes("Generated Package"), "Generate Documentation should show the generated package section.");
  assert(!text.includes("Documentation Panel"), "Generate Documentation should use the generated package layout.");
  assert(!text.includes("Patent Panel"), "Generate Documentation should hide patent panel.");
  assert(!text.includes("Research Paper Panel"), "Generate Documentation should hide research paper panel.");
  assert(text.includes("Package Item Preview"), "Generate Documentation should show the preview panel.");
  assert(text.includes("Title: Architecture"), "Generate Documentation should populate selected documentation item title.");
  assert(text.includes("ID: doc-architecture"), "Generate Documentation should populate selected documentation item ID.");
  assert(text.includes("Version: DOC-001"), "Generate Documentation should populate selected documentation item version.");
  assert(text.includes("Summary: Architecture overview generated from backend documentation outputs."), "Generate Documentation should populate selected documentation item summary.");
  assert(text.includes("Documentation Generated"), "Generate Documentation should add activity.");
  await act(async () => {
    actionButton("preview-documentation-doc-api").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Preview ready: API"), "Documentation Preview should show selected documentation content.");
  assert(text.includes("ID: doc-api"), "Documentation Preview should show selected documentation ID.");
  assert(text.includes("Summary: API reference package consumed from backend documentation services."), "Documentation Preview should correspond to the clicked documentation item.");

  await act(async () => {
    actionButton("generate-patent").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("generatePatent"), "Generate Patent should call adapter.");
  assert(text.includes("Patent package generated from existing PAT modules."), "Generate Patent should explain PAT module source.");
  assert(!text.includes("Documentation Panel"), "Generate Patent should hide documentation panel.");
  assert(!text.includes("Patent Panel"), "Generate Patent should use the generated package layout.");
  assert(!text.includes("Research Paper Panel"), "Generate Patent should hide research paper panel.");
  assert(text.includes("Generated Package"), "Generate Patent should show the generated package section.");
  assert(text.includes("Patent Draft"), "Generate Patent should show Patent Draft.");
  assert(text.includes("Claims"), "Generate Patent should show Claims.");
  assert(text.includes("Novelty Analysis"), "Generate Patent should show Novelty Analysis.");
  assert(!text.includes("Filing Status"), "Generate Patent should not show non-package patent cards in the generated package list.");
  assert(text.includes("Title: Patent Draft"), "Generate Patent should populate selected patent item title.");
  assert(text.includes("ID: patent-draft"), "Generate Patent should populate selected patent item ID.");
  assert(text.includes("Summary: Patent draft package consumed through adapter boundary."), "Generate Patent should populate selected patent item summary.");
  assert(text.includes("Patent Generated"), "Generate Patent should add activity.");
  await act(async () => {
    actionButton("preview-patent-patent-prior-art").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Preview ready: Novelty Analysis"), "Patent preview should update the selected package item preview.");
  assert(text.includes("Title: Novelty Analysis"), "Patent preview should show selected package item title.");
  assert(text.includes("ID: patent-prior-art"), "Patent preview should show selected package item ID.");
  assert(text.includes("Summary: Prior art comparison summary."), "Patent preview should show selected package item summary.");

  await act(async () => {
    actionButton("generate-research").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("generateResearchPaper"), "Generate Research Paper should call adapter.");
  assert(text.includes("Research paper package generated from existing RP modules."), "Generate Research Paper should explain RP module source.");
  assert(!text.includes("Documentation Panel"), "Generate Research Paper should hide documentation panel.");
  assert(!text.includes("Patent Panel"), "Generate Research Paper should hide patent panel.");
  assert(!text.includes("Research Paper Panel"), "Generate Research Paper should use the generated package layout.");
  assert(text.includes("Generated Package"), "Generate Research Paper should show the generated package section.");
  assert(text.includes("Title: Abstract"), "Generate Research Paper should populate selected research item title.");
  assert(text.includes("ID: research-abstract"), "Generate Research Paper should populate selected research item ID.");
  assert(text.includes("Version: RP-001"), "Generate Research Paper should populate selected research item version.");
  assert(text.includes("Status: generated"), "Generate Research Paper should populate selected research item status.");
  assert(text.includes("Summary: Abstract generated from research paper preparation outputs."), "Generate Research Paper should populate selected research item summary.");
  assert(text.includes("Research Generated"), "Generate Research Paper should add activity.");

  assert(document.querySelectorAll('[data-action-id^="generate-documentation-"], [data-action-id^="generate-patent-"], [data-action-id^="generate-research-"]').length === 0, "Section-level Generate buttons should not render.");

  await act(async () => {
    actionButton("preview-research-research-abstract").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Preview ready: Abstract"), "Preview Abstract should select Abstract.");
  assert(text.includes("Title: Abstract"), "Preview Abstract should display its title.");
  assert(text.includes("ID: research-abstract"), "Preview Abstract should display its ID.");
  assert(text.includes("Summary: Abstract generated from research paper preparation outputs."), "Preview Abstract should display its summary.");

  await act(async () => {
    actionButton("download-research-research-abstract").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  let payload = decodedDownloadPayload();
  assertEqual(payload.id, "research-abstract", "Abstract download should use the same ID shown in preview.");
  assertEqual(payload.title, "Abstract", "Abstract download should use the same title shown in preview.");
  assertEqual(payload.version, "RP-001", "Abstract download should use the same version shown in preview.");
  assertEqual(payload.status, "generated", "Abstract download should use the same status shown in preview.");
  assertEqual(payload.summary, "Abstract generated from research paper preparation outputs.", "Abstract download should use the same summary shown in preview.");

  await act(async () => {
    actionButton("preview-research-research-results").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Preview ready: Results"), "Preview Results should select Results.");
  assert(text.includes("Title: Results"), "Preview Results should display Results title.");
  assert(text.includes("ID: research-results"), "Preview Results should display Results ID.");
  assert(text.includes("Summary: Results section package."), "Preview Results should display Results-specific summary.");
  assert(!text.includes("ID: research-abstract"), "Preview Results should replace Abstract preview content.");

  await act(async () => {
    actionButton("preview-research-research-references").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Preview ready: References"), "Preview References should select References.");
  assert(text.includes("Title: References"), "Preview References should display References title.");
  assert(text.includes("ID: research-references"), "Preview References should display References ID.");
  assert(text.includes("Summary: Reference package."), "Preview References should display References-specific summary.");
  assert(!text.includes("ID: research-results"), "Preview References should replace Results preview content.");

  for (const button of Array.from(document.querySelectorAll<HTMLButtonElement>('button[data-action-id^="download-"]'))) {
    await act(async () => {
      button.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
    });
    assert(visibleText().includes("Download ready for"), "Download buttons should visibly update download state.");
    assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-docgen-package"]')?.href.startsWith("data:application/json"), "Download buttons should expose a deterministic JSON download.");
  }
  payload = decodedDownloadPayload();
  assert("id" in payload && "title" in payload && "version" in payload && "status" in payload && "summary" in payload, "Download payload should expose the same fields as preview.");

  await act(async () => {
    actionButton("refresh-docgen").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("refresh"), "Refresh should call adapter.");
  assert(text.includes("Generator refreshed. Choose a package type to generate preview again."), "Refresh should reset the generator view.");
  assert(text.includes("No package generated yet. Choose Documentation, Patent, or Research Paper to generate a package preview."), "Refresh should restore the default placeholder.");
  assert(!text.includes("Documentation Panel"), "Refresh should hide documentation panel.");
  assert(!text.includes("Patent Panel"), "Refresh should hide patent panel.");
  assert(!text.includes("Research Paper Panel"), "Refresh should hide research paper panel.");

  await act(async () => {
    actionButton("export-package").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("exportPackage"), "Export Package should call adapter.");
  assert(text.includes("Package exported"), "Export Package should update UI.");
  assert(text.includes("Package Exported"), "Export Package should add activity.");
  assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-docgen-package"]')?.download === "ux-005-documentation-package.json", "Export Package should expose package download.");
  assert(timelineItems().length <= 8, "Generation activity should stay capped.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Documentation generator actions should not show raw ISO timestamps.");
  assertEqual(activeRouteId(), "documentation", "Documentation nav should be active.");
  await act(async () => root.unmount());
});

test("React preview administration center renders and action buttons work", async () => {
  const calls: string[] = [];
  const fallback = createAdministrationUserManagementClient();
  const staleFallback = () => createAdministrationUserManagementClient();
  const client: AdministrationUserManagementClient = {
    getAdministrationSummary: () => fallback.getAdministrationSummary(),
    listUsers: () => fallback.listUsers(),
    listRoles: () => fallback.listRoles(),
    getGovernanceControls: () => fallback.getGovernanceControls(),
    getAuditLog: () => fallback.getAuditLog(),
    getSystemSettings: () => fallback.getSystemSettings(),
    async syncAdministration() {
      calls.push("syncAdministration");
      return staleFallback().syncAdministration();
    },
    async refreshAdministration() {
      calls.push("refreshAdministration");
      return fallback.refreshAdministration();
    },
    async addUser() {
      calls.push("addUser");
      return fallback.addUser();
    },
    async removeUser(userId) {
      calls.push(`removeUser:${userId}`);
      return fallback.removeUser(userId);
    },
    async changeUserRole(userId, role) {
      calls.push(`changeUserRole:${userId}:${role}`);
      return staleFallback().changeUserRole(userId, role);
    },
    async toggleUserStatus(userId) {
      calls.push(`toggleUserStatus:${userId}`);
      return staleFallback().toggleUserStatus(userId);
    },
    async exportAuditLog() {
      calls.push("exportAuditLog");
      return fallback.exportAuditLog();
    },
  };
  const { dom, root } = await renderApp({ administrationClient: client });
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: dom.window.localStorage });
  const userRowCount = () => [...document.querySelectorAll("article")]
    .find((article) => article.textContent?.includes("User Management"))
    ?.querySelectorAll("tbody tr").length ?? 0;
  const userRowText = (userId: string) => document
    .querySelector(`[data-action-id="view-user-${userId}"]`)
    ?.closest("tr")
    ?.textContent ?? "";
  const userRow = (userId: string): HTMLTableRowElement => {
    const row = document.querySelector(`[data-action-id="view-user-${userId}"]`)?.closest("tr");
    if (!(row instanceof window.HTMLTableRowElement)) throw new Error(`User row should exist: ${userId}`);
    return row;
  };
  const confirmCalls: string[] = [];

  await clickRoute("administration");
  window.confirm = (message?: string) => {
    confirmCalls.push(String(message));
    return true;
  };
  let text = visibleText();
  const initialUserCount = userRowCount();
  assert(text.includes("UX-006"), "Administration route should identify UX-006.");
  assert(text.includes("Administration & User Management Center"), "Administration center should render.");
  assert(text.includes("User Management"), "User management should render.");
  assert(text.includes("Roles & Permissions"), "Roles should render.");
  assert(text.includes("Governance Controls"), "Governance controls should render.");
  assert(text.includes("Audit Log"), "Audit log should render.");
  assert(text.includes("System Settings"), "System settings should render.");
  assert(text.includes("Remove User"), "Toolbar should render Remove User.");
  assert(text.includes("Snapshot version 0"), "Administration should start with visible refresh version.");
  assert(text.includes("Last refreshed at Not refreshed this session"), "Administration should start with refresh metadata.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Administration center should not show raw ISO timestamps.");

  await act(async () => {
    actionButton("remove-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Select a user to remove."), "Remove User should require an explicit selected user.");

  await act(async () => {
    userRow("USR-002").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Selected user USR-002"), "Clicking the second user row should select that user.");
  assertEqual(userRow("USR-002").getAttribute("data-selected"), "true", "Selected row should be visibly marked.");
  await act(async () => {
    userRow("USR-003").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Selected user USR-003"), "Clicking the third user row should select that user.");
  assertEqual(userRow("USR-003").getAttribute("data-selected"), "true", "Selected row highlight should move to the clicked row.");
  assertEqual(userRow("USR-002").getAttribute("data-selected"), "false", "Previous selected row highlight should clear.");

  await act(async () => {
    actionButton("sync-administration").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("syncAdministration"), "Sync Administration should call adapter.");
  assert(text.includes("Administration synced"), "Sync Administration should update status.");
  assert(text.includes("Administration synced"), "Sync Administration should add audit activity.");

  await act(async () => {
    actionButton("add-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Add user dialog opened"), "Add User should visibly open the provisioning dialog.");
  assert(text.includes("Confirm Add User"), "Add User dialog should provide a confirm action.");

  await act(async () => {
    actionButton("confirm-add-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("addUser"), "Add User should call adapter.");
  assert(text.includes("ADMIN-UX-USER-001"), "Add User should add deterministic sample user.");
  assert(text.includes("User added"), "Add User should add audit update.");
  assertEqual(userRowCount(), initialUserCount + 1, "Add User should increase user count.");
  assert(text.includes(`Users ${initialUserCount + 1}`), "User count should update after Add User.");

  await act(async () => {
    actionButton("sync-administration").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("ADMIN-UX-USER-001"), "Added user should remain visible after Sync Administration.");
  assertEqual(userRowCount(), initialUserCount + 1, "Sync Administration should not remove locally added users.");
  assert(text.includes("Administration synced"), "Sync Administration should add audit activity.");

  await act(async () => {
    actionButton("change-role-ADMIN-UX-USER-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.some((call) => call.startsWith("changeUserRole:ADMIN-UX-USER-001")), "Change Role should call adapter for added user.");
  assert(text.includes("ADMIN-UX-USER-001"), "Added user should remain visible after Change Role.");
  assert(userRowText("ADMIN-UX-USER-001").includes("Decision Admin"), "Change Role should update the added user's role.");
  assertEqual(userRowCount(), initialUserCount + 1, "Change Role should not remove locally added users.");

  await act(async () => {
    actionButton("toggle-user-ADMIN-UX-USER-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("toggleUserStatus:ADMIN-UX-USER-001"), "Activate/Suspend should call adapter for added user.");
  assert(text.includes("ADMIN-UX-USER-001"), "Added user should remain visible after Activate/Suspend.");
  assert(userRowText("ADMIN-UX-USER-001").includes("Suspended"), "Activate/Suspend should update the added user's status.");
  assertEqual(userRowCount(), initialUserCount + 1, "Activate/Suspend should not remove locally added users.");

  await act(async () => {
    actionButton("refresh-administration").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("refreshAdministration"), "Refresh should call adapter refreshAdministration.");
  assert(text.includes("Administration snapshot refreshed from current local data."), "Refresh should visibly update status.");
  assert(text.includes("Snapshot version 1"), "Refresh should increment visible snapshot version.");
  assert(text.includes("Last refreshed at"), "Refresh should update content refresh timestamp.");
  assert(text.includes("Refreshed"), "Refresh should visibly mark refreshed rows/content.");
  assert(text.includes("ADMIN-UX-USER-001"), "Added user should remain visible after Refresh.");
  assertEqual(userRowCount(), initialUserCount + 1, "Refresh should merge fallback data without removing locally added users.");

  await act(async () => {
    actionButton("view-user-USR-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Viewing Asha Raman"), "View user should visibly update selected user state.");
  await act(async () => {
    actionButton("refresh-administration").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Administration snapshot refreshed from current local data."), "Administration refresh should explain local data source.");
  assert(visibleText().includes("Selected user USR-001"), "Administration refresh should preserve selected user when still available.");

  await act(async () => {
    actionButton("remove-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Default administrator cannot be removed."), "Remove User should protect the default administrator.");
  assert(text.includes("USR-001"), "Protected administrator should remain visible.");

  await act(async () => {
    actionButton("view-user-ADMIN-UX-USER-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  window.confirm = (message?: string) => {
    confirmCalls.push(String(message));
    return false;
  };
  await act(async () => {
    actionButton("remove-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Remove user canceled"), "Canceled Remove User should show cancellation status.");
  assert(text.includes("ADMIN-UX-USER-001"), "Canceled Remove User should keep selected user.");

  const roleSelector = [...document.querySelectorAll<HTMLSelectElement>("select")]
    .find((select) => [...select.options].some((option) => option.value === "Auditor"));
  if (!roleSelector) throw new Error("Administration role selector should exist.");
  await act(async () => {
    roleSelector.value = "Auditor";
    roleSelector.dispatchEvent(new Event("change", { bubbles: true, cancelable: true }));
  });
  await act(async () => {
    actionButton("change-role-USR-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  await act(async () => {
    userRow("ADMIN-UX-USER-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  await act(async () => {
    actionButton("remove-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("At least one administrator must remain."), "Remove User should prevent removing the last administrator.");
  assert(userRowText("ADMIN-UX-USER-001"), "Last administrator protection should keep selected user.");
  await act(async () => {
    roleSelector.value = "Decision Admin";
    roleSelector.dispatchEvent(new Event("change", { bubbles: true, cancelable: true }));
  });
  await act(async () => {
    actionButton("change-role-USR-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });

  window.confirm = (message?: string) => {
    confirmCalls.push(String(message));
    return true;
  };
  await act(async () => {
    userRow("USR-002").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Selected user USR-002"), "Remove target should be the selected non-top row.");
  await act(async () => {
    actionButton("remove-user").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("removeUser:USR-002"), "Remove User should call adapter for selected non-top user.");
  assert(confirmCalls.some((message) => message.includes("Remove user Mira Shah? This action cannot be undone.")), "Remove User should confirm before deleting the selected user.");
  assert(!userRowText("USR-002"), "Remove User should remove selected non-top user from table.");
  assert(userRowText("ADMIN-UX-USER-001"), "Remove User should not remove the top user unless the top user is selected.");
  assert(text.includes("Selected user USR-003"), "Remove User should move selection to the nearest remaining user.");
  assertEqual(userRowCount(), initialUserCount, "Remove User should update user count.");
  assert(text.includes("User removed"), "Remove User should add audit entry.");
  const recreatedClient = createAdministrationUserManagementClient();
  const recreatedUsers = await recreatedClient.listUsers();
  const recreatedAudit = await recreatedClient.getAuditLog();
  assert(!recreatedUsers.some((user) => user.id === "USR-002"), "Removed user should stay removed after client recreation.");
  assert(recreatedAudit.some((entry) => entry.action === "User removed" && entry.resource.includes("USR-002")), "Removed user audit entry should persist.");

  await act(async () => {
    actionButton("change-role-USR-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.some((call) => call.startsWith("changeUserRole:USR-001")), "Change Role should call adapter.");
  assert(text.includes("Role changed"), "Change Role should add audit update.");

  await act(async () => {
    actionButton("toggle-user-USR-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("toggleUserStatus:USR-001"), "Activate/Suspend should call adapter.");
  assert(text.includes("User status updated"), "Activate/Suspend should add audit update.");

  await act(async () => {
    actionButton("export-audit-log").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("exportAuditLog"), "Export Audit Log should call adapter.");
  assert(text.includes("Audit log exported"), "Export Audit Log should update UI.");
  assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-audit-log"]')?.download === "ux-006-audit-log.json", "Export Audit Log should expose JSON download.");
  assert(timelineItems().length <= 8, "Audit log should stay capped.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Administration actions should not show raw ISO timestamps.");
  assertEqual(activeRouteId(), "administration", "Administration nav should be active.");
  await act(async () => root.unmount());
  Reflect.deleteProperty(globalThis, "localStorage");
});

test("React preview platform integration console renders and action buttons work", async () => {
  const calls: string[] = [];
  const fallback = createEnterpriseIntegrationClient();
  const client: EnterpriseIntegrationClient = {
    getIntegrationSummary: () => fallback.getIntegrationSummary(),
    listConnectors: () => fallback.listConnectors(),
    listApiEndpoints: () => fallback.listApiEndpoints(),
    listWebhooks: () => fallback.listWebhooks(),
    getDeploymentEnvironment: () => fallback.getDeploymentEnvironment(),
    listIntegrationActivity: () => fallback.listIntegrationActivity(),
    async syncIntegrations() {
      calls.push("syncIntegrations");
      return fallback.syncIntegrations();
    },
    async testConnections() {
      calls.push("testConnections");
      return fallback.testConnections();
    },
    async exportConfig() {
      calls.push("exportConfig");
      return fallback.exportConfig();
    },
    async testConnector(connectorId) {
      calls.push(`testConnector:${connectorId}`);
      return fallback.testConnector(connectorId);
    },
    async toggleConnector(connectorId) {
      calls.push(`toggleConnector:${connectorId}`);
      return fallback.toggleConnector(connectorId);
    },
    async refreshEndpoints() {
      calls.push("refreshEndpoints");
      return fallback.refreshEndpoints();
    },
    async exportApiMap() {
      calls.push("exportApiMap");
      return fallback.exportApiMap();
    },
    async addWebhook() {
      calls.push("addWebhook");
      return fallback.addWebhook();
    },
    async testWebhook(webhookId) {
      calls.push(`testWebhook:${webhookId}`);
      return fallback.testWebhook(webhookId);
    },
    async toggleWebhook(webhookId) {
      calls.push(`toggleWebhook:${webhookId}`);
      return fallback.toggleWebhook(webhookId);
    },
  };
  const { dom, root } = await renderApp({ enterpriseIntegrationClient: client });
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: dom.window.localStorage });
  await clickRoute("platform-integration");
  let text = visibleText();
  assert(text.includes("UX-007"), "Platform Integration route should identify UX-007.");
  assert(text.includes("Enterprise Platform Integration Console"), "Integration console should render.");
  assert(text.includes("Connector Management"), "Connector panel should render.");
  assert(text.includes("API Endpoint Overview"), "API endpoint panel should render.");
  assert(text.includes("Webhook Configuration"), "Webhook panel should render.");
  assert(text.includes("Deployment & Environment"), "Deployment panel should render.");
  assert(text.includes("Integration Activity Log"), "Activity log should render.");
  assert(text.includes("Connection Test Summary"), "Connection test summary should render.");
  assert(text.includes("Connector Details"), "Connector details should render.");
  assert(text.includes("Endpoint Refresh Summary"), "Endpoint refresh summary should render.");
  assert(text.includes("Snapshot version 0"), "Endpoint summary should start with snapshot version.");
  assert(!document.querySelector('[data-action-id^="view-connector-"]'), "Connector rows should not render View Details buttons.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Integration console should not show raw ISO timestamps.");

  await act(async () => {
    actionButton("sync-integrations").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(calls.includes("syncIntegrations"), "Sync Integrations should call adapter.");
  assert(visibleText().includes("Integrations synced"), "Sync Integrations should update activity/status.");

  await act(async () => {
    actionButton("test-connections").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(calls.includes("testConnections"), "Test Connections should call adapter.");
  assert(visibleText().includes("Connections tested"), "Test Connections should update activity/status.");
  assert(visibleText().includes("current v1.0.0 adapter configuration"), "Test Connections should explain adapter-only connection checks.");
  text = visibleText();
  assert(text.includes("Total connectors 8"), "Test Connections should update connector total summary.");
  assert(text.includes("Passed 6"), "Test Connections should show passed connector count.");
  assert(text.includes("Disabled 2"), "Test Connections should show disabled connector count.");
  assert(text.includes("Average latency 107 ms"), "Test Connections should show deterministic average latency.");
  assert(text.includes("Connector disabled. Enable before testing."), "Test Connections should show disabled connector result.");
  assert(text.includes("Documentation Service connection test passed against local adapter configuration."), "Test Connections should show connector row result messages.");

  await act(async () => {
    actionButton("test-connector-CONN-DOC").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("testConnector:CONN-DOC"), "Connector Test should call adapter.");
  assert(text.includes("Connector tested"), "Connector Test should update activity/status.");
  assert(text.includes("Selected connector Documentation Service"), "Connector Test should update selected connector details.");
  assert(text.includes("Authentication Result"), "Connector Test should populate authentication result details.");
  assert(text.includes("Signed request accepted by local adapter contract."), "Connector Test should show connector authentication result.");
  assert(text.includes("Endpoint Validation"), "Connector Test should populate endpoint validation details.");
  assert(text.includes("/api/documentation validated against configured UX-007 endpoint map."), "Connector Test should show endpoint validation result.");
  assert(text.includes("Adapter Handshake"), "Connector Test should populate adapter handshake details.");
  assert(text.includes("Documentation Service adapter handshake completed."), "Connector Test should show adapter handshake result.");
  assert(text.includes("Documentation Service connection test passed against local adapter configuration."), "Connector Test should show connector-specific result.");

  await act(async () => {
    actionButton("test-connector-CONN-WEBHOOK").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("testConnector:CONN-WEBHOOK"), "Disabled connector Test should call adapter.");
  assert(text.includes("Connector disabled. Enable before testing."), "Disabled connector Test should show disabled message.");
  assert(text.includes("Selected connector External Webhook"), "Disabled connector Test should still select the disabled connector.");

  await act(async () => {
    actionButton("toggle-connector-CONN-WEBHOOK").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("toggleConnector:CONN-WEBHOOK"), "Connector toggle should call adapter.");
  assert(text.includes("Connector toggled"), "Connector toggle should update activity/status.");
  assert(text.includes("CONN-WEBHOOK") && text.includes("Enabled"), "Connector toggle should persist visible connector state.");
  assert(!document.querySelector('[data-action-id="view-connector-CONN-BACKEND-API"]'), "View Details action should be removed from connector rows.");

  await act(async () => {
    actionButton("refresh-endpoints").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("refreshEndpoints"), "Refresh Endpoints should call adapter.");
  assert(text.includes("Endpoints refreshed"), "Refresh Endpoints should update activity/status.");
  assert(text.includes("Endpoint count 8"), "Refresh Endpoints should show endpoint count.");
  assert(text.includes("Methods available GET, POST"), "Refresh Endpoints should show methods summary.");
  assert(text.includes("Snapshot version 1"), "Refresh Endpoints should increment endpoint snapshot version.");
  assert(text.includes("Refreshed at"), "Refresh Endpoints should show refresh timestamp.");
  assert(text.includes("v1.1"), "Refresh Endpoints should visibly re-render endpoint snapshot.");
  assert(text.includes("Refreshed"), "Refresh Endpoints should show refreshed row state.");
  assert(document.querySelectorAll(".ux-refreshed-row").length === 8, "Refresh Endpoints should visibly highlight refreshed endpoint rows.");

  await act(async () => {
    actionButton("export-api-map").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(calls.includes("exportApiMap"), "Export API Map should call adapter.");
  assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-api-map"]')?.download === "ux-007-api-map.json", "Export API Map should expose JSON download.");

  await act(async () => {
    actionButton("add-webhook").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("addWebhook"), "Add Webhook should call adapter.");
  assert(text.includes("WH-UX-007-001"), "Add Webhook should add deterministic webhook.");

  await act(async () => {
    actionButton("test-webhook-WH-UX-007-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("testWebhook:WH-UX-007-001"), "Test Webhook should call adapter.");
  assert(text.includes("WH-UX-007-001"), "Test Webhook should preserve added webhook.");
  assert(text.includes("Webhook delivery test completed against local adapter configuration."), "Test Webhook should show deterministic delivery result.");
  const recreatedIntegrationClient = createEnterpriseIntegrationClient();
  const persistedWebhooks = await recreatedIntegrationClient.listWebhooks();
  assert(persistedWebhooks.some((webhook) => webhook.id === "WH-UX-007-001" && webhook.deliveryResult?.includes("Webhook delivery test completed")), "Custom webhook test result should persist after client recreation.");

  await act(async () => {
    actionButton("toggle-webhook-WH-UX-007-001").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("toggleWebhook:WH-UX-007-001"), "Webhook toggle should call adapter.");
  assert(text.includes("WH-UX-007-001") && text.includes("Disabled"), "Webhook toggle should persist visible webhook state.");

  await act(async () => {
    actionButton("export-config").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(calls.includes("exportConfig"), "Export Config should call adapter.");
  assert(text.includes("Config exported"), "Export Config should update UI.");
  assert(document.querySelector<HTMLAnchorElement>('[data-action-id="download-config"]')?.download === "ux-007-integration-config.json", "Export Config should expose JSON download.");
  assert(timelineItems().length <= 8, "Integration activity should stay capped.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Integration actions should not show raw ISO timestamps.");
  assertEqual(activeRouteId(), "platform-integration", "Platform Integration nav should be active.");
  await act(async () => root.unmount());
  Reflect.deleteProperty(globalThis, "localStorage");
});

test("React preview knowledge graph explorer supports selection and adapter actions", async () => {
  const calls: string[] = [];
  const fallback = createKnowledgeGraphProvenanceClient();
  const clock = installMockDate("2026-07-04T10:00:00.000Z");
  const client: KnowledgeGraphProvenanceClient = {
    getGraphSummary: () => fallback.getGraphSummary(),
    getGraphData: () => fallback.getGraphData(),
    getProvenanceTimeline: () => fallback.getProvenanceTimeline(),
    getNodeDetails: (nodeId) => fallback.getNodeDetails(nodeId),
    getEdgeDetails: (edgeId) => fallback.getEdgeDetails(edgeId),
    async refreshGraph() {
      calls.push("refreshGraph");
      return fallback.refreshGraph();
    },
    async loadDecisionProvenance(decisionId) {
      calls.push(`loadDecisionProvenance:${decisionId}`);
      return fallback.loadDecisionProvenance(decisionId);
    },
  };
  const { root } = await renderApp({ knowledgeGraphClient: client });
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: window.localStorage });
  await clickRoute("knowledge-graph");
  let text = visibleText();
  assert(text.includes("UX-003"), "Knowledge graph route should identify UX-003.");
  assert(text.includes("Graph Visualization"), "Graph panel should render.");
  assert(text.includes("Graph Filters"), "Filters should render.");
  assert(text.includes("Node Inspector"), "Node inspector should render.");
  assert(text.includes("Edge Inspector"), "Edge inspector should render.");
  assert(text.includes("Provenance Timeline"), "Provenance timeline should render.");
  assert(text.includes("Enterprise Expansion Decision"), "Default selected node should render.");

  await act(async () => {
    document.querySelector<SVGGElement>('[data-node-id="NODE-GOV-001"]')?.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Policy-gated governance mesh"), "Clicking a node should update the node inspector.");

  await act(async () => {
    document.querySelector<SVGTextElement>(".ux-graph-edge-label")?.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("EDGE-001"), "Clicking an edge should update the edge inspector.");
  assert(visibleText().includes("Source Timestamp"), "Edge Inspector should keep source timestamp label.");
  assert(visibleText().includes("01 Jul 2026, 1:45 PM"), "Source Timestamp should remain original edge metadata.");
  assert(visibleText().includes("Selected At"), "Selecting an edge should show current Selected At.");
  assert(visibleText().includes("04 Jul 2026, 3:30 PM"), "Selected At should use current browser/system time.");

  await act(async () => {
    actionButton("refresh-graph").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(calls.includes("refreshGraph"), "Refresh Graph should call adapter.");
  assert(visibleText().includes("Refreshed"), "Refresh Graph should keep refreshed timestamp visible.");
  assert(visibleText().includes("Graph refresh 1"), "Refresh Graph should increment a visible refresh counter.");
  assert(document.querySelector('[data-node-id="NODE-DEC-001"]'), "Refresh Graph should keep the graph visible.");

  await act(async () => {
    actionButton("load-provenance").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(calls.includes("loadDecisionProvenance:DEC-2026-001"), "Load Provenance should call adapter.");
  assert(visibleText().includes("Provenance Loaded"), "Load Provenance should update status.");
  assert(visibleText().includes("Full provenance path loaded from current graph snapshot."), "Load Provenance should show the required full-path action message.");
  assert(visibleText().includes("Decision created"), "Load Provenance should reveal decision-created provenance event.");
  assert(visibleText().includes("Evidence linked"), "Load Provenance should reveal evidence-linked provenance event.");
  assert(visibleText().includes("Governance criterion traced"), "Load Provenance should reveal criterion provenance event.");
  assert(visibleText().includes("Governance mesh applied"), "Load Provenance should reveal governance mesh event.");
  assert(visibleText().includes("Ranking completed"), "Load Provenance should reveal ranking provenance event.");
  assert(visibleText().includes("Recommendation generated"), "Load Provenance should reveal recommendation provenance event.");
  assert(window.localStorage.getItem("project1.ux003.provenance.timeline.v1")?.includes("Recommendation generated"), "Load Provenance should persist provenance timeline.");
  assert(document.querySelector("[data-node-id]"), "Load Provenance should keep graph nodes visible.");
  assert(visibleText().includes("Visible graph:"), "Load Provenance should keep visible graph counters rendered.");
  const highlightedEdges = document.querySelectorAll('[data-edge-id][data-provenance-highlight="true"]');
  const highlightedNodes = document.querySelectorAll('[data-node-id][data-provenance-highlight="true"]');
  assert(highlightedEdges.length > 1, "Load Provenance should highlight more than one provenance edge when data exists.");
  assert(document.querySelector('[data-edge-id="EDGE-004"][data-provenance-highlight="true"]'), "Highlighted provenance path should include ranked-by edge.");
  assert(highlightedEdges.length > 1, "Highlighted provenance path should not be limited to ranked-by edge.");
  assertEqual(highlightedNodes.length, 5, "Load Provenance should highlight all available provenance nodes.");
  assert(!document.querySelector(".ux-graph-edge.is-selected"), "Load Provenance should not add a separate selected-edge highlight.");
  assert(visibleText().includes("Source Timestamp"), "Edge Inspector should label edge metadata timestamp separately.");
  assert(visibleText().includes("01 Jul 2026, 2:50 PM"), "Source Timestamp should still show original ranked edge metadata.");
  assert(visibleText().includes("Selected At"), "Load Provenance should show selected edge action timestamp.");
  assert(visibleText().includes("Provenance Loaded At"), "Edge Inspector should show current provenance action timestamp separately.");
  assert(visibleText().includes("04 Jul 2026, 3:30 PM"), "Provenance Loaded At should use current browser/system time.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(visibleText()), "Load Provenance should not show raw ISO timestamps.");

  await act(async () => {
    actionButton("reset-graph-view").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("Enterprise Expansion Decision"), "Reset View should restore default selected node.");
  assert(text.includes("Visible graph: 5 nodes / 4 edges"), "Reset View should restore the full graph.");
  assertEqual(activeRouteId(), "knowledge-graph", "Knowledge Graph nav should be active.");
  Reflect.deleteProperty(globalThis, "localStorage");
  clock.restore();
  await act(async () => root.unmount());
});

test("React preview knowledge graph filters and preferences affect visible graph", async () => {
  const { dom, root } = await renderApp();
  Object.defineProperty(globalThis, "localStorage", { configurable: true, value: dom.window.localStorage });
  await clickRoute("knowledge-graph");

  assert(document.querySelector('[data-node-id="NODE-DEC-001"]'), "Default graph should show decision node.");
  assert(document.querySelector('[data-node-id="NODE-EVD-001"]'), "Default graph should show evidence node.");

  await selectGraphFilter("nodeType", "decision");
  assert(document.querySelector('[data-node-id="NODE-DEC-001"]'), "Node type filter should keep matching node.");
  assert(!document.querySelector('[data-node-id="NODE-EVD-001"]'), "Node type filter should hide non-matching node.");
  assert(visibleText().includes("Visible graph: 1 nodes"), "Filter status should report reduced node count.");

  dom.window.localStorage.removeItem("project1.ux003.graph.preferences.v1");
  await act(async () => {
    actionButton("load-graph-preferences").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("No saved graph preferences found. Current graph view preserved."), "Load Preferences without saved state should preserve current graph view.");
  assert(document.querySelector('[data-node-id="NODE-DEC-001"]'), "Load Preferences without saved state should keep the current graph visible.");
  assertEqual(document.querySelectorAll('[data-edge-id][data-provenance-highlight="true"]').length, 0, "Load Preferences without saved state should not create provenance highlights.");

  await act(async () => {
    actionButton("refresh-graph").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Graph refreshed from current adapter snapshot."), "Refresh Graph should show adapter snapshot message.");
  assert(visibleText().includes("Visible graph: 1 nodes"), "Refresh Graph should reapply active filters.");
  assert(visibleText().includes("Graph refresh 1"), "Refresh Graph should visibly increment refresh version in filtered view.");

  await selectGraphFilter("governanceStatus", "pending");
  assert(visibleText().includes("No graph data matches the active filters."), "No-match filters should show empty state.");

  dom.window.localStorage.setItem("project1.ux003.graph.preferences.v1", JSON.stringify({
    filters: { nodeType: "governance", relationshipType: "all", confidenceRange: "0.80-1.00", governanceStatus: "approved", timePeriod: "all", provenanceSource: "DIE Governance" },
    selectedNodeId: "NODE-GOV-001",
    selectedEdgeId: "",
  }));
  await act(async () => {
    actionButton("load-graph-preferences").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Saved graph preferences loaded."), "Load Preferences should load saved filter state.");
  assert(document.querySelector('[data-node-id="NODE-GOV-001"]'), "Saved preferences should restore matching selected node.");
  assert(!document.querySelector('[data-node-id="NODE-DEC-001"]'), "Saved preferences should keep non-matching nodes hidden.");
  assertEqual(document.querySelectorAll('[data-edge-id][data-provenance-highlight="true"]').length, 0, "Load Preferences should not apply provenance-path highlights.");

  dom.window.localStorage.setItem("project1.ux003.graph.preferences.v1", JSON.stringify({
    filters: { nodeType: "decision", relationshipType: "all", confidenceRange: "0.80-1.00", governanceStatus: "pending", timePeriod: "all", provenanceSource: "all" },
    selectedNodeId: "NODE-DEC-001",
    selectedEdgeId: "",
  }));
  await act(async () => {
    actionButton("load-graph-preferences").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(visibleText().includes("Saved preferences were invalid or too restrictive. Default graph restored."), "No-result saved preferences should fall back safely.");
  assert(document.querySelector('[data-node-id="NODE-DEC-001"]'), "No-result saved preferences should not leave graph blank.");
  assert(visibleText().includes("Visible graph: 5 nodes / 4 edges"), "Invalid preferences should restore the full graph.");

  Reflect.deleteProperty(globalThis, "localStorage");
  await act(async () => root.unmount());
});

test("React preview decision workspace renders all UX-002 panels", async () => {
  const { root } = await renderApp();
  await clickRoute("decision-workspace");
  const text = visibleText();
  assert(text.includes("UX-002"), "Decision Workspace should identify UX-002.");
  assert(text.includes("Enterprise Expansion Decision"), "Workspace header should render.");
  assert(text.includes("DEC-2026-001"), "Decision ID should render.");
  assert(text.includes("Decision Context"), "Decision context panel should render.");
  assert(text.includes("Alternatives"), "Alternatives panel should render.");
  assert(text.includes("Evaluation Results"), "Evaluation results panel should render.");
  assert(text.includes("Ranking"), "Ranking panel should render.");
  assert(text.includes("Workspace Activity"), "Timeline should render.");
  assert(text.includes("Evaluation ready"), "Evaluation action should start ready.");
  assert(text.includes("Ranking ready"), "Ranking action should start ready.");
  assert(text.includes("No evaluation run yet."), "Evaluation panel should start hidden until Run Evaluation.");
  assert(text.includes("No ranking run yet."), "Ranking panel should start hidden until Run Ranking.");
  assert(text.includes("No workspace action has been run in this preview session."), "Initial page should not pretend a workspace action just ran.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Workspace should not show raw ISO timestamps.");
  assert(timelineItems().length <= 8, "Workspace activity list should be capped.");
  assert(text.includes("Backend modules remain frozen and authoritative."), "Backend boundary note should render.");
  assertEqual(activeRouteId(), "decision-workspace", "Decision Workspace nav should become active.");
  await act(async () => root.unmount());
});

test("React preview new and load decision actions update workspace cleanly", async () => {
  const { root } = await renderApp();
  await clickRoute("decision-workspace");

  await act(async () => {
    actionButton("new-decision").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  let text = visibleText();
  assert(text.includes("DEC-UX-DRAFT-001"), "New Decision should select deterministic draft decision ID.");
  assert(text.includes("Supply Chain Optimization Decision"), "First New Decision should show the first deterministic draft snapshot.");
  assert(text.includes("Supply chain optimization"), "First New Decision should show a distinct decision domain.");
  assert(text.includes("SC-OPT-1A"), "First New Decision should show domain-specific option IDs.");
  assert(text.includes("Decision History"), "Decision Workspace should show a saved decision history section.");
  assert(text.includes("Draft"), "New Decision should show draft status.");
  assert(text.includes("New decision workspace created"), "New Decision should add activity.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "New Decision should not show raw ISO timestamps.");
  assert(timelineItems().length <= 8, "New Decision activity list should stay capped.");

  await act(async () => {
    actionButton("new-decision").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("DEC-UX-DRAFT-002"), "Second New Decision should select a different deterministic draft decision ID.");
  assert(text.includes("Healthcare Resource Allocation Decision"), "Second New Decision should show a visibly different draft title.");
  assert(text.includes("Healthcare resource allocation"), "Second New Decision should change decision context details.");
  assert(text.includes("HC-RES-2A"), "Second New Decision should show different domain-specific option IDs.");
  assertEqual(document.querySelector("#decision-workspace-title")?.textContent, "Healthcare Resource Allocation Decision", "Second New Decision should replace the active workspace while preserving history.");
  assertEqual(document.querySelectorAll("[data-history-decision-id]").length, 2, "Decision history should remember both generated frontend decisions.");
  assert(timelineItems().length <= 8, "Repeated New Decision activity list should stay capped.");

  await act(async () => {
    actionButton("load-decision").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  text = visibleText();
  assert(text.includes("DEC-UX-DRAFT-001"), "Load Decision should cycle to a saved frontend draft decision ID.");
  assert(text.includes("Supply Chain Optimization Decision"), "Load Decision should load from saved frontend decision snapshots instead of only the default.");
  assert(text.includes("Loaded"), "Load Decision should show loaded status.");
  assert(text.includes("Decision workspace loaded"), "Load Decision should add activity.");
  assert(!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(text), "Load Decision should not show raw ISO timestamps.");
  assert(timelineItems().length <= 8, "Load Decision activity list should stay capped.");
  await act(async () => root.unmount());
});

test("React preview decision workspace action buttons call adapter methods", async () => {
  const calls: string[] = [];
  const fallback = createDecisionWorkspaceClient();
  const evaluation = deferred();
  const ranking = deferred();
  let evaluationCalls = 0;
  let rankingCalls = 0;
  const client: DecisionWorkspaceClient = {
    getWorkspaceSummary: () => fallback.getWorkspaceSummary(),
    listDecisionSessions: () => fallback.listDecisionSessions(),
    getDecisionContext: () => fallback.getDecisionContext(),
    listAlternatives: () => fallback.listAlternatives(),
    async runEvaluation() {
      evaluationCalls += 1;
      calls.push("runEvaluation");
      if (evaluationCalls > 1) await evaluation.promise;
      return fallback.runEvaluation();
    },
    async runRanking() {
      rankingCalls += 1;
      calls.push("runRanking");
      if (rankingCalls > 1) await ranking.promise;
      return fallback.runRanking();
    },
    getWorkspaceTimeline: () => fallback.getWorkspaceTimeline(),
  };
  const { root } = await renderApp({ decisionWorkspaceClient: client });
  await clickRoute("decision-workspace");
  const evaluationCallsBefore = calls.filter((call) => call === "runEvaluation").length;
  const rankingCallsBefore = calls.filter((call) => call === "runRanking").length;
  const evaluationButton = actionButton("run-evaluation");
  const rankingButton = actionButton("run-ranking");

  await act(async () => {
    evaluationButton.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(evaluationButton.disabled, "Run Evaluation button should be disabled while running.");
  assert(visibleText().includes("Running evaluation..."), "Evaluation loading status should render.");
  evaluation.resolve();
  await act(async () => {
    await evaluation.promise;
  });
  assert(!actionButton("run-evaluation").disabled, "Run Evaluation button should be enabled after completion.");
  assert(visibleText().includes("Evaluation completed"), "Evaluation completed status should render.");
  assert(visibleText().includes("Current backend/fallback result snapshot revealed by Run Evaluation"), "Run Evaluation should reveal evaluation result content.");
  assert(visibleText().includes("Strategic fit"), "Run Evaluation should reveal criteria analysis.");
  assert(visibleText().includes("Evaluation completed from workspace action"), "Timeline should receive evaluation activity.");
  const visibleAlternativeIds = Array.from(document.querySelectorAll("[data-alternative-id]")).map((element) => element.getAttribute("data-alternative-id"));
  const visibleEvaluationIds = Array.from(document.querySelectorAll("[data-evaluation-id]")).map((element) => element.getAttribute("data-evaluation-id"));
  assertEqual(visibleEvaluationIds.length, visibleAlternativeIds.length, "Run Evaluation should render one evaluation result for each visible alternative.");
  assertEqual(visibleEvaluationIds.join(","), visibleAlternativeIds.join(","), "Evaluation result IDs should match the visible alternative IDs.");

  await act(async () => {
    rankingButton.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  assert(rankingButton.disabled, "Run Ranking button should be disabled while running.");
  assert(visibleText().includes("Running ranking..."), "Ranking loading status should render.");
  ranking.resolve();
  await act(async () => {
    await ranking.promise;
  });
  assert(!actionButton("run-ranking").disabled, "Run Ranking button should be enabled after completion.");
  assert(visibleText().includes("Ranking completed"), "Ranking completed status should render.");
  assert(visibleText().includes("Current backend/fallback result snapshot revealed by Run Ranking"), "Run Ranking should reveal ranking result content.");
  assert(visibleText().includes("Recommended"), "Run Ranking should reveal recommendation output.");
  assert(visibleText().includes("Ranking completed from workspace action"), "Timeline should receive ranking activity.");
  const visibleRankingIds = Array.from(document.querySelectorAll("[data-ranking-id]")).map((element) => element.getAttribute("data-ranking-id"));
  assertEqual(visibleRankingIds.length, visibleAlternativeIds.length, "Run Ranking should render one ranking row for each visible alternative.");
  assert(timelineItems().length <= 8, "Action activity list should stay capped.");
  assertEqual(countVisibleOccurrences("Evaluation completed from workspace action"), 1, "Evaluation activity should be added once.");
  assertEqual(countVisibleOccurrences("Ranking completed from workspace action"), 1, "Ranking activity should be added once.");

  const secondEvaluation = deferred();
  evaluation.resolve = secondEvaluation.resolve;
  evaluation.promise = secondEvaluation.promise;
  await act(async () => {
    actionButton("run-evaluation").dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
  });
  secondEvaluation.resolve();
  await act(async () => {
    await secondEvaluation.promise;
  });
  assertEqual(countVisibleOccurrences("Evaluation completed from workspace action"), 1, "Repeated evaluation should not spam duplicate activity.");
  assert(timelineItems().length <= 8, "Repeated actions should not exceed the activity cap.");

  assertEqual(calls.filter((call) => call === "runEvaluation").length, evaluationCallsBefore + 2, "Run Evaluation should call adapter method for each click.");
  assertEqual(calls.filter((call) => call === "runRanking").length, rankingCallsBefore + 1, "Run Ranking should call adapter method once.");
  await act(async () => root.unmount());
});

test("React preview dashboard link returns to dashboard cards", async () => {
  const { root } = await renderApp();
  await clickRoute("decision-workspace");
  assert(visibleText().includes("Decision Context"), "Decision Workspace page should appear before returning.");
  await clickRoute("dashboard");
  assert(visibleText().includes("Backend Platform"), "Dashboard cards should return after clicking Dashboard.");
  assertEqual(activeRouteId(), "dashboard", "Dashboard nav should be active after returning.");
  await act(async () => root.unmount());
});

for (const item of tests) {
  await item.run();
  console.log(`ok - ${item.name}`);
}
