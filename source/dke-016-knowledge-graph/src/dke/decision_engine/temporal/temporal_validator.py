from __future__ import annotations

from .models import TemporalDecision, TemporalDecisionPackage, TemporalLineageLedger


class TemporalValidator:
    def validate_ledger(self, ledger: TemporalLineageLedger) -> None:
        version_ids = tuple(version.version_id for version in ledger.versions)
        if len(version_ids) != len(set(version_ids)):
            raise ValueError("temporal ledger versions must be unique")
        numbers = tuple(version.version_number for version in ledger.versions)
        if numbers != tuple(sorted(numbers)):
            raise ValueError("temporal ledger versions must be ordered")
        if numbers and numbers != tuple(range(1, len(numbers) + 1)):
            raise ValueError("temporal ledger version numbers must be sequential")
        if ledger.active_version and ledger.active_version not in version_ids:
            raise ValueError("active version must exist in temporal ledger")
        parents = {version.version_id: version.parent_version for version in ledger.versions if version.parent_version}
        missing = sorted(parent for parent in parents.values() if parent not in version_ids)
        if missing:
            raise ValueError(f"temporal ledger references missing parent versions: {', '.join(missing)}")
        if self._has_version_cycle(parents):
            raise ValueError("temporal ledger contains a version cycle")
        timestamps = tuple(event.timestamp for event in ledger.timeline)
        if timestamps != tuple(sorted(timestamps)):
            raise ValueError("temporal timeline must be chronological")
        for rollback in ledger.rollback_points:
            if rollback.target_version not in version_ids:
                raise ValueError(f"rollback point references missing version {rollback.target_version}")

    def validate_decision(self, decision: TemporalDecision) -> None:
        if not decision.alternative_id.strip():
            raise ValueError("TemporalDecision.alternative_id is required")
        self.validate_ledger(decision.ledger)
        self._validate_unit(decision.stability_score, "stability score")
        self._validate_unit(decision.change_frequency, "change frequency")

    def validate_package(self, package: TemporalDecisionPackage) -> None:
        if not isinstance(package, TemporalDecisionPackage):
            raise ValueError("Expected TemporalDecisionPackage")
        for result in package.temporal_results:
            self.validate_decision(result)
        if package.temporal_results and package.selected_result is None:
            raise ValueError("selected temporal result is required when temporal results exist")
        if not package.temporal_results and package.selected_result is not None:
            raise ValueError("selected temporal result must be None when no temporal results exist")
        if package.selected_result is not None and package.selected_result not in package.temporal_results:
            raise ValueError("selected temporal result must be present in temporal results")

    def _has_version_cycle(self, parents: dict[str, str | None]) -> bool:
        for version_id in parents:
            seen: set[str] = set()
            current = version_id
            while current in parents:
                if current in seen:
                    return True
                seen.add(current)
                current = parents[current] or ""
        return False

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
