from __future__ import annotations

from typing import Any

from .models import ReasoningResult, ValidationIssue, ValidationReport


def validate_context(context_package: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    facts = tuple(getattr(context_package, "facts", ()) or ())
    evidence = tuple(getattr(context_package, "evidence", ()) or ())
    confidence = float(getattr(context_package, "confidence", 0.0) or 0.0)
    normalized_confidence = confidence / 100 if confidence > 1 else confidence

    if not facts:
        issues.append(ValidationIssue("empty_context", "context package must not be empty", "error"))
    if not evidence:
        issues.append(ValidationIssue("missing_evidence", "evidence must exist for major claims", "warning"))
    if not 0 <= normalized_confidence <= 1:
        issues.append(ValidationIssue("invalid_context_confidence", "context confidence must normalize to 0..1", "error"))
    if normalized_confidence < 0.35:
        issues.append(ValidationIssue("weak_context", "retrieval context confidence is weak", "warning"))
    return ValidationReport(valid=not any(issue.severity == "error" for issue in issues), issues=tuple(issues))


def validate_reasoning(reasoning_result: ReasoningResult | Any) -> ValidationReport:
    result = reasoning_result if isinstance(reasoning_result, ReasoningResult) else ReasoningResult(**_reasoning_dict(reasoning_result))
    issues: list[ValidationIssue] = []
    if not result.recommendation and not result.limitations:
        issues.append(ValidationIssue("missing_recommendation_or_limitation", "reasoning output must include recommendation or limitation", "error"))
    if not 0 <= result.confidence <= 1:
        issues.append(ValidationIssue("invalid_reasoning_confidence", "reasoning confidence must be between 0 and 1", "error"))
    if result.unsupported_conclusions:
        issues.append(ValidationIssue("unsupported_conclusions", "unsupported conclusions must be flagged", "warning"))
    if not result.evidence:
        issues.append(ValidationIssue("reasoning_without_evidence", "reasoning should preserve supporting evidence", "warning"))
    return ValidationReport(valid=not any(issue.severity == "error" for issue in issues), issues=tuple(issues))


def _reasoning_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    return {
        "recommendation": getattr(value, "recommendation", None),
        "confidence": getattr(value, "confidence", 0.0),
        "reasoning_summary": getattr(value, "reasoning_summary", getattr(value, "summary", "")),
        "supporting_factors": tuple(getattr(value, "supporting_factors", ())),
        "risk_factors": tuple(getattr(value, "risk_factors", ())),
        "evidence": tuple(getattr(value, "evidence", ())),
        "assumptions": tuple(getattr(value, "assumptions", ())),
        "limitations": tuple(getattr(value, "limitations", ())),
        "unsupported_conclusions": tuple(getattr(value, "unsupported_conclusions", ())),
        "metadata": getattr(value, "metadata", {}),
    }
