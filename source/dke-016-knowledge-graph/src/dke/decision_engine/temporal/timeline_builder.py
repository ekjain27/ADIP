from __future__ import annotations

from .models import DecisionChange, DecisionVersion, RollbackPoint, TimelineEvent


class TimelineBuilder:
    def build(
        self,
        versions: tuple[DecisionVersion, ...],
        changes: tuple[DecisionChange, ...],
        rollback_points: tuple[RollbackPoint, ...] = (),
    ) -> tuple[TimelineEvent, ...]:
        events: list[TimelineEvent] = []
        for version in versions:
            events.append(
                TimelineEvent(
                    event_id=f"evt-{version.version_id}-created",
                    event_type="version_creation",
                    timestamp=version.created_at,
                    description=version.summary,
                    related_version=version.version_id,
                    metadata={"status": version.status},
                )
            )
        active_version = versions[-1].version_id if versions else ""
        for change in changes:
            events.append(
                TimelineEvent(
                    event_id=f"evt-{change.change_id}",
                    event_type=change.change_type,
                    timestamp=change.timestamp,
                    description=change.reason,
                    related_version=active_version,
                    metadata={"source_module": change.source_module},
                )
            )
        for rollback in rollback_points:
            events.append(
                TimelineEvent(
                    event_id=f"evt-{rollback.rollback_id}",
                    event_type="rollback_point",
                    timestamp=rollback.created_at,
                    description=rollback.reason,
                    related_version=rollback.target_version,
                    metadata=rollback.metadata,
                )
            )
        return tuple(sorted(events, key=lambda event: (event.timestamp, event.event_id)))
