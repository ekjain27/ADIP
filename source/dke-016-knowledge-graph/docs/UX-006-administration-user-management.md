# UX-006 Administration & User Management

## Purpose

UX-006 replaces the Administration placeholder with a thin enterprise UI for administration visibility, user management, roles, governance controls, audit log review, and system settings.

Authentication, authorization, governance, and security logic remain backend responsibilities. The UI consumes outputs and action results through `AdministrationUserManagementClient`.

## Page Structure

- Administration Header with system status, active organization, and last sync time.
- User Management table with user ID, name, email, role, status, last active, and row actions.
- Roles & Permissions cards.
- Governance Controls panel.
- Audit Log table.
- System Settings panel.
- Backend Boundary panel.

## Adapter Boundary

UX-006 uses `AdministrationUserManagementClient`:

- `getAdministrationSummary()`
- `listUsers()`
- `listRoles()`
- `getGovernanceControls()`
- `getAuditLog()`
- `getSystemSettings()`
- `syncAdministration()`
- `addUser()`
- `changeUserRole()`
- `toggleUserStatus()`
- `exportAuditLog()`

If backend endpoints are unavailable, deterministic fallback data is isolated in the UX layer.

## Rules

- No authentication logic is implemented in UI.
- No authorization policy is evaluated in UI.
- No backend module is modified.
- Timestamps render in `Asia/Kolkata` readable format.
- Raw ISO timestamps must not be rendered.
