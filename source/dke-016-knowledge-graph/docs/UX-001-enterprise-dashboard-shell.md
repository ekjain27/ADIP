# UX-001 Enterprise Dashboard Shell

UX-001 introduces the first application-layer module for the AI Decision Intelligence Platform. It is a thin enterprise dashboard shell that presents backend-owned status information, route foundations, layout primitives, and UX roadmap placeholders without duplicating backend decision logic.

## Layout Structure

- `ux-shell`: responsive application frame with light and dark theme tokens.
- `ux-sidebar`: primary navigation for the UX roadmap.
- `ux-topbar`: route title and backend boundary indicator.
- `ux-main`: route content outlet.
- `ux-dashboard`: implemented dashboard home view.

## Route Map

- `/` - Dashboard, implemented in UX-001.
- `/decision-workspace` - Coming in UX-002.
- `/knowledge-graph` - Coming in UX-003.
- `/explainability` - Coming in UX-004.
- `/documentation` - Coming in UX-005.
- `/administration` - Coming in UX-006.
- `/platform-integration` - Coming in UX-007.

## Backend Boundary Rule

The shell consumes platform state only through `BackendStatusClient`. UX components render data from the adapter and must not implement decision, governance, provenance, recommendation, validation, release, patent, documentation, or research-paper logic. The current deterministic adapter is isolated in the UX application layer so future live backend endpoints can replace it without changing components.

## Future Extension

Future UX modules should add routes through `UX_ROADMAP_NAVIGATION`, implement route rendering in the application shell route resolver, and consume backend data through dedicated typed clients. Route components should remain presentation-focused and keep backend modules authoritative.

## Local Preview

UX-001 includes a minimal Vite/React preview that mounts the existing shell renderer without moving backend logic into the browser layer.

```bash
npm run dev
```

The dev server starts the browser app from `index.html` and `src/ux/main.tsx`. The React preview in `src/ux/App.tsx` renders the shell directly and uses the existing `BackendStatusClient` abstraction.

Sidebar navigation is handled by React state in the preview app, with hash routes such as `#/decision-workspace` and `#/knowledge-graph` kept in sync for shareable browser URLs. The sidebar, topbar, dashboard, and placeholder pages are rendered as React components; routing does not depend on `dangerouslySetInnerHTML` or delegated link-click capture. Direct browser refresh on path routes such as `/decision-workspace` also resolves to the matching placeholder. Placeholder routes do not add business logic; they only describe future UX modules and preserve the backend API boundary.

## Freeze Readiness

The UX-001 shell is designed as a commercial-ready foundation layer: restrained enterprise sidebar navigation, active route state, responsive layout bands, dashboard KPI/status hierarchy, architecture mechanism cards, polished placeholder pages, and light/dark theme tokens. Future modules should extend these primitives without moving backend logic into the UI.

## Files Added

- `src/ux/application-shell/types.ts`
- `src/ux/application-shell/navigation.ts`
- `src/ux/application-shell/platformStatusClient.ts`
- `src/ux/application-shell/dashboard.ts`
- `src/ux/application-shell/routes.ts`
- `src/ux/application-shell/layout.ts`
- `src/ux/application-shell/index.ts`
- `src/ux/index.ts`
- `src/ux/App.tsx`
- `src/ux/main.tsx`
- `src/ux/tests/ux001.test.ts`
- `index.html`
- `vite.config.ts`
- `docs/UX-001-enterprise-dashboard-shell.md`
