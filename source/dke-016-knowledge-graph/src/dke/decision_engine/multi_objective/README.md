# DIE-011 Multi-Objective Decision Optimization Engine

DIE-011 consumes `LearningDecisionPackage` from DIE-010 and produces a deterministic `MultiObjectiveDecisionPackage`.

## Components

- `ObjectiveRegistry` defines default objectives and normalized weights for value, risk, confidence, feasibility, compliance, and stability.
- `ObjectiveScorer` converts each learning result into per-objective scores between 0 and 1.
- `ParetoAnalyzer` identifies non-dominated alternatives.
- `TradeoffMatrixBuilder` creates objective and pairwise tradeoff matrices.
- `BalanceOptimizer` computes a balanced score and selected balanced result.
- `MultiObjectiveValidator` enforces normalized weights and unit-range scores.
- `MultiObjectivePackageBuilder` assembles and validates the final package.
- `MultiObjectiveEngine` coordinates the deterministic DIE-011 pipeline.

The module performs no random sampling and has no external service dependency.
