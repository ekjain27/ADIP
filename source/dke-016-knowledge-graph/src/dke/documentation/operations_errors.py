class OperationsDocumentationError(ValueError):
    """Base error for deployment and operations documentation."""


class UnsupportedDeploymentEnvironmentError(OperationsDocumentationError):
    """Raised when an unsupported deployment environment is requested."""


class IncompleteDeploymentMetadataError(OperationsDocumentationError):
    """Raised when deployment metadata is incomplete."""


class DuplicateOperationalProcedureError(OperationsDocumentationError):
    """Raised when an operations manual contains duplicate procedures."""


class MalformedEnvironmentDefinitionError(OperationsDocumentationError):
    """Raised when an environment definition is malformed."""


class InconsistentDeploymentManifestError(OperationsDocumentationError):
    """Raised when deployment manifest content is inconsistent."""
