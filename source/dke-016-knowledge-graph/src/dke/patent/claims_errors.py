class ClaimsMappingError(ValueError):
    """Base error for patent claims mapping artifacts."""


class DuplicateClaimError(ClaimsMappingError):
    """Raised when duplicate claim IDs are generated or supplied."""


class UnmappedInnovationError(ClaimsMappingError):
    """Raised when an innovation has no claim mapping."""


class MissingEvidenceReferenceError(ClaimsMappingError):
    """Raised when a claim lacks implementation evidence."""


class MalformedClaimMetadataError(ClaimsMappingError):
    """Raised when claim metadata is incomplete or malformed."""


class InconsistentTraceabilityError(ClaimsMappingError):
    """Raised when innovation-to-evidence traceability is inconsistent."""
