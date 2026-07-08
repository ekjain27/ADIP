from __future__ import annotations

import logging

from decision_engine.core.models import clamp_confidence
from decision_engine.governance import GovernanceDecisionPackage, GovernanceEvaluation

from .lineage_ledger import LineageLedger
from .models import TemporalDecision
from .temporal_package import TemporalPackageBuilder

logger = logging.getLogger(__name__)


class TemporalDecisionEngine:
    def __init__(
        self,
        lineage_ledger: LineageLedger | None = None,
        package_builder: TemporalPackageBuilder | None = None,
    ) -> None:
        self.lineage_ledger = lineage_ledger or LineageLedger()
        self.package_builder = package_builder or TemporalPackageBuilder()

    def track(self, governance_package: GovernanceDecisionPackage):
        if not isinstance(governance_package, GovernanceDecisionPackage):
            raise ValueError("TemporalDecisionEngine.track requires a GovernanceDecisionPackage")
        logger.info("Tracking temporal decision lineage")
        results = tuple(self._track_evaluation(evaluation) for evaluation in governance_package.evaluations)
        selected = self._selected_result(results, governance_package.selected_evaluation)
        return self.package_builder.build(
            results,
            selected,
            metadata={
                "source_module": governance_package.metadata.get("module", "DIE-014"),
                "governance_evaluation_count": len(governance_package.evaluations),
            },
        )

    def _track_evaluation(self, evaluation: GovernanceEvaluation) -> TemporalDecision:
        ledger = self.lineage_ledger.create(evaluation)
        change_frequency = clamp_confidence(len(ledger.changes) / max(1, len(ledger.timeline)))
        penalty = (len(evaluation.violations) * 0.08) + (change_frequency * 0.18)
        stability_score = clamp_confidence(evaluation.overall_score - penalty + 0.12)
        return TemporalDecision(
            alternative_id=evaluation.alternative_id,
            ledger=ledger,
            evolution_summary=self._evolution_summary(evaluation, ledger),
            stability_score=stability_score,
            change_frequency=change_frequency,
            metadata={
                "governance_status": evaluation.governance_status,
                "active_version": ledger.active_version,
            },
        )

    def _selected_result(self, results: tuple[TemporalDecision, ...], selected_evaluation: GovernanceEvaluation | None) -> TemporalDecision | None:
        if not results:
            return None
        if selected_evaluation is not None:
            for result in results:
                if result.alternative_id == selected_evaluation.alternative_id:
                    return result
        return max(results, key=lambda result: (result.stability_score, result.alternative_id))

    def _evolution_summary(self, evaluation: GovernanceEvaluation, ledger) -> str:
        return (
            f"{evaluation.alternative_id} evolved through {len(ledger.versions)} version(s), "
            f"{len(ledger.changes)} change(s), and {len(ledger.rollback_points)} rollback point(s)."
        )
