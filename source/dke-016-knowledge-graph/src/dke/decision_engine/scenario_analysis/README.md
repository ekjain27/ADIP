# DIE-009 Multi-Scenario Decision Analysis Engine

## Purpose

The scenario analysis package consumes a DIE-008 `UncertaintyDecisionPackage` and evaluates whether optimized decisions
remain good as future conditions change.

## Pipeline

`UncertaintyDecisionPackage` -> `DecisionScenarioEngine` -> `ScenarioGenerator` -> `ScenarioEvaluator` -> `ScenarioComparator` -> `ScenarioPackageBuilder` -> `ScenarioAnalysisDecisionPackage`

## Scenario Library

The default deterministic library includes Optimistic, Expected, Pessimistic, Market Shift, Resource Constraint,
Policy Change, and Technical Failure scenarios.

## Evaluation

Each uncertainty result is evaluated under every scenario for decision score, risk score, confidence, and robustness.

## Comparison And Stability

`ScenarioComparator` calculates average, best, worst, and stability scores, then assigns a recommendation:
`strong`, `moderate`, `weak`, or `unstable`.

## Future AI Scenarios

The public API is designed for future Monte Carlo, Bayesian, economic, climate, geopolitical, or LLM-generated scenario
engines without changing callers.

## Example Usage

```python
from decision_engine.scenario_analysis import DecisionScenarioEngine

scenario_package = DecisionScenarioEngine().analyze(uncertainty_package)
print(scenario_package.selected_comparison.recommendation)
```
