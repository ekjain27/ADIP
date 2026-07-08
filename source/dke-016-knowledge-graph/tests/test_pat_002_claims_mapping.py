import pytest

from patent import (
    CLAIMS_MANIFEST_VERSION,
    ClaimMapping,
    DuplicateClaimError,
    InconsistentTraceabilityError,
    MalformedClaimMetadataError,
    UnmappedInnovationError,
    create_claims_mapping_framework,
)


def test_innovation_discovery_from_pat001():
    framework = create_claims_mapping_framework()
    innovations = framework.patent_framework.discover_innovations()
    assert len(innovations) == 8
    assert innovations[0].innovation_id.startswith("PAT-001-")


def test_deterministic_mapping():
    framework = create_claims_mapping_framework()
    first = framework.generate_claims_matrix()
    second = framework.generate_claims_matrix()
    assert first == second
    assert first["claim_count"] == 16
    assert tuple(claim["claim_id"] for claim in first["claims"]) == tuple(sorted(claim["claim_id"] for claim in first["claims"]))


def test_map_innovation_to_claim():
    framework = create_claims_mapping_framework()
    innovation = framework.patent_framework.discover_innovations()[0]
    mappings = framework.map_innovation_to_claim(innovation)
    assert tuple(mapping.claim_type for mapping in mappings) == ("independent", "dependent")
    assert all(mapping.innovation_id == innovation.innovation_id for mapping in mappings)


def test_duplicate_claim_rejection():
    framework = create_claims_mapping_framework()
    mapping = framework.map_innovation_to_claim(framework.patent_framework.discover_innovations()[0])[0]
    with pytest.raises(DuplicateClaimError, match="duplicate claim ID"):
        framework.validate_claims_mapping((mapping, mapping))


def test_unmapped_innovation_rejection():
    framework = create_claims_mapping_framework()
    one_mapping = framework.map_innovation_to_claim(framework.patent_framework.discover_innovations()[0])[0]
    with pytest.raises(UnmappedInnovationError, match="unmapped innovation"):
        framework.validate_claims_mapping((one_mapping,))


def test_missing_evidence_rejection():
    framework = create_claims_mapping_framework()
    mapping = framework.map_innovation_to_claim(framework.patent_framework.discover_innovations()[0])[0]
    with pytest.raises(MalformedClaimMetadataError, match="claim mapping lacks support"):
        ClaimMapping(
            claim_id=mapping.claim_id,
            innovation_id=mapping.innovation_id,
            claim_type=mapping.claim_type,
            claim_candidate=mapping.claim_candidate,
            supporting_modules=mapping.supporting_modules,
            supporting_apis=mapping.supporting_apis,
            architectural_mechanisms=mapping.architectural_mechanisms,
            implementation_evidence=(),
        )


def test_orphan_claim_rejection():
    framework = create_claims_mapping_framework()
    mapping = framework.map_innovation_to_claim(framework.patent_framework.discover_innovations()[0])[0]
    orphan = ClaimMapping(
        claim_id="PAT-002-ORPHAN-IND",
        innovation_id="PAT-001-UNKNOWN",
        claim_type="independent",
        claim_candidate="Orphan claim",
        supporting_modules=("DPG",),
        supporting_apis=("PlatformIntegrationLayer.execute_component:DPG",),
        architectural_mechanisms=("Orphan",),
        implementation_evidence=("evidence",),
    )
    with pytest.raises(InconsistentTraceabilityError, match="orphan claim entry"):
        framework.validate_claims_mapping((mapping, orphan))


def test_traceability_report():
    framework = create_claims_mapping_framework()
    report = framework.generate_traceability_report()
    assert report["module"] == "PAT-002"
    assert report["trace_count"] == 16
    assert all(trace["evidence"] for trace in report["traces"])


def test_claims_manifest_json_export():
    framework = create_claims_mapping_framework()
    manifest = framework.generate_claims_manifest()
    assert manifest["module"] == "PAT-002"
    assert manifest["manifest_version"] == CLAIMS_MANIFEST_VERSION
    assert manifest["coverage_report"]["status"] == "complete"
    assert manifest["traceability_report"]["trace_count"] == 16


def test_claims_matrix_markdown_export():
    framework = create_claims_mapping_framework()
    markdown = framework.generate_claims_matrix()["markdown"]
    assert markdown.startswith("# Claims Mapping Matrix")
    assert "PAT-002-DPG-IND" in markdown
    assert "PAT-002-EDOF-DEP" in markdown


def test_integration_with_pat001_and_runtime_registry():
    framework = create_claims_mapping_framework()
    manifest = framework.generate_claims_manifest()
    assert framework.patent_framework.export_patent_manifest()["module"] == "PAT-001"
    assert framework.runtime_registry.export_registry_snapshot()["module"] == "PI-002"
    assert manifest["claims"][0]["implementation_evidence"][0].startswith("PI-002 runtime metadata")
