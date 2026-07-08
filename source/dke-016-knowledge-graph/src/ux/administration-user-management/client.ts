import type { AdministrationRole, AdministrationSnapshot, AdministrationSummary, AdministrationUser, AdministrationUserManagementClient, AuditLogEntry, GovernanceControls, SystemSettings } from "./types.js";

const initialSyncAt = new Date().toISOString();
export const ADMINISTRATION_STORAGE_KEY = "project1.ux006.administration.snapshot.v1";

function minutesBefore(timestamp: string, minutes: number): string {
  return new Date(Date.parse(timestamp) - minutes * 60 * 1000).toISOString();
}

const summary: AdministrationSummary = {
  systemStatus: "ready",
  activeOrganization: "Decision Intelligence Enterprise",
  lastSyncAt: initialSyncAt,
};

const users: readonly AdministrationUser[] = [
  { id: "USR-001", name: "Asha Raman", email: "asha.raman@example.com", role: "Decision Admin", status: "active", lastActiveAt: minutesBefore(initialSyncAt, 12) },
  { id: "USR-002", name: "Mira Shah", email: "mira.shah@example.com", role: "Governance Reviewer", status: "active", lastActiveAt: minutesBefore(initialSyncAt, 31) },
  { id: "USR-003", name: "Dev Malhotra", email: "dev.malhotra@example.com", role: "Analyst", status: "suspended", lastActiveAt: minutesBefore(initialSyncAt, 88) },
];

const roles: readonly AdministrationRole[] = [
  { role: "Decision Admin", permissionCount: 42, accessLevel: "Enterprise", governanceScope: "Full decision governance" },
  { role: "Governance Reviewer", permissionCount: 27, accessLevel: "Controlled", governanceScope: "Policy review and approvals" },
  { role: "Analyst", permissionCount: 18, accessLevel: "Workspace", governanceScope: "Decision analysis views" },
  { role: "Auditor", permissionCount: 14, accessLevel: "Read Only", governanceScope: "Audit and evidence review" },
];

const governanceControls: GovernanceControls = {
  governanceMode: "Policy gated",
  approvalPolicy: "Two-stage approval",
  complianceStatus: "Compliant",
  overridePolicy: "Executive approval required",
  riskThreshold: "Medium",
};

const auditLog: readonly AuditLogEntry[] = [
  { id: "AUD-001", timestamp: minutesBefore(initialSyncAt, 5), user: "System", action: "Administration synced", resource: "Admin Center", severity: "info", status: "complete" },
  { id: "AUD-002", timestamp: minutesBefore(initialSyncAt, 18), user: "Asha Raman", action: "Role reviewed", resource: "Decision Admin", severity: "info", status: "complete" },
  { id: "AUD-003", timestamp: minutesBefore(initialSyncAt, 46), user: "Mira Shah", action: "Governance policy checked", resource: "Approval Policy", severity: "warning", status: "review" },
];

const systemSettings: SystemSettings = {
  environment: "Production Preview",
  releaseVersion: "v1.0.2-backend-complete",
  regressionBaseline: "606 / 606 tests passing",
  monitoringMode: "Decision health monitoring",
  complianceMode: "Enterprise governance",
};

const baseSnapshot: AdministrationSnapshot = { summary, users, roles, governanceControls, auditLog, systemSettings };

