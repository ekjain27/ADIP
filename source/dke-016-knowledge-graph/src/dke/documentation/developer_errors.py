class DeveloperDocumentationError(ValueError):
    """Base error for developer onboarding documentation."""


class UndocumentedPublicModuleError(DeveloperDocumentationError):
    """Raised when a public module lacks developer documentation."""


class DuplicateGuideSectionError(DeveloperDocumentationError):
    """Raised when a developer guide contains duplicate sections."""


class InconsistentDependencyGraphError(DeveloperDocumentationError):
    """Raised when documented dependencies conflict with registry metadata."""


class MalformedApiReferenceError(DeveloperDocumentationError):
    """Raised when SDK/API reference documentation is malformed."""
