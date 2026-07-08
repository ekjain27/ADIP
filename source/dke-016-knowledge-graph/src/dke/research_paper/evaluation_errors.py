class ExperimentalEvaluationError(ValueError):
    """Base error for experimental evaluation artifact generation."""


class FabricatedBenchmarkValueError(ExperimentalEvaluationError):
    """Raised when an evaluation record is marked as fabricated or unsupported."""


class MissingBenchmarkMetadataError(ExperimentalEvaluationError):
    """Raised when imported benchmark metadata is incomplete."""


class DuplicateExperimentIdentifierError(ExperimentalEvaluationError):
    """Raised when experiment identifiers are duplicated."""


class MalformedEvaluationRecordError(ExperimentalEvaluationError):
    """Raised when an experiment or benchmark record is malformed."""


class InconsistentExperimentMappingError(ExperimentalEvaluationError):
    """Raised when experiment mappings do not cover imported benchmark artifacts."""
