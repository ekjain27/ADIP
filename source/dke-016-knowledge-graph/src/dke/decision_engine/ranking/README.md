# DIE-004 Decision Ranking & Selection Engine

## Purpose

The ranking package consumes a DIE-003 `EvaluatedDecisionPackage`, ranks evaluated alternatives, selects the best
alternative, and returns a stable shortlist for downstream decision packaging.

## Pipeline

`EvaluatedDecisionPackage` -> `DecisionRanker` -> `RankingStrategy` -> `TieBreaker` -> `SelectionEngine` -> `RankingPackageBuilder` -> `RankedDecisionPackage`

## Ranking Strategy

The default strategy primarily uses `overall_score`, then blends confidence, recommendation level, evidence support,
risk count, and advantage/disadvantage balance. Recommendation levels adjust scores with deterministic boosts:

- `strong`: `+0.05`
- `moderate`: `+0.025`
- `weak`: `+0`
- `not_recommended`: `-0.05`

Scores are capped between `0.0` and `1.0`.

## Tie-Breaker Rules

Ties are resolved in this order:

1. Higher overall score
2. Higher confidence
3. Better recommendation level
4. More supporting evidence
5. Fewer risks
6. Lexicographic `alternative_id`

## Selection Statuses

- `selected`: rank 1
- `shortlisted`: rank 2 through top N
- `rejected`: all alternatives outside top N

## Example Usage

```python
from decision_engine.core import DIECore
from decision_engine.alternatives import AlternativeGenerator
from decision_engine.evaluation import DecisionEvaluator
from decision_engine.ranking import DecisionRanker

decision = DIECore().process({"query": "Choose a vendor"})
alternatives = AlternativeGenerator().generate(decision.decision_state)
evaluated = DecisionEvaluator().evaluate(alternatives)
ranked = DecisionRanker().rank(evaluated, top_n=3)
print(ranked.selected_alternative.alternative_id)
```

## Future Expansion

Future ranking modules can add portfolio-aware selection, scenario-specific strategy weights, human preference signals,
or policy gates while preserving the `RankedDecisionPackage` contract.
