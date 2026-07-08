class CommercialReleaseError(ValueError):
    """Base error for deterministic commercial release infrastructure."""


class InvalidVersionMetadataError(CommercialReleaseError):
    """Raised when release version metadata is incomplete or malformed."""


class UnsupportedReleaseChannelError(CommercialReleaseError):
    """Raised when a release channel is not part of the supported lifecycle."""


class InvalidRegressionBaselineError(CommercialReleaseError):
    """Raised when the regression baseline is not formatted as passed/total passing."""


class InvalidGitTagError(CommercialReleaseError):
    """Raised when the release git tag does not match the deterministic tag format."""


class InconsistentReleaseManifestError(CommercialReleaseError):
    """Raised when release manifests or package metadata are inconsistent."""
