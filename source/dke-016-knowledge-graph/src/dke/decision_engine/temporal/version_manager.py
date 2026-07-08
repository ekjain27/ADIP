from __future__ import annotations

from decision_engine.core.models import utc_now
from decision_engine.governance import GovernanceEvaluation

from .models import DecisionVersion


class VersionManager:
    def create_versions(self, evaluation: GovernanceEvaluation) -> tuple[DecisionVersion, ...]:
        decision_id = f"decision-{self._clean(evaluation.alternative_id)}"
        created_at = utc_now().isoformat()
        stages = (
            ("initial", "Initial decision candidate created from governed decision evidence."),
            ("governed", f"Governance status set to {evaluation.governance_status}."),
            ("active", f"Decision activated with governance score {evaluation.overall_score:.3f}."),
        )
        versions: list[DecisionVersion] = []
        parent: str | None = None
        for number, (status, summary) in enumerate(stages, start=1):
            version_id = f"{decision_id}-v{number}"
            versions.append(
                DecisionVersion(
                    version_id=version_id,
                    decision_id=decision_id,
                    version_number=number,
                    created_at=created_at,
                    parent_version=parent,
                    status=status,
                    summary=summary,
                    metadata={
                        "alternative_id": evaluation.alternative_id,
                        "governance_status": evaluation.governance_status,
                    },
                )
            )
            parent = version_id
        return tuple(versions)

    def active_version(self, versions: tuple[DecisionVersion, ...]) -> str:
        if not versions:
            return ""
        active = tuple(version for version in versions if version.status == "active")
        return (active[-1] if active else versions[-1]).version_id

    def _clean(self, value: str) -> str:
        return value.lower().replace(" ", "-").replace("_", "-")
