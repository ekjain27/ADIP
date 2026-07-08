class ModuleRegistryDocumentationError(ValueError):
    """Base error for module registry documentation."""


class DuplicateModuleRegistryEntryError(ModuleRegistryDocumentationError):
    """Raised when duplicate module IDs appear in documentation input."""


class MissingModuleMetadataError(ModuleRegistryDocumentationError):
    """Raised when a module registry entry lacks required metadata."""


class InconsistentPhaseAssignmentError(ModuleRegistryDocumentationError):
    """Raised when a module registry entry has an unsupported phase."""


class MalformedModuleRegistryEntryError(ModuleRegistryDocumentationError):
    """Raised when a module registry entry is malformed."""
