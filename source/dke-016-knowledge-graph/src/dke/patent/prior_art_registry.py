from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .novelty_errors import DuplicateReferenceError, MalformedComparisonRecordError

REFERENCE_TYPES = ("publication", "patent", "product", "standard", "other")


@dataclass(frozen=True)
class PriorArtReference:
    reference_id: str
    title: str
    reference_type: str
    summary: str
    cited_elements: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = {
            "reference_id": self.reference_id,
            "title": self.title,
            "reference_type": self.reference_type,
            "summary": self.summary,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MalformedComparisonRecordError(f"malformed reference metadata: {', '.join(missing)}")
        if self.reference_type not in REFERENCE_TYPES:
            raise MalformedComparisonRecordError(f"unsupported reference type: {self.reference_type}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "title": self.title,
            "reference_type": self.reference_type,
            "summary": self.summary,
            "cited_elements": tuple(sorted(self.cited_elements)),
        }


class PriorArtRegistry:
    def __init__(self) -> None:
        self._references: dict[str, PriorArtReference] = {}

    def register_reference(self, reference: PriorArtReference) -> PriorArtReference:
        if not isinstance(reference, PriorArtReference):
            raise MalformedComparisonRecordError("reference must be PriorArtReference")
        if reference.reference_id in self._references:
            raise DuplicateReferenceError(f"duplicate reference ID: {reference.reference_id}")
        self._references[reference.reference_id] = reference
        return reference

    def list_references(self) -> tuple[PriorArtReference, ...]:
        return tuple(self._references[key] for key in sorted(self._references))

    def references(self) -> Mapping[str, PriorArtReference]:
        return MappingProxyType(dict(sorted(self._references.items())))

    def export_reference_registry(self) -> dict[str, Any]:
        return {
            "module": "PAT-003",
            "registry_type": "prior_art_reference_registry",
            "status": "generated",
            "reference_count": len(self._references),
            "references": tuple(reference.snapshot() for reference in self.list_references()),
        }
