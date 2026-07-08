class GovernanceValidationError(ValueError):
    """Base error for governance and provenance validation."""


class GovernancePolicyError(GovernanceValidationError):
    """Raised when a validation policy is malformed."""


class UnsupportedGovernanceRuleError(GovernanceValidationError):
    """Raised when a policy contains unsupported rule definitions."""


class ProvenanceIntegrityError(GovernanceValidationError):
    """Raised when provenance links are missing or broken."""


class GovernancePolicyViolationError(GovernanceValidationError):
    """Raised when governance compliance rules are violated."""


class LineageConsistencyError(GovernanceValidationError):
    """Raised when temporal lineage chains are broken."""


class GovernanceBaselineError(GovernanceValidationError):
    """Raised when governance baseline comparison fails."""
