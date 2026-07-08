export type ShellTheme = "light" | "dark";

export type RouteStatus = "implemented" | "placeholder";

export interface NavigationEntry {
  readonly id: string;
  readonly label: string;
  readonly path: string;
  readonly uxModule: string;
  readonly purpose: string;
  readonly status: RouteStatus;
}

export interface StatusCard {
  readonly id: string;
  readonly title: string;
  readonly status: "complete" | "ready" | "healthy" | "passing";
  readonly detail: string;
}

export interface ArchitectureMechanismCard {
  readonly id: string;
  readonly title: string;
  readonly backendModule: string;
  readonly description: string;
}

export interface RegressionBaseline {
  readonly passing: number;
  readonly total: number;
}

export interface PlatformStatusSnapshot {
  readonly platformStatus: readonly StatusCard[];
  readonly mechanisms: readonly ArchitectureMechanismCard[];
  readonly regressionBaseline: RegressionBaseline;
  readonly releaseTags: readonly string[];
}

export interface BackendStatusClient {
  getPlatformStatus(): Promise<PlatformStatusSnapshot>;
}

export interface DashboardViewModel {
  readonly title: string;
  readonly subtitle: string;
  readonly statusCards: readonly StatusCard[];
  readonly mechanisms: readonly ArchitectureMechanismCard[];
  readonly regressionBaseline: RegressionBaseline;
  readonly releaseTags: readonly string[];
}

export interface ShellRouteView {
  readonly path: string;
  readonly title: string;
  readonly contentHtml: string;
}

export interface ShellRenderOptions {
  readonly routePath?: string;
  readonly theme?: ShellTheme;
  readonly navigationMode?: "path" | "hash";
}
