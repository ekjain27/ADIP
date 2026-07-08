# DIE-005 Decision Simulation Engine

## Purpose

The simulation package consumes a DIE-004 `RankedDecisionPackage` and models likely outcomes for each ranked
alternative. It answers: "If this decision is selected, what could happen?"

## Pipeline

`RankedDecisionPackage` -> `DecisionSimulator` -> `OutcomeSimulator` -> `ScenarioGenerator` + `ImpactAnalyzer` -> `SimulationPackageBuilder` -> `SimulationDecisionPackage`

## Scenario Types

Each ranked alternative receives exactly three deterministic scenarios:

- `best_case`
- `expected_case`
- `worst_case`

Probabilities are normalized to sum to `1.0`.

## Outcome Scoring

`OutcomeSimulator` calculates `outcome_score` as the probability-weighted average of scenario impact scores.
Scores are normalized between `0.0` and `1.0`.

## Impact Analysis

`ImpactAnalyzer` calculates risk and confidence impacts from ranked alternative data and scenario confidence.

## Example Usage

```python
from decision_engine.core import DIECore
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.ranking import DecisionRanker
from decision_engine.simulation import DecisionSimulator

decision = DIECore().process({"query": "Choose a vendor"})
alternatives = AlternativeGenerator().generate(decision.decision_state)
evaluated = DecisionEvaluator().evaluate(alternatives)
ranked = DecisionRanker().rank(evaluated)
simulated = DecisionSimulator().simulate(ranked)
print(simulated.selected_outcome.outcome_score)
```

## Future Expansion

Future versions can add richer domain-specific scenario templates, Monte Carlo adapters, historical outcome calibration,
and policy-aware impact modeling while preserving the `SimulationDecisionPackage` contract.
