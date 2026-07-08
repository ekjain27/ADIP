class LiteratureAnalysisError(ValueError):
    """Base error for deterministic related-work analysis."""


class MalformedLiteratureRecordError(LiteratureAnalysisError):
    """Raised when a literature entry is missing mandatory metadata."""


class DuplicateLiteratureEntryError(LiteratureAnalysisError):
    """Raised when literature entries duplicate identifiers or citation keys."""


class InconsistentLiteratureClassificationError(LiteratureAnalysisError):
    """Raised when a taxonomy or classification contains unsupported themes."""


class LiteratureRegistryValidationError(LiteratureAnalysisError):
    """Raised when a literature registry fails deterministic validation."""
