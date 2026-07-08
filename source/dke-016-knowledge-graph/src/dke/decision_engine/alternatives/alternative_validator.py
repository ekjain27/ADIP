from __future__ import annotations

from decision_engine.core import DecisionState

from .models import AlternativeDecision


class AlternativeValidator:
    def validate(
        self,
        alternatives: tuple[AlternativeDecision, ...],
        decision_state: DecisionState | None = None,
    ) -> None:
        self._validate_unique_ids(alternatives)
        self._validate_unique_descriptions(alternatives)
        valid_evidence_ids = {item.id for item in decision_state.evidence} if decision_state else set()
        for alternative in alternatives:
            self._validate_required_fields(alternative)
            self._validate_confidence(alternative)
            self._validate_evidence_refs(alternative, valid_evidence_ids)

    def _validate_unique_ids(self, alternatives: tuple[AlternativeDecision, ...]) -> None:
        ids = [alternative.alternative_id for alternative in alternatives]
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        if duplicates:
            raise ValueError(f"Duplicate alternative IDs: {', '.join(duplicates)}")

    def _validate_unique_descriptions(self, alternatives: tuple[AlternativeDecision, ...]) -> None:
        descriptions = [alternative.description.strip().lower() for alternative in alternatives]
        duplicates = sorted({item for item in descriptions if descriptions.count(item) > 1})
        if duplicates:
            raise ValueError("Duplicate alternative descriptions detected")

    def _validate_required_fields(self, alternative: AlternativeDecision) -> None:
        missing = []
        for field_name in ("alternative_id", "title", "description"):
            if not str(getattr(alternative, field_name, "")).strip():
                missing.append(field_name)
        if missing:
            raise ValueError(f"AlternativeDecision missing required fields: {', '.join(missing)}")

    def _validate_confidence(self, alternative: AlternativeDecision) -> None:
        for field_name in ("confidence", "feasibility"):
            value = getattr(alternative, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1 for {alternative.alternative_id}")

    def _validate_evidence_refs(self, alternative: AlternativeDecision, valid_evidence_ids: set[str]) -> None:
        if not valid_evidence_ids and not alternative.supporting_evidence:
            return
        invalid_refs = [item for item in alternative.supporting_evidence if item not in valid_evidence_ids]
        if invalid_refs:
            raise ValueError(
                f"Alternative {alternative.alternative_id} references unknown evidence IDs: {', '.join(invalid_refs)}"
            )
