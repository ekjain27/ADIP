class ResearchPaperGenerationError(ValueError):
    """Base error for deterministic research paper artifact generation."""


class MalformedPaperMetadataError(ResearchPaperGenerationError):
    """Raised when paper metadata is missing required deterministic fields."""


class DuplicateAcronymError(ResearchPaperGenerationError):
    """Raised when acronym metadata contains duplicate acronym identifiers."""


class DuplicateSectionError(ResearchPaperGenerationError):
    """Raised when paper structure contains duplicate section identifiers."""


class InconsistentPublicationProfileError(ResearchPaperGenerationError):
    """Raised when a publication or venue profile is unsupported or inconsistent."""


class GlossaryConsistencyError(ResearchPaperGenerationError):
    """Raised when glossary terms are incomplete or inconsistent."""


class NumberingConsistencyError(ResearchPaperGenerationError):
    """Raised when figure or table numbering is inconsistent."""
