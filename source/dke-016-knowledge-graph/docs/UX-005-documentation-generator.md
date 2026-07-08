# UX-005 Documentation / Patent / Research Generator UI

## Purpose

UX-005 replaces the Documentation / Patent / Research placeholder with a thin enterprise UI for viewing and requesting generated documentation, patent preparation assets, and research paper assets.

The UI does not generate documentation, patent claims, figures, or research content itself. It consumes backend-owned outputs through `DocumentationGenerationClient`.

## Page Structure

- Header with generator status, current project, and last generation time.
- Documentation Panel for Architecture, API, User Guide, Technical Guide, and Deployment Guide.
- Patent Panel for Patent Draft, Claims, Figures, Prior Art Summary, and Filing Status.
- Research Paper Panel for Abstract, Introduction, Methodology, Experiments, Results, and References.
- Generation Activity timeline for documentation, patent, research, refresh, and package export events.
- Backend Boundary panel explaining that backend modules remain authoritative.

## Adapter Boundary

UX-005 uses `DocumentationGenerationClient` with these methods:

- `getDocumentation()`
- `getPatent()`
- `getResearchPaper()`
- `getSummary()`
- `getActivity()`
- `generateDocumentation()`
- `generatePatent()`
- `generateResearchPaper()`
- `refresh()`
- `exportPackage()`

If live backend endpoints are not discoverable, the UX layer uses deterministic fallback data isolated in `src/ux/documentation-generator/client.ts`.

## Time Handling

All displayed UX-005 timestamps are formatted in `Asia/Kolkata` using readable local time, such as `02 Jul 2026, 10:45 PM`. Raw ISO timestamps must not be rendered in the UI.

## Extension Notes

Future UX modules should extend the shell by adding a typed client, a static route renderer, a React preview page, and focused tests. Business logic and generation logic must remain behind backend APIs.

## Files Added

- `src/ux/documentation-generator/types.ts`
- `src/ux/documentation-generator/client.ts`
- `src/ux/documentation-generator/page.ts`
- `src/ux/documentation-generator/index.ts`
- `docs/UX-005-documentation-generator.md`
