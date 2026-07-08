from __future__ import annotations

from decision_engine.governance import GovernanceEvaluation

from .change_tracker import ChangeTracker
from .models import TemporalLineageLedger
from .rollback_manager import RollbackManager
from .temporal_validator import TemporalValidator
from .timeline_builder import TimelineBuilder
from .version_manager import VersionManager


class LineageLedger:
    def __init__(
        self,
        version_manager: VersionManager | None = None,
        change_tracker: ChangeTracker | None = None,
        rollback_manager: RollbackManager | None = None,
        timeline_builder: TimelineBuilder | None = None,
        validator: TemporalValidator | None = None,
    ) -> None:
        self.version_manager = version_manager or VersionManager()
        self.change_tracker = change_tracker or ChangeTracker()
        self.rollback_manager = rollback_manager or RollbackManager()
        self.timeline_builder = timeline_builder or TimelineBuilder()
        self.validator = validator or TemporalValidator()

    def create(self, evaluation: GovernanceEvaluation) -> TemporalLineageLedger:
        versions = self.version_manager.create_versions(evaluation)
        changes = self.change_tracker.track(evaluation)
        rollback_points = self.rollback_manager.create_points(evaluation, versions)
        timeline = self.timeline_builder.build(versions, changes, rollback_points)
        ledger = TemporalLineageLedger(
            versions=versions,
            changes=changes,
            timeline=timeline,
            rollback_points=rollback_points,
            active_version=self.version_manager.active_version(versions),
            metadata={
                "ledger_type": "Temporal Decision Lineage Ledger",
                "immutable": True,
                "alternative_id": evaluation.alternative_id,
            },
        )
        self.validator.validate_ledger(ledger)
        return ledger
