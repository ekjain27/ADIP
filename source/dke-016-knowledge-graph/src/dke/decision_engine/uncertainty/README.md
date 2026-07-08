# DIE-008 Decision Uncertainty & Sensitivity Engine

## Purpose

The uncertainty package consumes a DIE-007 `OptimizedDecisionPackage` and quantifies how reliable an optimized decision is.

## Pipeline

`OptimizedDecisionPackage` -> `UncertaintyEngine` -> `UncertaintyEstimator` + `SensitivityAnalyzer` + `RobustnessAnalyzer` + `AssumptionAnalyzer` -> `UncertaintyPackageBuilder` -> `UncertaintyDecisionPackage`

## Uncertainty Estimation

Uncertainty is deterministic and uses optimization confidence, optimized score, objective coverage, optimization gain,
and risk signals. Higher confidence lowers uncertainty; risk signals raise it.

## Sensitivity Analysis

Sensitivity is estimated for confidence, risk, constraints, objective weights, and assumptions using small deterministic
parameter variations.

## Robustness Analysis

Robustness combines optimized score, confidence, and confidence stability. Failure points identify high sensitivity,
low stability, or unresolved constraint concerns.

## Reliability Scoring

Reliability blends inverse uncertainty, confidence, and objective satisfaction into a normalized `0.0..1.0` score.

## Future Probabilistic Engines

The public API is designed to support future plug-ins such as Monte Carlo uncertainty, Bayesian uncertainty,
probabilistic graphical models, Gaussian process estimators, and deep ensemble estimators.

## Example Usage

```python
from decision_engine.uncertainty import UncertaintyEngine

uncertainty_package = UncertaintyEngine().analyze(optimized_package)
print(uncertainty_package.selected_result.reliability_score)
```
