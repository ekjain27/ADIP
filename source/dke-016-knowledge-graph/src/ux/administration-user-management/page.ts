import type { AdministrationRole, AdministrationSnapshot, AdministrationUser, AuditLogEntry, GovernanceControls, SystemSettings } from "./types.js";

export function renderAdministrationUserManagementCenter(snapshot: AdministrationSnapshot): string {
  return `
    <section class="ux-admin" aria-labelledby="admin-title">
      <header class="ux-workspace-header">
        <div>
          <p class="ux-module-label">UX-006</p>
          <h1 id="admin-title">Administration & User Management Center</h1>
          <div class="ux-workspace-meta">
            <span>System Status ${escapeHtml(toTitle(snapshot.summary.systemStatus))}</span>
            <span>${escapeHtml(snapshot.summary.activeOrganization)}</span>
            <span>Last Sync ${escapeHtml(formatTimestamp(snapshot.summary.lastSyncAt))}</span>
          </div>
        </div>
        <span class="ux-status-pill">${escapeHtml(toTitle(snapshot.summary.systemStatus))}</span>
      </header>
      <section class="ux-workspace-actions"><button type="button">Sync Administration</button><button type="button">Add User</button><button type="button">Export Audit Log</button></section>
      <section class="ux-workspace-grid">
        <article class="ux-panel ux-context-panel"><h2>User Management</h2><div class="ux-table-wrap"><table class="ux-table"><thead><tr><th>User ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Active</th><th>Actions</th></tr></thead><tbody>${snapshot.users.map(renderUser).join("")}</tbody></table></div></article>
        <article class="ux-panel"><h2>Roles & Permissions</h2><div class="ux-asset-grid">${snapshot.roles.map(renderRole).join("")}</div></article>
        <article class="ux-panel"><h2>Governance Controls</h2>${renderGovernance(snapshot.governanceControls)}</article>
        <article class="ux-panel ux-context-panel"><h2>Audit Log</h2><div class="ux-table-wrap"><table class="ux-table"><thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Resource</th><th>Severity</th><th>Status</th></tr></thead><tbody>${visibleAudit(snapshot.auditLog).map(renderAudit).join("")}</tbody></table></div></article>
        <article class="ux-panel"><h2>System Settings</h2>${renderSettings(snapshot.systemSettings)}</article>
        <article class="ux-panel ux-boundary-panel"><h2>Backend Boundary</h2><p>Authentication, authorization, governance, and security logic remain in backend services. UX-006 consumes administration outputs through AdministrationUserManagementClient.</p></article>
      </section>
    </section>
  `;
}

function renderUser(user: AdministrationUser): string {
  return `<tr><td>${escapeHtml(user.id)}</td><td><strong>${escapeHtml(user.name)}</strong></td><td>${escapeHtml(user.email)}</td><td>${escapeHtml(user.role)}</td><td>${escapeHtml(toTitle(user.status))}</td><td>${escapeHtml(formatTimestamp(user.lastActiveAt))}</td><td><button type="button">View</button><button type="button">Change Role</button><button type="button">${user.status === "active" ? "Suspend" : "Activate"}</button></td></tr>`;
}

function renderRole(role: AdministrationRole): string {
  return `<section class="ux-card ux-status-card"><span class="ux-status-pill">${escapeHtml(role.accessLevel)}</span><h3>${escapeHtml(role.role)}</h3><strong>${role.permissionCount} permissions</strong><p>${escapeHtml(role.governanceScope)}</p></section>`;
}

function renderGovernance(governance: GovernanceControls): string {
  return `<dl class="ux-inspector-list"><div><dt>Governance Mode</dt><dd>${escapeHtml(governance.governanceMode)}</dd></div><div><dt>Approval Policy</dt><dd>${escapeHtml(governance.approvalPolicy)}</dd></div><div><dt>Compliance Status</dt><dd>${escapeHtml(governance.complianceStatus)}</dd></div><div><dt>Override Policy</dt><dd>${escapeHtml(governance.overridePolicy)}</dd></div><div><dt>Risk Threshold</dt><dd>${escapeHtml(governance.riskThreshold)}</dd></div></dl>`;
}

function renderSettings(settings: SystemSettings): string {
  return `<dl class="ux-inspector-list"><div><dt>Environment</dt><dd>${escapeHtml(settings.environment)}</dd></div><div><dt>Release Version</dt><dd>${escapeHtml(settings.releaseVersion)}</dd></div><div><dt>Regression Baseline</dt><dd>${escapeHtml(settings.regressionBaseline)}</dd></div><div><dt>Monitoring Mode</dt><dd>${escapeHtml(settings.monitoringMode)}</dd></div><div><dt>Compliance Mode</dt><dd>${escapeHtml(settings.complianceMode)}</dd></div></dl>`;
}

function renderAudit(entry: AuditLogEntry): string {
  return `<tr><td>${escapeHtml(formatTimestamp(entry.timestamp))}</td><td>${escapeHtml(entry.user)}</td><td>${escapeHtml(entry.action)}</td><td>${escapeHtml(entry.resource)}</td><td>${escapeHtml(toTitle(entry.severity))}</td><td>${escapeHtml(toTitle(entry.status))}</td></tr>`;
}

function visibleAudit(entries: readonly AuditLogEntry[]): readonly AuditLogEntry[] {
  return [...entries].sort((left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp)).slice(0, 8);
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric", hour: "numeric", minute: "2-digit", hour12: true }).format(date).replace(" am", " AM").replace(" pm", " PM");
}

function toTitle(value: string): string {
  return value.replaceAll("-", " ").replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}
