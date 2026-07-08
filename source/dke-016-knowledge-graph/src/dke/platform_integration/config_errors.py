from .platform_errors import PlatformIntegrationError


class PlatformConfigError(PlatformIntegrationError):
    """Base error for PI-005 configuration layer failures."""


class InvalidConfigProfileError(PlatformConfigError):
    """Raised when a configuration profile is unsupported."""


class MissingConfigValueError(PlatformConfigError):
    """Raised when a required configuration key is absent."""


class InvalidConfigTypeError(PlatformConfigError):
    """Raised when a configuration value has the wrong type."""


class FrozenConfigMutationError(PlatformConfigError):
    """Raised when a frozen configuration snapshot would be mutated."""
