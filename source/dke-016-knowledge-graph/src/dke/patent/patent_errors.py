class PatentPreparationError(ValueError):
    """Base error for deterministic patent preparation artifacts."""


class DuplicateInnovationError(PatentPreparationError):
    """Raised when an innovation ID appears more than once."""


class MissingInnovationMetadataError(PatentPreparationError):
    """Raised when an innovation record is missing required metadata."""


class UnsupportedInnovationMappingError(PatentPreparationError):
    """Raised when an innovation cannot be mapped to implemented architecture."""


class MalformedDisclosureError(PatentPreparationError):
    """Raised when an invention disclosure draft is malformed."""
