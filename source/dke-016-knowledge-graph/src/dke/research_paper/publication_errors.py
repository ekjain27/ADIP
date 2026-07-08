class PublicationPackageError(ValueError):
    """Base error for publication package generation."""


class DuplicatePublicationSectionError(PublicationPackageError):
    """Raised when assembled manuscript sections contain duplicate IDs."""


class MalformedPublicationProfileError(PublicationPackageError):
    """Raised when a publication profile is unsupported or incomplete."""


class MissingMandatoryPublicationSectionError(PublicationPackageError):
    """Raised when a mandatory manuscript section is absent."""


class InconsistentPublicationManifestError(PublicationPackageError):
    """Raised when package manifests or source traces are inconsistent."""


class PublicationNumberingConsistencyError(PublicationPackageError):
    """Raised when figures, tables, or appendices are inconsistent."""


class FabricatedPublicationClaimError(PublicationPackageError):
    """Raised when package metadata claims fabricated review, acceptance, references, or results."""
