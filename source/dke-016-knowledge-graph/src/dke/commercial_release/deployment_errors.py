class DeploymentPackageError(ValueError):
    """Base error for deterministic deployment and distribution metadata."""


class UnsupportedDeploymentProfileError(DeploymentPackageError):
    """Raised when a deployment target is not supported."""


class DuplicateDeploymentIdentifierError(DeploymentPackageError):
    """Raised when generated deployment artifacts contain duplicate identifiers."""


class IncompleteDeploymentMetadataError(DeploymentPackageError):
    """Raised when mandatory deployment metadata is missing."""


class IncompleteConfigurationError(DeploymentPackageError):
    """Raised when configuration profiles are incomplete or malformed."""


class InconsistentUpgradePlanError(DeploymentPackageError):
    """Raised when upgrade and rollback plans do not align."""


class MalformedDeploymentManifestError(DeploymentPackageError):
    """Raised when deployment manifests do not satisfy release constraints."""
