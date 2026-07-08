from __future__ import annotations

from hashlib import sha256

from decision_engine.core.models import clamp_confidence
from decision_engine.optimization import OptimizationResult

from .models import AssumptionImpact


class AssumptionAnalyzer:
    def analyze(self, result: OptimizationResult) -> tuple[AssumptionImpact, ...]:
        assumptions = self._extract_assumptions(result)
        impacts = []
        for index, assumption in enumerate(assumptions):
            influence = clamp_confidence(0.35 + (index * 0.08) + (0.12 if "risk" in assumption.lower() else 0.0))
            impacts.append(
                AssumptionImpact(
                    assumption_id=self._stable_id(result.alternative_id, assumption),
                    description=assumption,
                    influence_score=influence,
                    confidence=clamp_confidence(result.confidence - (influence * 0.1)),
                    affected_components=("optimization", "confidence", "reliability"),
                    metadata={"alternative_id": result.alternative_id},
                )
            )
        return tuple(sorted(impacts, key=lambda item: item.influence_score, reverse=True))

    def _extract_assumptions(self, result: OptimizationResult) -> tuple[str, ...]:
        candidates = []
        candidates.extend(str(item) for item in result.improvements if "assumption" in str(item).lower())
        candidates.extend(str(item) for item in result.tradeoffs)
        if result.metadata.get("constraint_violations"):
            candidates.append("Constraint violations must be resolved before optimization is reliable.")
        if not candidates:
            candidates.append("Optimization inputs remain representative of the decision context.")
        return tuple(dict.fromkeys(candidates))

    def _stable_id(self, alternative_id: str, assumption: str) -> str:
        digest = sha256(f"{alternative_id}|{assumption}".encode("utf-8")).hexdigest()[:16]
        return f"assumption-{digest}"
