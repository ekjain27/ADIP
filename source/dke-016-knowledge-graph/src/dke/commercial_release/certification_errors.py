class ReleaseCertificationError(ValueError):
    """Base error for deterministic release certification artifacts."""


class MissingCertificationArtifactError(ReleaseCertificationError):
    """Raised when a mandatory certification artifact is absent or incomplete."""


class VersionConsistencyError(ReleaseCertificationError):
    """Raised when release certification version metadata is inconsistent."""


class DuplicateReleaseIdentifierError(ReleaseCertificationError):
    """Raised when certification artifacts reuse release identifiers."""


class IncompleteReleaseCertificationError(ReleaseCertificationError):
    """Raised when production readiness cannot be certified."""
