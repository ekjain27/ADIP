from __future__ import annotations

from typing import Any

from documentation import create_api_integration_documentation_framework

from .claims_errors import (
    DuplicateClaimError,
    InconsistentTraceabilityError,
    MissingEvidenceReferenceError,
    UnmappedInnovationError,
)
from .claims_manifest import generate_claims_manifest
from .claims_matrix import ClaimMapping, export_claims_matrix_markdown
from .claims_traceability import generate_traceability_report
from .invention_registry import InnovationRecord
from .patent_manifest import PatentPreparationFramework, create_patent_preparation_framework


class ClaimsMappingFramework:
    MODULE = "PAT-002"

    def __init__(self, patent_framework: PatentPreparationFramework | None = None) -> None:
        self.patent_framework = patent_framework or create_patent_preparation_framework()
        self.runtime_registry = self.patent_framework.runtime_registry
        self.api_docs = create_api_integration_documentation_framework()

    def map_innovation_to_claim(self, innovation: InnovationRecord) -> tuple[ClaimMapping, ClaimMapping]:
        module_id = innovation.related_modules[0]
        supporting_apis = self._supporting_apis(module_id)
        evidence = self._implementation_evidence(module_id, supporting_apis)
        base_id = innovation.innovation_id.replace("PAT-001", "PAT-002")
        independent = ClaimMapping(
            claim_id=f"{base_id}-IND",
            innovation_id=innovation.innovation_id,
            claim_type="independent",
            claim_candidate=f"A deterministic decision intelligence platform mechanism comprising {innovation.title}.",
            supporting_modules=innovation.related_modules,
            supporting_apis=supporting_apis,
            architectural_mechanisms=(innovation.architectural_contribution,),
            implementation_evidence=evidence,
        )
        dependent = ClaimMapping(
            claim_id=f"{base_id}-DEP",
            innovation_id=innovation.innovation_id,
            claim_type="dependent",
            claim_candidate=f"The mechanism of {innovation.title} further providing registry traceability and validation evidence.",
            supporting_modules=innovation.related_modules,
            supporting_apis=supporting_apis,
            architectural_mechanisms=(innovation.novelty_summary,),
            implementation_evidence=evidence,
        )
        return independent, dependent

    def generate_claims_matrix(self) -> dict[str, Any]:
        mappings = self._claim_mappings()
        self.validate_claims_mapping(mappings)
        return {
            "module": self.MODULE,
            "matrix_type": "claims_mapping_matrix",
            "status": "generated",
            "claim_count": len(mappings),
            "claims": tuple(mapping.snapshot() for mapping in mappings),
            "markdown": export_claims_matrix_markdown(mappings),
        }

    def generate_traceability_report(self) -> dict[str, Any]:
        mappings = self._claim_mappings()
        self.validate_claims_mapping(mappings)
        return generate_traceability_report(tuple(mapping.traceability() for mapping in mappings))

    def generate_claims_manifest(self) -> dict[str, Any]:
        mappings = self._claim_mappings()
        coverage = self._coverage_report(mappings)
        self.validate_claims_mapping(mappings)
        return generate_claims_manifest(mappings, coverage)

    def validate_claims_mapping(self, mappings: tuple[ClaimMapping, ...] | None = None) -> dict[str, Any]:
        active_mappings = mappings or self._claim_mappings()
        seen_claims: set[str] = set()
        mapped_innovations: set[str] = set()
        known_innovations = {innovation.innovation_id for innovation in self.patent_framework.discover_innovations()}
        for mapping in active_mappings:
            if mapping.claim_id in seen_claims:
                raise DuplicateClaimError(f"duplicate claim ID: {mapping.claim_id}")
            seen_claims.add(mapping.claim_id)
            if mapping.innovation_id not in known_innovations:
                raise InconsistentTraceabilityError(f"orphan claim entry: {mapping.claim_id}")
            mapped_innovations.add(mapping.innovation_id)
            if not mapping.implementation_evidence:
                raise MissingEvidenceReferenceError(f"missing evidence references: {mapping.claim_id}")
            mapping.traceability()
        missing = tuple(sorted(known_innovations - mapped_innovations))
        if missing:
            raise UnmappedInnovationError(f"unmapped innovation(s): {', '.join(missing)}")
        return {"module": self.MODULE, "status": "valid", "claim_count": len(active_mappings), "innovation_count": len(mapped_innovations)}

    def _claim_mappings(self) -> tuple[ClaimMapping, ...]:
        mappings: list[ClaimMapping] = []
        for innovation in self.patent_framework.discover_innovations():
            mappings.extend(self.map_innovation_to_claim(innovation))
        return tuple(sorted(mappings, key=lambda mapping: mapping.claim_id))

    def _coverage_report(self, mappings: tuple[ClaimMapping, ...]) -> dict[str, Any]:
        innovations = self.patent_framework.discover_innovations()
        return {
            "module": self.MODULE,
            "report_type": "claims_coverage",
            "status": "complete",
            "innovation_count": len(innovations),
            "claim_count": len(mappings),
            "claims_per_innovation": tuple(
                (innovation.innovation_id, sum(1 for mapping in mappings if mapping.innovation_id == innovation.innovation_id))
                for innovation in innovations
            ),
        }

    def _supporting_apis(self, module_id: str) -> tuple[str, ...]:
        api_catalog = self.api_docs.generate_api_catalog()
        platform_apis = tuple(
            api["api_id"]
            for api in api_catalog["apis"]
            if api["api_id"].startswith(("PlatformIntegrationLayer.", "UnifiedPlatformRuntimeRegistry.", "EnterpriseApiGateway."))
        )
        module_specific = (f"PlatformIntegrationLayer.execute_component:{module_id}", f"PlatformIntegrationLayer.execute_pipeline:{module_id}")
        return tuple(sorted((*module_specific, *platform_apis[:3])))

    def _implementation_evidence(self, module_id: str, supporting_apis: tuple[str, ...]) -> tuple[str, ...]:
        runtime = self.runtime_registry.get_runtime_component(module_id).snapshot()
        evidence = (
            f"PI-002 runtime metadata:{runtime['module_id']}",
            f"contracts:{','.join(runtime['contracts'].get('provides', ())) or 'registered'}",
            f"apis:{','.join(supporting_apis[:2])}",
            "PAT-001 innovation registry",
        )
        return evidence


def create_claims_mapping_framework() -> ClaimsMappingFramework:
    return ClaimsMappingFramework()
