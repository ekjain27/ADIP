from .innovation_catalog import ARCHITECTURAL_CONTRIBUTIONS, INNOVATION_MODULES, INNOVATION_TITLES
from .claims_errors import (
    ClaimsMappingError,
    DuplicateClaimError,
    InconsistentTraceabilityError,
    MalformedClaimMetadataError,
    MissingEvidenceReferenceError,
    UnmappedInnovationError,
)
from .claims_manifest import CLAIMS_MANIFEST_VERSION, generate_claims_manifest
from .claims_mapper import ClaimsMappingFramework, create_claims_mapping_framework
from .claims_matrix import ClaimMapping, export_claims_matrix_markdown
from .claims_traceability import ClaimTraceability, generate_traceability_report
from .figure_generator import default_patent_figures, generate_default_figure_manifest
from .figure_manifest import FIGURE_MANIFEST_VERSION, PatentFigure, generate_figure_manifest as generate_patent_figure_manifest
from .invention_disclosure import export_disclosure_markdown, generate_invention_disclosure, validate_invention_disclosure
from .invention_registry import InnovationRecord, discover_innovations, generate_innovation_registry, validate_innovation_registry
from .comparison_matrix import NoveltyComparisonRecord, export_novelty_matrix_markdown
from .novelty_analyzer import NoveltyAnalysisFramework, create_novelty_analysis_framework
from .novelty_errors import (
    DuplicateAnalysisError,
    DuplicateReferenceError,
    InconsistentNoveltyTraceabilityError,
    MalformedComparisonRecordError,
    MissingInnovationReferenceError,
    NoveltyAnalysisError,
)
from .novelty_manifest import NOVELTY_MANIFEST_VERSION, generate_novelty_manifest
from .prior_art_registry import PriorArtReference, PriorArtRegistry
from .patent_errors import (
    DuplicateInnovationError,
    MalformedDisclosureError,
    MissingInnovationMetadataError,
    PatentPreparationError,
    UnsupportedInnovationMappingError,
)
from .patent_manifest import PATENT_MANIFEST_VERSION, PatentPreparationFramework, create_patent_preparation_framework
from .specification_errors import (
    DuplicateFigureError,
    IncompleteSpecificationTraceabilityError,
    InconsistentSpecificationManifestError,
    MalformedSpecificationSectionError,
    SpecificationGenerationError,
)
from .specification_generator import (
    PatentSpecificationGenerator,
    create_patent_specification_generator,
    export_json_manifest as export_specification_json_manifest,
    export_markdown_specification,
    generate_figure_manifest,
    generate_patent_specification,
    generate_specification_manifest,
    validate_specification,
)
from .specification_manifest import SPECIFICATION_MANIFEST_VERSION

__all__ = [
    "ARCHITECTURAL_CONTRIBUTIONS",
    "CLAIMS_MANIFEST_VERSION",
    "FIGURE_MANIFEST_VERSION",
    "INNOVATION_MODULES",
    "INNOVATION_TITLES",
    "ClaimMapping",
    "ClaimTraceability",
    "ClaimsMappingError",
    "ClaimsMappingFramework",
    "DuplicateClaimError",
    "DuplicateFigureError",
    "DuplicateInnovationError",
    "IncompleteSpecificationTraceabilityError",
    "InconsistentSpecificationManifestError",
    "InconsistentTraceabilityError",
    "InnovationRecord",
    "MalformedClaimMetadataError",
    "MalformedDisclosureError",
    "MalformedComparisonRecordError",
    "MalformedSpecificationSectionError",
    "MissingEvidenceReferenceError",
    "MissingInnovationMetadataError",
    "MissingInnovationReferenceError",
    "NOVELTY_MANIFEST_VERSION",
    "NoveltyAnalysisError",
    "NoveltyAnalysisFramework",
    "NoveltyComparisonRecord",
    "PATENT_MANIFEST_VERSION",
    "SPECIFICATION_MANIFEST_VERSION",
    "PatentPreparationError",
    "PatentPreparationFramework",
    "PatentFigure",
    "PatentSpecificationGenerator",
    "PriorArtReference",
    "PriorArtRegistry",
    "SpecificationGenerationError",
    "UnmappedInnovationError",
    "UnsupportedInnovationMappingError",
    "create_claims_mapping_framework",
    "create_novelty_analysis_framework",
    "create_patent_preparation_framework",
    "create_patent_specification_generator",
    "default_patent_figures",
    "discover_innovations",
    "export_claims_matrix_markdown",
    "export_disclosure_markdown",
    "export_markdown_specification",
    "export_novelty_matrix_markdown",
    "export_specification_json_manifest",
    "generate_claims_manifest",
    "generate_default_figure_manifest",
    "generate_figure_manifest",
    "generate_innovation_registry",
    "generate_invention_disclosure",
    "generate_novelty_manifest",
    "generate_patent_figure_manifest",
    "generate_patent_specification",
    "generate_specification_manifest",
    "generate_traceability_report",
    "validate_innovation_registry",
    "validate_invention_disclosure",
    "validate_specification",
]
