from .platform_errors import PlatformIntegrationError


class ObservabilityError(PlatformIntegrationError):
    """Base error for PI-007 observability layer failures."""


class InvalidLogLevelError(ObservabilityError):
    """Raised when a log level is unsupported."""


class MetricRegistrationError(ObservabilityError):
    """Raised when metric registration fails."""


class MetricNotFoundError(ObservabilityError):
    """Raised when a metric is not registered."""


class TraceValidationError(ObservabilityError):
    """Raised when trace lifecycle validation fails."""


class HealthCheckError(ObservabilityError):
    """Raised when health check registration or execution fails."""


class ObservabilityEventError(ObservabilityError):
    """Raised when an observability event is malformed."""
