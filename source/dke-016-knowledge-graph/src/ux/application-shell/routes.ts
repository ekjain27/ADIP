import { createDashboardViewModel, renderDashboard } from "./dashboard.js";
import { createAdministrationUserManagementClient, getAdministrationSnapshot, renderAdministrationUserManagementCenter } from "../administration-user-management/index.js";
import { createDecisionWorkspaceClient, getDecisionWorkspaceSnapshot, renderDecisionWorkspace } from "../decision-workspace/index.js";
import { createDocumentationGenerationClient, getDocumentationGenerationSnapshot, renderDocumentationGenerationCenter } from "../documentation-generator/index.js";
import { createEnterpriseIntegrationClient, getEnterpriseIntegrationSnapshot, renderEnterprisePlatformIntegrationConsole } from "../enterprise-platform-integration/index.js";
import { createExplainabilityAnalyticsClient, getExplainabilityAnalyticsSnapshot, renderExplainabilityAnalyticsDashboard } from "../explainability-analytics/index.js";
import { createKnowledgeGraphProvenanceClient, getKnowledgeGraphSnapshot, renderKnowledgeGraphExplorer } from "../knowledge-graph-provenance/index.js";
import { findNavigationEntry, normalizeRoutePath, UX_ROADMAP_NAVIGATION } from "./navigation.js";
import type { BackendStatusClient, ShellRouteView } from "./types.js";
import type { AdministrationUserManagementClient } from "../administration-user-management/index.js";
import type { DecisionWorkspaceClient } from "../decision-workspace/index.js";
import type { DocumentationGenerationClient } from "../documentation-generator/index.js";
import type { EnterpriseIntegrationClient } from "../enterprise-platform-integration/index.js";
import type { ExplainabilityAnalyticsClient } from "../explainability-analytics/index.js";
import type { KnowledgeGraphProvenanceClient } from "../knowledge-graph-provenance/index.js";

export async function resolveShellRoute(
  path: string | undefined,
  client: BackendStatusClient,
  decisionWorkspaceClient: DecisionWorkspaceClient = createDecisionWorkspaceClient(),
  knowledgeGraphClient: KnowledgeGraphProvenanceClient = createKnowledgeGraphProvenanceClient(),
  explainabilityClient: ExplainabilityAnalyticsClient = createExplainabilityAnalyticsClient(),
  documentationClient: DocumentationGenerationClient = createDocumentationGenerationClient(),
  administrationClient: AdministrationUserManagementClient = createAdministrationUserManagementClient(),
  enterpriseIntegrationClient: EnterpriseIntegrationClient = createEnterpriseIntegrationClient(),
): Promise<ShellRouteView> {
  const routePath = normalizeRoutePath(path);
  const entry = findNavigationEntry(routePath);

  if (entry.id === "dashboard") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderDashboard(await createDashboardViewModel(client)),
    };
  }

  if (entry.id === "decision-workspace") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderDecisionWorkspace(await getDecisionWorkspaceSnapshot(decisionWorkspaceClient)),
    };
  }

  if (entry.id === "knowledge-graph") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderKnowledgeGraphExplorer(await getKnowledgeGraphSnapshot(knowledgeGraphClient)),
    };
  }

  if (entry.id === "explainability") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderExplainabilityAnalyticsDashboard(await getExplainabilityAnalyticsSnapshot(explainabilityClient)),
    };
  }

  if (entry.id === "documentation") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderDocumentationGenerationCenter(await getDocumentationGenerationSnapshot(documentationClient)),
    };
  }

  if (entry.id === "administration") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderAdministrationUserManagementCenter(await getAdministrationSnapshot(administrationClient)),
    };
  }

  if (entry.id === "platform-integration") {
    return {
      path: entry.path,
      title: entry.label,
      contentHtml: renderEnterprisePlatformIntegrationConsole(await getEnterpriseIntegrationSnapshot(enterpriseIntegrationClient)),
    };
  }

  return {
    path: entry.path,
    title: entry.label,
    contentHtml: renderPlaceholderRoute(entry.uxModule, entry.label, entry.purpose),
  };
}

export function getRouteMap(): readonly string[] {
  return UX_ROADMAP_NAVIGATION.map((entry) => entry.path);
}

function renderPlaceholderRoute(uxModule: string, title: string, purpose: string): string {
  return `
    <section class="ux-placeholder" aria-label="${escapeHtml(title)}" data-ux-module="${escapeHtml(uxModule)}">
      <p class="ux-module-label">${escapeHtml(uxModule)}</p>
      <h1>${escapeHtml(title)}</h1>
      <p class="ux-placeholder-purpose">${escapeHtml(purpose)}</p>
      <p class="ux-placeholder-message">Coming in future UX implementation</p>
      <p class="ux-boundary-note">Backend modules are frozen; this UI route will consume backend APIs only.</p>
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
