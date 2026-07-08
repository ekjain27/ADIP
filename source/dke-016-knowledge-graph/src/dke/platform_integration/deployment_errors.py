from .platform_errors import PlatformIntegrationError


class DeploymentReadinessError(PlatformIntegrationError):
    """Base error for PI-008 deployment readiness failures."""


class MissingDeploymentComponentError(DeploymentReadinessError):
    """Raised when a required platform component is absent."""


class IncompatibleRuntimeStateError(DeploymentReadinessError):
    """Raised when runtime state is not compatible for release."""


class IncompleteConfigurationError(DeploymentReadinessError):
    """Raised when a deployment profile configuration is incomplete."""


class UnsupportedDeploymentProfileError(DeploymentReadinessError):
    """Raised when a deployment profile is unsupported."""


class DuplicateManifestEntryError(DeploymentReadinessError):
    """Raised when a release manifest entry is duplicated."""
