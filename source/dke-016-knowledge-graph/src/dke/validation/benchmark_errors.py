class BenchmarkError(ValueError):
    """Base error for deterministic decision quality benchmarks."""


class BenchmarkDefinitionError(BenchmarkError):
    """Raised when a benchmark definition is invalid."""


class DuplicateBenchmarkError(BenchmarkError):
    """Raised when a benchmark ID is registered more than once."""


class BenchmarkProfileError(BenchmarkError):
    """Raised when a scoring profile is invalid or incompatible."""


class BenchmarkInputError(BenchmarkError):
    """Raised when benchmark inputs are malformed."""


class MissingBenchmarkMetricError(BenchmarkError):
    """Raised when required benchmark metrics are missing."""


class BenchmarkBaselineMismatchError(BenchmarkError):
    """Raised when a benchmark snapshot differs from its baseline."""
