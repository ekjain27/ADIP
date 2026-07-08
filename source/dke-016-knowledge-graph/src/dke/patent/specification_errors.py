class SpecificationGenerationError(ValueError):
    """Base error for deterministic patent specification generation."""


class DuplicateFigureError(SpecificationGenerationError):
    """Raised when generated figure metadata contains duplicate identifiers."""


class MalformedSpecificationSectionError(SpecificationGenerationError):
    """Raised when a patent specification section is missing or malformed."""


class InconsistentSpecificationManifestError(SpecificationGenerationError):
    """Raised when a specification manifest is internally inconsistent."""


class IncompleteSpecificationTraceabilityError(SpecificationGenerationError):
    """Raised when specification traceability does not cover all required artifacts."""
