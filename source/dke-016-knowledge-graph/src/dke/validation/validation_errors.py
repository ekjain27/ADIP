class RegressionValidationError(ValueError):
    """Base error for VB-001 regression validation failures."""


class IncompleteWorkflowError(RegressionValidationError):
    """Raised when a requested workflow is incomplete or unavailable."""


class MissingPlatformComponentError(RegressionValidationError):
    """Raised when a required platform component is missing."""


class NonDeterministicOutputError(RegressionValidationError):
    """Raised when repeated workflow execution produces different output."""


class IncompatibleContractError(RegressionValidationError):
    """Raised when platform contracts are incompatible."""


class SnapshotMismatchError(RegressionValidationError):
    """Raised when a regression snapshot differs from the baseline."""
