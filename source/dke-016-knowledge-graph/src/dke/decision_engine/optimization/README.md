# DIE-007 Decision Optimization Engine

## Purpose

The optimization package consumes a DIE-006 `ExplanationDecisionPackage` and asks whether the recommendation can be
improved while respecting objectives, constraints, and tradeoffs.

## Pipeline

`ExplanationDecisionPackage` -> `OptimizationEngine` -> `ObjectiveOptimizer` + `ConstraintOptimizer` + `TradeoffAnalyzer` -> `OptimizationPackageBuilder` -> `OptimizedDecisionPackage`

## Objectives

Default normalized objectives:

- `value`: `0.25`
- `risk`: `0.20`
- `confidence`: `0.15`
- `goal_alignment`: `0.15`
- `feasibility`: `0.15`
- `constraints`: `0.10`

## Tradeoffs

`TradeoffAnalyzer` produces deterministic summaries such as confidence versus validation time, risk reduction versus
return, speed versus accuracy, and budget versus safeguards.

## Optimization Strategy

The current implementation is rule-based and deterministic. It calculates objective satisfaction, constraint
satisfaction, bounded optimization gain, and a selected optimized result.

## Future AI Optimizers

The public API is designed so future optimizers can be plugged in without changing callers:

- `RuleBasedOptimizer`
- `LinearOptimizer`
- `GeneticOptimizer`
- `BayesianOptimizer`
- `ReinforcementOptimizer`
- `LLMOptimizer`

## Example Usage

```python
from decision_engine.optimization import OptimizationEngine

optimized = OptimizationEngine().optimize(explanation_package)
print(optimized.selected_result.optimized_score)
```
