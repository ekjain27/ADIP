class NoveltyAnalysisError(ValueError):
    """Base error for novelty and prior-art analysis artifacts."""


class DuplicateReferenceError(NoveltyAnalysisError):
    """Raised when duplicate prior-art reference IDs are registered."""


class DuplicateAnalysisError(NoveltyAnalysisError):
    """Raised when duplicate comparison analysis IDs are generated."""


class MalformedComparisonRecordError(NoveltyAnalysisError):
    """Raised when a comparison record is incomplete or malformed."""


class MissingInnovationReferenceError(NoveltyAnalysisError):
    """Raised when a comparison references an unknown innovation."""


class InconsistentNoveltyTraceabilityError(NoveltyAnalysisError):
    """Raised when comparison evidence cannot be traced to implementation artifacts."""
