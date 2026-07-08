from .platform_errors import PlatformIntegrationError


class RuntimeRegistryError(PlatformIntegrationError):
    """Base error for PI-002 runtime registry failures."""


class RuntimeComponentRegistrationError(RuntimeRegistryError):
    """Raised when a runtime component cannot be registered."""


class RuntimeComponentNotFoundError(RuntimeRegistryError):
    """Raised when a runtime component is not registered."""


class RuntimeDependencyError(RuntimeRegistryError):
    """Raised when runtime dependency validation fails."""


class RuntimeCompatibilityError(RuntimeRegistryError):
    """Raised when runtime contract compatibility validation fails."""


class FrozenRuntimeComponentError(RuntimeRegistryError):
    """Raised when a frozen runtime component would be mutated."""
