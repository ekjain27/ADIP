from .platform_errors import PlatformIntegrationError


class PersistenceError(PlatformIntegrationError):
    """Base error for PI-006 persistence layer failures."""


class PersistenceBackendRegistrationError(PersistenceError):
    """Raised when a persistence backend cannot be registered."""


class PersistenceBackendNotFoundError(PersistenceError):
    """Raised when a persistence backend is not registered."""


class PersistenceRecordError(PersistenceError):
    """Raised when a persistence record is invalid or unavailable."""


class DuplicatePersistenceRecordError(PersistenceRecordError):
    """Raised when a record ID already exists."""


class UnsupportedPersistenceBackendError(PersistenceError):
    """Raised when a backend is unsupported for an operation."""


class PersistenceTransactionError(PersistenceError):
    """Raised when transaction lifecycle rules are violated."""


class ImmutablePersistenceRecordError(PersistenceRecordError):
    """Raised when an immutable record would be modified."""
