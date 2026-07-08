import type { NavigationEntry } from "./types.js";

export const UX_ROADMAP_NAVIGATION: readonly NavigationEntry[] = [
  { id: "dashboard", label: "Dashboard", path: "/", uxModule: "UX-001", purpose: "Enterprise platform status overview.", status: "implemented" },
  { id: "decision-workspace", label: "Decision Workspace", path: "/decision-workspace", uxModule: "UX-002", purpose: "Main user workspace for decision sessions, context, alternatives, backend evaluation outputs, and backend ranking outputs.", status: "implemented" },
  { id: "knowledge-graph", label: "Knowledge Graph & Provenance", path: "/knowledge-graph", uxModule: "UX-003", purpose: "Knowledge graph and provenance exploration surface.", status: "implemented" },
  { id: "explainability", label: "Explainability & Analytics", path: "/explainability", uxModule: "UX-004", purpose: "Explainability, analytics, and decision insight views.", status: "implemented" },
  { id: "documentation", label: "Documentation / Patent / Research", path: "/documentation", uxModule: "UX-005", purpose: "Documentation, patent preparation, and research paper surfaces.", status: "implemented" },
  { id: "administration", label: "Administration", path: "/administration", uxModule: "UX-006", purpose: "Administrative configuration and governance operations.", status: "implemented" },
  { id: "platform-integration", label: "Platform Integration", path: "/platform-integration", uxModule: "UX-007", purpose: "Platform integration visibility and API boundary readiness.", status: "implemented" },
];

export function findNavigationEntry(path: string): NavigationEntry {
  const normalized = normalizeRoutePath(path);
  return UX_ROADMAP_NAVIGATION.find((entry) => entry.path === normalized) ?? UX_ROADMAP_NAVIGATION[0];
}

export function normalizeRoutePath(path: string | undefined): string {
  if (!path || !path.trim()) return "/";
  const trimmed = path.trim();
  if (trimmed.startsWith("#")) return normalizeRoutePath(trimmed.slice(1));
  if (trimmed === "/dashboard") return "/";
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

export function toHashRoute(path: string | undefined): string {
  return `#${normalizeRoutePath(path)}`;
}
