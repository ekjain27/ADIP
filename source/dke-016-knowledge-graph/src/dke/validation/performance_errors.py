class PerformanceBenchmarkError(ValueError):
    """Base error for deterministic performance benchmarking."""


class InvalidPerformanceProfileError(PerformanceBenchmarkError):
    """Raised when an unsupported performance profile is requested."""


class DuplicatePerformanceBenchmarkError(PerformanceBenchmarkError):
    """Raised when a performance benchmark ID is registered more than once."""


class PerformanceBenchmarkDefinitionError(PerformanceBenchmarkError):
    """Raised when a benchmark definition is malformed."""


class UnsupportedPerformanceMetricError(PerformanceBenchmarkError):
    """Raised when a benchmark references unsupported metrics."""


class PerformanceBaselineError(PerformanceBenchmarkError):
    """Raised when a performance baseline is incompatible or mismatched."""
