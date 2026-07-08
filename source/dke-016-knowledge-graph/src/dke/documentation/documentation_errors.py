class DocumentationGenerationError(ValueError):
    """Base error for deterministic documentation generation."""


class DocumentationRegistryError(DocumentationGenerationError):
    """Raised when runtime registry documentation cannot be generated."""


class DocumentationManifestError(DocumentationGenerationError):
    """Raised when a documentation manifest is malformed."""
