from __future__ import annotations

from decision_engine.simulation import SimulatedOutcome


class EvidenceExplainer:
    def explain(self, outcome: SimulatedOutcome) -> str:
        evidence = outcome.ranked_alternative.evaluated_alternative.alternative.supporting_evidence
        if not evidence:
            return "No supporting evidence was linked, so this explanation relies on ranking and simulation signals."
        strength = "strong" if len(evidence) >= 2 else "limited"
        return (
            f"The alternative is supported by {len(evidence)} evidence item(s), giving it {strength} evidence coverage. "
            f"Confidence impact is {outcome.confidence_impact:.3f}, which reflects both alternative confidence and scenario confidence."
        )

    def evidence_refs(self, outcome: SimulatedOutcome) -> tuple[str, ...]:
        return outcome.ranked_alternative.evaluated_alternative.alternative.supporting_evidence
