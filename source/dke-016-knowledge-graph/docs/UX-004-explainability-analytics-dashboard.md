# UX-004 Explainability & Analytics Dashboard

## Purpose

UX-004 adds an enterprise explainability and analytics dashboard inside the existing application shell. It visualizes backend explainability, evaluation, ranking, optimization, governance, performance, and recommendation outputs.

The UI does not implement XAI algorithms, scoring, ranking, optimization, forecasting, or governance logic.

## Architecture

The route is implemented as a UX/application-layer module under `src/ux/explainability-analytics`. React and static shell rendering consume a typed `ExplainabilityAnalyticsSnapshot`.

## Backend Boundary

UX-004 uses `ExplainabilityAnalyticsClient` with:

- `getExplainabilitySummary()`
- `getDecisionReasoning()`
- `getFeatureImportance()`
- `getAnalyticsMetrics()`
- `getRecommendationSummary()`
- `getTimeline()`
- `generateExplanation()`
- `refreshAnalytics()`

## UI Interactions

- Generate Explanation calls the adapter, shows loading, updates status/timestamp, and adds timeline data returned by the adapter.
- Refresh Analytics calls the adapter and refreshes visible metrics/status.
- Export Report creates a JSON download from the currently displayed snapshot only.

## Fallback Policy

Live frontend explainability endpoints were not clear in the current repository. UX-004 therefore uses deterministic UX-layer fallback data isolated behind the adapter. Future backend API wiring should replace adapter internals only.

## Extension Notes

UX-005 documentation/patent/research surfaces should consume documentation and publication outputs through their own adapters and may link to UX-004 by decision ID, explanation timestamp, recommendation ID, and governance status.
