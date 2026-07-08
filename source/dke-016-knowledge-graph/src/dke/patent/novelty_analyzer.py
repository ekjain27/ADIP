from __future__ import annotations

from typing import Any

from .claims_mapper import ClaimsMappingFramework, create_claims_mapping_framework
from .comparison_matrix import NoveltyComparisonRecord, export_novelty_matrix_markdown
from .invention_registry import InnovationRecord
from .novelty_errors import (
    DuplicateAnalysisError,
    InconsistentNoveltyTraceabilityError,
    MissingInnovationReferenceError,
)
from .novelty_manifest import generate_novelty_manifest
from .patent_manifest import PatentPreparationFramework, create_patent_preparation_framework
from .prior_art_registry import PriorArtReference, PriorArtRegistry


class NoveltyAnalysisFramework:
    MODULE = "PAT-003"

    def __init__(
        self,
        patent_framework: PatentPreparationFramework | None = None,
        claims_framework: ClaimsMappingFramework | None = None,
    ) -> None:
        self.patent_framework = patent_framework or create_patent_preparation_framework()
        self.claims_framework = claims_framework or create_claims_mapping_framework()
        self.reference_registry = PriorArtRegistry()
        self.runtime_registry = self.patent_framework.runtime_registry

    def register_reference(self, reference: PriorArtReference) -> PriorArtReference:
        return self.reference_registry.register_reference(reference)

    def analyze_innovation(self, innovation: InnovationRecord, reference: PriorArtReference) -> NoveltyComparisonRecord:
        claim_manifest = self.claims_framework.generate_claims_manifest()
        related_claims = tuple(claim for claim in claim_manifest["claims"] if claim["innovation_id"] == innovation.innovation_id)
        evidence = tuple(
            sorted(
                {
                    evidence_item
                    for claim in related_claims
                    for evidence_item in claim["implementation_evidence"]
                }
            )
        )
        return NoveltyComparisonRecord(
            analysis_id=f"PAT-003-{innovation.related_modules[0]}-{reference.reference_id}",
            innovation_id=innovation.innovation_id,
            reference_id=reference.reference_id,
            comparison_summary=(
                f"Compares {innovation.title} with {reference.title} for drafting support only."
            ),
            distinguishing_characteristics=(
                innovation.architectural_contribution,
                innovation.novelty_summary,
                f"Reference elements considered: {', '.join(reference.cited_elements) or reference.reference_type}",
            ),
            implementation_evidence=evidence,
            supporting_modules=innovation.related_modules,
        )

    def generate_novelty_matrix(self) -> dict[str, Any]:
        records = self._comparison_records()
        self.validate_novelty_analysis(records)
        return {
            "module": self.MODULE,
            "matrix_type": "novelty_matrix",
            "status": "generated",
            "analysis_count": len(records),
            "analyses": tuple(record.snapshot() for record in records),
            "markdown": export_novelty_matrix_markdown(records),
        }

    def generate_reference_coverage(self) -> dict[str, Any]:
        records = self._comparison_records()
        references = self.reference_registry.list_references()
        return {
            "module": self.MODULE,
            "report_type": "reference_coverage",
            "status": "complete",
            "reference_count": len(references),
            "coverage": tuple(
                (
                    reference.reference_id,
                    sum(1 for record in records if record.reference_id == reference.reference_id),
                )
                for reference in references
            ),
        }

    def export_novelty_manifest(self) -> dict[str, Any]:
        records = self._comparison_records()
        self.validate_novelty_analysis(records)
        return generate_novelty_manifest(
            records,
            self._innovation_coverage(records),
            self.generate_reference_coverage(),
            self.reference_registry.export_reference_registry(),
            self.runtime_registry.export_registry_snapshot(),
        )

    def validate_novelty_analysis(self, records: tuple[NoveltyComparisonRecord, ...] | None = None) -> dict[str, Any]:
        active_records = records or self._comparison_records()
        known_innovations = {innovation.innovation_id for innovation in self.patent_framework.discover_innovations()}
        seen: set[str] = set()
        covered: set[str] = set()
        for record in active_records:
            if record.analysis_id in seen:
                raise DuplicateAnalysisError(f"duplicate analysis ID: {record.analysis_id}")
            seen.add(record.analysis_id)
            if record.innovation_id not in known_innovations:
                raise MissingInnovationReferenceError(f"missing innovation reference: {record.innovation_id}")
            if not record.implementation_evidence or not record.supporting_modules:
                raise InconsistentNoveltyTraceabilityError(f"inconsistent traceability: {record.analysis_id}")
            covered.add(record.innovation_id)
        missing = tuple(sorted(known_innovations - covered))
        if missing:
            raise MissingInnovationReferenceError(f"unanalyzed innovation(s): {', '.join(missing)}")
        return {"module": self.MODULE, "status": "valid", "analysis_count": len(active_records), "innovation_count": len(covered)}

    def _comparison_records(self) -> tuple[NoveltyComparisonRecord, ...]:
        references = self.reference_registry.list_references() or self._default_references()
        records = [
            self.analyze_innovation(innovation, reference)
            for innovation in self.patent_framework.discover_innovations()
            for reference in references
        ]
        return tuple(sorted(records, key=lambda item: item.analysis_id))

    def _innovation_coverage(self, records: tuple[NoveltyComparisonRecord, ...]) -> dict[str, Any]:
        innovations = self.patent_framework.discover_innovations()
        return {
            "module": self.MODULE,
            "report_type": "innovation_coverage",
            "status": "complete",
            "innovation_count": len(innovations),
            "coverage": tuple(
                (
                    innovation.innovation_id,
                    sum(1 for record in records if record.innovation_id == innovation.innovation_id),
                )
                for innovation in innovations
            ),
        }

    def _default_references(self) -> tuple[PriorArtReference, ...]:
        return (
            PriorArtReference(
                "REF-BASELINE-001",
                "Configurable enterprise decision system reference",
                "publication",
                "Generic configurable decision workflow reference for structured comparison.",
                ("workflow", "governance", "monitoring"),
            ),
        )


def create_novelty_analysis_framework() -> NoveltyAnalysisFramework:
    return NoveltyAnalysisFramework()
