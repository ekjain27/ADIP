class ApiDocumentationError(ValueError):
    """Base error for API and integration documentation."""


class DuplicateApiIdentifierError(ApiDocumentationError):
    """Raised when duplicate API identifiers are discovered."""


class UndocumentedPublicInterfaceError(ApiDocumentationError):
    """Raised when a public interface lacks generated documentation."""


class MalformedApiSignatureError(ApiDocumentationError):
    """Raised when an API signature cannot be documented."""


class InconsistentIntegrationMappingError(ApiDocumentationError):
    """Raised when an integration mapping is malformed or inconsistent."""
