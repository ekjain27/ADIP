# DIE-018 Enterprise Decision Monitoring Engine

DIE-018 consumes a `WorkflowDecisionPackage` from DIE-017 and produces a `MonitoringDecisionPackage`.

## Decision Health Monitoring Fabric

The Decision Health Monitoring Fabric, or DHMF, monitors workflow health, execution status, risk drift, confidence drift, governance drift, delay signals, exception signals, and decision degradation.

## Components

- `MetricCollector` gathers deterministic workflow metrics: completion score, stage count, approval count, exception count, and routing complexity.
- `DriftDetector` calculates normalized risk, confidence, and governance drift signals.
- `HealthMonitor` calculates a normalized health score and assigns `healthy`, `watch`, `degraded`, or `critical`.
- `AlertGenerator` creates deterministic alerts and recommended actions for degraded health, drift, and exception pressure.
- `MonitoringValidator` validates scores, metric values, alert severities, selected result consistency, and workflow references.
- `MonitoringPackageBuilder` assembles timestamped monitoring output.
- `DecisionMonitoringEngine` coordinates the end-to-end monitoring workflow.

Future real-time event monitoring, streaming telemetry, anomaly detection, SLA monitoring, and dashboard adapters can replace collectors, detectors, monitors, alert generators, or package builders without changing the public API.