function getBrowserStorage(): Storage | null {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

function isAdministrationSummary(value: unknown): value is AdministrationSummary {
  if (!value || typeof value !== "object") return false;
  const summaryValue = value as Partial<AdministrationSummary>;
  return typeof summaryValue.systemStatus === "string"
    && typeof summaryValue.activeOrganization === "string"
    && typeof summaryValue.lastSyncAt === "string";
}

function isAdministrationUser(value: unknown): value is AdministrationUser {
  if (!value || typeof value !== "object") return false;
  const user = value as Partial<AdministrationUser>;
  return typeof user.id === "string"
    && typeof user.name === "string"
    && typeof user.email === "string"
    && typeof user.role === "string"
    && (user.status === "active" || user.status === "suspended")
    && typeof user.lastActiveAt === "string";
}

function isAuditLogEntry(value: unknown): value is AuditLogEntry {
  if (!value || typeof value !== "object") return false;
  const entry = value as Partial<AuditLogEntry>;
  return typeof entry.id === "string"
    && typeof entry.timestamp === "string"
    && typeof entry.user === "string"
    && typeof entry.action === "string"
    && typeof entry.resource === "string"
    && (entry.severity === "info" || entry.severity === "warning" || entry.severity === "critical")
    && (entry.status === "complete" || entry.status === "review");
}

function loadStoredSnapshot(): Pick<AdministrationSnapshot, "summary" | "users" | "auditLog"> | null {
  const storage = getBrowserStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(ADMINISTRATION_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<AdministrationSnapshot>;
    if (!isAdministrationSummary(parsed.summary)) return null;
    if (!Array.isArray(parsed.users) || !parsed.users.every(isAdministrationUser)) return null;
    if (!Array.isArray(parsed.auditLog) || !parsed.auditLog.every(isAuditLogEntry)) return null;
    return { summary: parsed.summary, users: parsed.users, auditLog: parsed.auditLog };
  } catch {
    return null;
  }
}

function saveStoredSnapshot(summaryToSave: AdministrationSummary, usersToSave: readonly AdministrationUser[], auditLogToSave: readonly AuditLogEntry[]): void {
  const storage = getBrowserStorage();
  if (!storage) return;
  try {
    storage.setItem(ADMINISTRATION_STORAGE_KEY, JSON.stringify({
      summary: summaryToSave,
      users: usersToSave,
      auditLog: auditLogToSave,
    }));
  } catch {
    // Persistence is a UX preview convenience only; localStorage failures should not break the page.
  }
}

function getNextUserIndexFromUsers(currentUsers: readonly AdministrationUser[]): number {
  const highest = currentUsers.reduce((max, user) => {
    const match = /^ADMIN-UX-USER-(\d+)$/.exec(user.id);
    if (!match) return max;
    return Math.max(max, Number.parseInt(match[1], 10));
  }, 0);
  return highest + 1;
}

function withAudit(event: AuditLogEntry, entries: readonly AuditLogEntry[]): readonly AuditLogEntry[] {
  return [event, ...entries.filter((item) => item.id !== event.id)].slice(0, 8);
}

function createSnapshot(
  currentUsers: readonly AdministrationUser[],
  currentAuditLog: readonly AuditLogEntry[],
  status: AdministrationSummary["systemStatus"] = "ready",
  timestamp = initialSyncAt,
): AdministrationSnapshot {
  return {
    ...baseSnapshot,
    summary: { ...baseSnapshot.summary, systemStatus: status, lastSyncAt: timestamp },
    users: currentUsers,
    auditLog: currentAuditLog,
  };
}

export class DeterministicAdministrationUserManagementClient implements AdministrationUserManagementClient {
  private currentSummary: AdministrationSummary = baseSnapshot.summary;
  private currentUsers: readonly AdministrationUser[] = baseSnapshot.users;
  private currentAuditLog: readonly AuditLogEntry[] = baseSnapshot.auditLog;
  private nextUserIndex = 1;

  constructor() {
    const stored = loadStoredSnapshot();
    if (!stored) return;
    this.currentSummary = stored.summary;
    this.currentUsers = stored.users;
    this.currentAuditLog = stored.auditLog;
    this.nextUserIndex = getNextUserIndexFromUsers(stored.users);
  }

  async getAdministrationSummary(): Promise<AdministrationSummary> { return this.currentSummary; }
  async listUsers(): Promise<readonly AdministrationUser[]> { return this.currentUsers; }
  async listRoles(): Promise<readonly AdministrationRole[]> { return baseSnapshot.roles; }
  async getGovernanceControls(): Promise<GovernanceControls> { return baseSnapshot.governanceControls; }
  async getAuditLog(): Promise<readonly AuditLogEntry[]> { return this.currentAuditLog; }
  async getSystemSettings(): Promise<SystemSettings> { return baseSnapshot.systemSettings; }

  private actionSnapshot(status: AdministrationSummary["systemStatus"], event: AuditLogEntry, usersToKeep: readonly AdministrationUser[] = this.currentUsers): AdministrationSnapshot {
    this.currentSummary = { ...baseSnapshot.summary, systemStatus: status, lastSyncAt: event.timestamp };
    this.currentUsers = usersToKeep;
    this.currentAuditLog = withAudit(event, this.currentAuditLog);
    saveStoredSnapshot(this.currentSummary, this.currentUsers, this.currentAuditLog);
    return createSnapshot(this.currentUsers, this.currentAuditLog, status, event.timestamp);
  }

  async syncAdministration(): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    return this.actionSnapshot("synced", { id: "AUD-SYNC", timestamp, user: "System", action: "Administration synced", resource: "Admin Center", severity: "info", status: "complete" });
  }
  async refreshAdministration(): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    return this.actionSnapshot("refreshed", { id: `AUD-REFRESH-${timestamp}`, timestamp, user: "UX Administrator", action: "Administration refreshed", resource: "Admin Center", severity: "info", status: "complete" });
  }
  async addUser(): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    const nextIndex = this.nextUserIndex;
    this.nextUserIndex += 1;
    const id = `ADMIN-UX-USER-${String(nextIndex).padStart(3, "0")}`;
    const newUser: AdministrationUser = { id, name: `UX Admin User ${nextIndex}`, email: `ux-admin-user-${String(nextIndex).padStart(3, "0")}@example.com`, role: "Analyst", status: "active", lastActiveAt: timestamp };
    return this.actionSnapshot("user-added", { id: `AUD-ADD-USER-${id}`, timestamp, user: "System", action: "User added", resource: newUser.id, severity: "info", status: "complete" }, [newUser, ...this.currentUsers]);
  }
  async removeUser(userId: string): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    const removedUser = this.currentUsers.find((user) => user.id === userId);
    if (!removedUser) return createSnapshot(this.currentUsers, this.currentAuditLog, this.currentSummary.systemStatus, this.currentSummary.lastSyncAt);
    const nextUsers = this.currentUsers.filter((user) => user.id !== userId);
    return this.actionSnapshot("user-removed", { id: `AUD-REMOVE-${userId}-${timestamp}`, timestamp, user: "UX Administrator", action: "User removed", resource: `${removedUser.id} ${removedUser.name}`, severity: "warning", status: "complete" }, nextUsers);
  }
  async changeUserRole(userId: string, role: string): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    const nextUsers = this.currentUsers.map((user) => user.id === userId ? { ...user, role, lastActiveAt: timestamp } : user);
    return this.actionSnapshot("role-updated", { id: `AUD-ROLE-${userId}`, timestamp, user: "System", action: "Role changed", resource: userId, severity: "info", status: "complete" }, nextUsers);
  }
  async toggleUserStatus(userId: string): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    const nextUsers = this.currentUsers.map((user): AdministrationUser => user.id === userId ? { ...user, status: user.status === "active" ? "suspended" : "active", lastActiveAt: timestamp } : user);
    return this.actionSnapshot("status-updated", { id: `AUD-STATUS-${userId}`, timestamp, user: "System", action: "User status toggled", resource: userId, severity: "warning", status: "complete" }, nextUsers);
  }
  async exportAuditLog(): Promise<AdministrationSnapshot> {
    const timestamp = new Date().toISOString();
    return this.actionSnapshot("audit-exported", { id: "AUD-EXPORT", timestamp, user: "System", action: "Audit log exported", resource: "Audit Log", severity: "info", status: "complete" });
  }
}

export function createAdministrationUserManagementClient(): AdministrationUserManagementClient {
  return new DeterministicAdministrationUserManagementClient();
}

export async function getAdministrationSnapshot(client: AdministrationUserManagementClient): Promise<AdministrationSnapshot> {
  const [summary, users, roles, governanceControls, auditLog, systemSettings] = await Promise.all([client.getAdministrationSummary(), client.listUsers(), client.listRoles(), client.getGovernanceControls(), client.getAuditLog(), client.getSystemSettings()]);
  return { summary, users, roles, governanceControls, auditLog, systemSettings };
}
