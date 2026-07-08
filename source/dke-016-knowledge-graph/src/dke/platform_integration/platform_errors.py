class PlatformIntegrationError(ValueError):
    """Base error for PI-001 platform integration failures."""


class ComponentRegistrationError(PlatformIntegrationError):
    """Raised when a platform component cannot be registered."""


class ComponentNotFoundError(PlatformIntegrationError):
    """Raised when a requested platform component is not registered."""


class ContractValidationError(PlatformIntegrationError):
    """Raised when a component does not satisfy its declared contract."""


class InvalidExecutionRequestError(PlatformIntegrationError):
    """Raised when a platform execution request is invalid."""
