from __future__ import annotations

from decision_engine.core.models import utc_now
from decision_engine.governance import GovernanceEvaluation

from .models import DecisionVersion, RollbackPoint


class RollbackManager:
    def create_points(
        self,
        evaluation: GovernanceEvaluation,
        versions: tuple[DecisionVersion, ...],
    ) -> tuple[RollbackPoint, ...]:
        if not versions:
            return ()
        timestamp = utc_now().isoformat()
        points = [
            RollbackPoint(
                rollback_id=f"rb-{self._clean(evaluation.alternative_id)}-initial",
                target_version=versions[0].version_id,
                reason="Return to initial decision state if governance or policy conditions regress.",
                created_at=timestamp,
                metadata={"recommendation": "Use when decision must be re-opened."},
            )
        ]
        if evaluation.governance_status == "conditional":
            points.append(
                RollbackPoint(
                    rollback_id=f"rb-{self._clean(evaluation.alternative_id)}-governed",
                    target_version=versions[min(1, len(versions) - 1)].version_id,
                    reason="Return to governed version after resolving conditional controls.",
                    created_at=timestamp,
                    metadata={"recommendation": "Review governance conditions before activation."},
                )
            )
        return tuple(points)

    def validate_target(self, rollback: RollbackPoint, versions: tuple[DecisionVersion, ...]) -> bool:
        return rollback.target_version in {version.version_id for version in versions}

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
