# DIE-002 Decision Alternative Generator

## Purpose

The alternatives package turns a DIE-001 `DecisionState` into an `AlternativeDecisionPackage`.
It generates several possible decision paths before later evaluation, ranking, or audit modules choose between them.

## Pipeline

`DecisionState` -> `AlternativeGenerator` -> `AlternativeBuilder` -> `AlternativeValidator` -> `AlternativePackageBuilder` -> `AlternativeDecisionPackage`

## Classes

- `AlternativeDecision`: immutable model for one possible decision path.
- `AlternativeDecisionPackage`: immutable package containing all generated alternatives and generation metadata.
- `AlternativeGenerator`: deterministic rule-based generator that produces three to seven unique alternatives.
- `AlternativeBuilder`: validates required inputs, generates stable IDs, normalizes confidence, and populates metadata.
- `AlternativeValidator`: checks unique IDs, duplicate descriptions, confidence bounds, required fields, and evidence references.
- `AlternativePackageBuilder`: validates alternatives and wraps them with count, strategy, timestamp, and metadata.

## Future Expansion

The generator is intentionally modular. Future modules can add LLM-backed generation, domain-specific strategy plugins,
learning from historical decisions, or policy-aware templates while keeping the same `AlternativeDecisionPackage` output.

## Example Usage

```python
from decision_engine.core import DIECore
from decision_engine.alternatives import AlternativeGenerator

decision_package = DIECore().process({
    "query": "Choose a compliant vendor within budget",
    "semantic_results": [{"text": "Vendor A has strong reliability.", "confidence": 0.86}],
})

alternatives = AlternativeGenerator().generate(decision_package.decision_state)
print(alternatives.total_generated)
```
