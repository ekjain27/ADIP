class MethodologyGenerationError(ValueError):
    """Base error for methodology and architecture composition."""


class DuplicateArchitectureIdError(MethodologyGenerationError):
    """Raised when architecture components, workflows, or glossary terms duplicate IDs."""


class UndocumentedComponentError(MethodologyGenerationError):
    """Raised when a component is not covered by architecture or workflow documentation."""


class InconsistentArchitectureMappingError(MethodologyGenerationError):
    """Raised when architecture mappings are incomplete or inconsistent."""


class MalformedWorkflowDefinitionError(MethodologyGenerationError):
    """Raised when workflow documentation is missing required deterministic fields."""


class TerminologyConsistencyError(MethodologyGenerationError):
    """Raised when methodology terminology is incomplete or inconsistent."""
