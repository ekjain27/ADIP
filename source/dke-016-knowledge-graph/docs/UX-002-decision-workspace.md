# UX-002 Decision Workspace

## Purpose

UX-002 adds the Decision Workspace page inside the frozen UX-001 Enterprise Dashboard Shell. It gives users a workspace-level view of decision sessions, decision context, alternatives, backend-produced evaluation results, backend-produced ranking results, and workspace activity.

The page is an application-layer surface only. It does not implement evaluation, ranking, simulation, optimization, provenance, or governance algorithms.

## Page Layout

- Workspace header: title, status, decision ID, session ID, last updated timestamp, and primary actions.
- Decision context panel: objective, domain, constraints, stakeholders, risk preference, and governance mode.
- Decision sessions panel: available sessions and status metadata.
- Alternatives panel: alternative ID, title, summary, expected impact, risk level, and status.
- Evaluation results panel: backend output scores, confidence, criteria breakdown, strengths, weaknesses, and warnings.
- Ranking panel: backend output rank, alternative, score, explanation summary, and recommended flag.
- Workspace activity timeline: created, context loaded, alternatives generated, evaluation completed, ranking completed, and governance checked.
- Backend boundary panel: visible confirmation that backend modules remain frozen and authoritative.

## Adapter Boundary

UX-002 uses `DecisionWorkspaceClient` in `src/ux/decision-workspace/client.ts`.

Current adapter methods:

- `getWorkspaceSummary()`
- `listDecisionSessions()`
- `getDecisionContext()`
- `listAlternatives()`
- `runEvaluation()`
- `runRanking()`
- `getWorkspaceTimeline()`

React components and static shell route rendering consume `DecisionWorkspaceSnapshot` only. The UI maps data into controls and panels; it does not calculate scores, ranks, recommendations, confidence, warnings, or governance state.

## Backend Outputs Consumed

The UX layer is prepared to consume:

- workspace/session metadata
- decision context
- alternatives
- evaluation outputs
- ranking outputs
- activity/timeline status

Live frontend-facing decision workspace endpoints were not clear in the current repository, so UX-002 uses deterministic fallback data isolated in the UX adapter. This fallback is test/demo data only and can be replaced by backend API calls inside the adapter without changing UI components.

## Intentionally Not Implemented In UI

- decision evaluation algorithms
- ranking algorithms
- recommendation logic
- governance policy execution
- provenance graph construction
- explainability generation
- simulation or optimization workflows

## Extension Notes

Future UX modules should extend the shell by adding route-specific pages and typed UX adapters. UX-003 provenance and explainability modules should consume backend provenance/XAI outputs through their own clients, then link from UX-002 using decision ID, session ID, alternative ID, and evaluation/ranking result identifiers.

Do not move backend logic into React components. Keep backend discovery and fallback/demo data behind UX service adapters.

## Files Added

- `src/ux/decision-workspace/types.ts`
- `src/ux/decision-workspace/client.ts`
- `src/ux/decision-workspace/page.ts`
- `src/ux/decision-workspace/index.ts`
- `docs/UX-002-decision-workspace.md`
