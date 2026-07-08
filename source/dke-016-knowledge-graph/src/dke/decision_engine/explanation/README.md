# DIE-006 Decision Explanation Engine

## Purpose

The explanation package consumes a DIE-005 `SimulationDecisionPackage` and explains why a decision is recommended.
It connects evidence, risks, scenarios, ranking, evaluation, assumptions, and simulated outcomes into deterministic
explanation text.

## Pipeline

`SimulationDecisionPackage` -> `ExplanationGenerator` -> sub-explainers -> `ExplanationPackageBuilder` -> `ExplanationDecisionPackage`

## Explanation Sections

Each `DecisionExplanation` includes sections for:

- Evidence
- Risk
- Scenarios
- Recommendation

## Confidence Calculation

Explanation confidence is the normalized average of simulation outcome score, confidence impact, scenario confidence
average, and ranked alternative confidence.

## Example Usage

```python
from decision_engine.explanation import ExplanationGenerator

explanation_package = ExplanationGenerator().explain(simulation_package)
print(explanation_package.selected_explanation.summary)
```

## Future Expansion

Future versions can add template libraries, domain-specific explanation styles, human-readable policy citations,
auditor-focused traces, or LLM-backed drafting while preserving the deterministic package contract.
