# DIE-016 Adaptive Decision Engine

DIE-016 consumes a `TemporalDecisionPackage` from DIE-015 and produces an `AdaptiveDecisionPackage`.

## Adaptive Decision Behavior Model

The Adaptive Decision Behavior Model, or ADBM, deterministically adjusts decision behavior when temporal stability, governance status, confidence, risk, or change frequency shifts.

## Components

- `AdaptiveBehaviorModel` creates default profiles and preserves adjustment history.
- `AdaptationRuleEngine` loads deterministic rules for low stability, high change frequency, confidence pressure, risk tolerance, stable lineage, and governance concern.
- `ThresholdAdapter` adjusts confidence thresholds.
- `RiskToleranceAdapter` lowers risk tolerance under instability or governance concern.
- `ObjectivePriorityAdapter` shifts and normalizes objective priorities.
- `AdaptiveValidator` validates thresholds, risk tolerance, governance sensitivity, objective weights, scores, selected results, and rule uniqueness.
- `AdaptivePackageBuilder` assembles timestamped adaptive output.
- `AdaptiveDecisionEngine` coordinates the end-to-end adaptation workflow.

## Example

```python
from decision_engine.adaptive import AdaptiveDecisionEngine

adaptive_package = AdaptiveDecisionEngine().adapt(temporal_package)
selected = adaptive_package.selected_adaptive_result
```

Future reinforcement learning, online learning, human feedback, adaptive policy, and autonomous behavior optimizers can plug in by replacing adapters, rule engines, behavior models, or package builders without changing the public API.
