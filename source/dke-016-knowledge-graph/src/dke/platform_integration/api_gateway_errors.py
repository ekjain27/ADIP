from .platform_errors import PlatformIntegrationError


class ApiGatewayError(PlatformIntegrationError):
    """Base error for PI-004 enterprise API gateway failures."""


class ApiRouteRegistrationError(ApiGatewayError):
    """Raised when an API gateway route cannot be registered."""


class ApiRouteNotFoundError(ApiGatewayError):
    """Raised when an API gateway route is not registered."""


class ApiRequestValidationError(ApiGatewayError):
    """Raised when an API gateway request is malformed."""


class ApiUnauthorizedActionError(ApiGatewayError):
    """Raised when an internal gateway action is not authorized."""
