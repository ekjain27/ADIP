export interface AdministrationSummary {
  readonly systemStatus: "ready" | "synced" | "refreshed" | "user-added" | "user-removed" | "role-updated" | "status-updated" | "audit-exported";
  readonly activeOrganization: string;
  readonly lastSyncAt: string;
}

export interface AdministrationUser {
  readonly id: string;
  readonly name: string;
  readonly email: string;
  readonly role: string;
  readonly status: "active" | "suspended";
  readonly lastActiveAt: string;
}

export interface AdministrationRole {
  readonly role: string;
  readonly permissionCount: number;
  readonly accessLevel: string;
  readonly governanceScope: string;
}

export interface GovernanceControls {
  readonly governanceMode: string;
  readonly approvalPolicy: string;
  readonly complianceStatus: string;
  readonly overridePolicy: string;
  readonly riskThreshold: string;
}

export interface AuditLogEntry {
  readonly id: string;
  readonly timestamp: string;
  readonly user: string;
  readonly action: string;
  readonly resource: string;
  readonly severity: "info" | "warning" | "critical";
  readonly status: "complete" | "review";
}

export interface SystemSettings {
  readonly environment: string;
  readonly releaseVersion: string;
  readonly regressionBaseline: string;
  readonly monitoringMode: string;
  readonly complianceMode: string;
}

export interface AdministrationSnapshot {
  readonly summary: AdministrationSummary;
  readonly users: readonly AdministrationUser[];
  readonly roles: readonly AdministrationRole[];
  readonly governanceControls: GovernanceControls;
  readonly auditLog: readonly AuditLogEntry[];
  readonly systemSettings: SystemSettings;
}

export interface AdministrationUserManagementClient {
  getAdministrationSummary(): Promise<AdministrationSummary>;
  listUsers(): Promise<readonly AdministrationUser[]>;
  listRoles(): Promise<readonly AdministrationRole[]>;
  getGovernanceControls(): Promise<GovernanceControls>;
  getAuditLog(): Promise<readonly AuditLogEntry[]>;
  getSystemSettings(): Promise<SystemSettings>;
  syncAdministration(): Promise<AdministrationSnapshot>;
  refreshAdministration(): Promise<AdministrationSnapshot>;
  addUser(): Promise<AdministrationSnapshot>;
  removeUser(userId: string): Promise<AdministrationSnapshot>;
  changeUserRole(userId: string, role: string): Promise<AdministrationSnapshot>;
  toggleUserStatus(userId: string): Promise<AdministrationSnapshot>;
  exportAuditLog(): Promise<AdministrationSnapshot>;
}
