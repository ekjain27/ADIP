from .platform_errors import PlatformIntegrationError


class ContractAdapterError(PlatformIntegrationError):
    """Base error for PI-003 cross-engine contract adapter failures."""


class ContractAdapterRegistrationError(ContractAdapterError):
    """Raised when a cross-engine adapter cannot be registered."""


class ContractAdapterNotFoundError(ContractAdapterError):
    """Raised when a source-to-target adapter is not registered."""


class ContractAdapterValidationError(ContractAdapterError):
    """Raised when adapter or payload validation fails."""


class ContractAdapterCompatibilityError(ContractAdapterError):
    """Raised when source and target contracts are incompatible."""
