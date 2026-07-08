class StressTestingError(ValueError):
    """Base error for deterministic enterprise stress testing."""


class StressScenarioDefinitionError(StressTestingError):
    """Raised when a stress scenario definition is malformed."""


class DuplicateStressScenarioError(StressTestingError):
    """Raised when a stress scenario ID is registered more than once."""


class UnsupportedFailureSimulationError(StressTestingError):
    """Raised when a failure simulation mode is unsupported."""


class MalformedWorkloadError(StressTestingError):
    """Raised when a workload description is malformed."""


class StressBaselineError(StressTestingError):
    """Raised when a stress baseline is incompatible or mismatched."""
