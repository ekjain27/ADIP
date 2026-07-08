# UX-007 Enterprise Platform Integration Console

UX-007 replaces the Platform Integration placeholder with a thin enterprise UI for observing integration readiness, connector status, API endpoint visibility, webhook configuration, deployment environment, and integration activity.

## Page Structure

- Integration Header: status, active environment, last sync time, release version, and primary actions.
- Connector Management: backend/API/service connectors with status, endpoint, auth mode, latency, last checked time, and action buttons.
- API Endpoint Overview: endpoint name, method, path, owning service, status, and version.
- Webhook Configuration: webhook ID, event type, target URL, status, retry policy, last delivery, and action buttons.
- Deployment & Environment: environment, release tag, runtime, build status, monitoring mode, regression baseline, and commercial readiness.
- Integration Activity Log: latest integration actions with readable Asia/Kolkata timestamps.

## Backend Boundary

The UI consumes integration data through `EnterpriseIntegrationClient` only. The console does not implement connector protocols, endpoint discovery, webhook delivery, authentication, deployment logic, or monitoring logic. Backend modules remain frozen and authoritative.

## Fallback Policy

When live endpoints are not discoverable, UX-007 uses deterministic fallback data inside the UX layer. The fallback adapter preserves current UI session state for connector toggles and locally added webhooks so action refreshes do not delete visible state.

## Extension Notes

Future production integration can replace the fallback client implementation while keeping the same `EnterpriseIntegrationClient` contract and React/static rendering surfaces.
