from __future__ import annotations

from decision_engine.core.models import utc_now
from decision_engine.governance import GovernanceEvaluation

from .models import DecisionChange


class ChangeTracker:
    def track(self, evaluation: GovernanceEvaluation) -> tuple[DecisionChange, ...]:
        timestamp = utc_now().isoformat()
        changes = [
            DecisionChange(
                change_id=f"chg-{self._clean(evaluation.alternative_id)}-governance",
                change_type="governance_decision",
                previous_value="pending",
                new_value=evaluation.governance_status,
                reason="Governance evaluation completed.",
                source_module="DIE-014",
                timestamp=timestamp,
                metadata={"overall_score": evaluation.overall_score},
            ),
            DecisionChange(
                change_id=f"chg-{self._clean(evaluation.alternative_id)}-confidence",
                change_type="confidence_change",
                previous_value="untracked",
                new_value=f"{evaluation.overall_score:.3f}",
                reason="Governance score established the current confidence baseline.",
                source_module="DIE-014",
                timestamp=timestamp,
                metadata={"policy_count": len(evaluation.policy_results)},
            ),
            DecisionChange(
                change_id=f"chg-{self._clean(evaluation.alternative_id)}-policy",
                change_type="policy_update",
                previous_value="not_evaluated",
                new_value=f"{len(evaluation.policy_results)} policies evaluated",
                reason="Policy mesh evaluation recorded active controls.",
                source_module="DIE-014",
                timestamp=timestamp,
                metadata={"violation_count": len(evaluation.violations)},
            ),
            DecisionChange(
                change_id=f"chg-{self._clean(evaluation.alternative_id)}-learning",
                change_type="learning_update",
                previous_value="pre_governance",
                new_value="post_governance",
                reason="Learning, planning, provenance, and governance signals were consolidated.",
                source_module="DIE-010:DIE-014",
                timestamp=timestamp,
                metadata={"recommendation_count": len(evaluation.recommendations)},
            ),
        ]
        return tuple(changes)

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
