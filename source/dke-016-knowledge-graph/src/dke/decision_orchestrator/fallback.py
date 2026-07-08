from __future__ import annotations

from dataclasses import replace
from typing import Any

from .models import DecisionQuery, ReasoningResult, ValidationReport


class FallbackPolicy:
    def improve_context(self, retrieval_adapter: Any, query: DecisionQuery, context_package: Any, report: ValidationReport) -> Any:
        codes = {issue.code for issue in report.issues}
        if "weak_context" in codes or "empty_context" in codes:
            broader = getattr(retrieval_adapter, "retrieve_broader_context", None)
            if callable(broader):
                return broader(query)
        return context_package

    def apply_reasoning_fallback(self, reasoning_result: ReasoningResult, context_report: ValidationReport, reasoning_report: ValidationReport) -> ReasoningResult:
        limitations = list(reasoning_result.limitations)
        confidence = reasoning_result.confidence
        if any(issue.code == "missing_evidence" for issue in context_report.issues):
            confidence *= 0.85
            limitations.append("Evidence coverage is limited.")
        if reasoning_result.unsupported_conclusions:
            confidence *= 0.75
            limitations.append("Unsupported conclusions were flagged and down-weighted.")
        if confidence < 0.5 and reasoning_result.recommendation:
            limitations.append("Confidence is below threshold; treat recommendation as tentative.")
        if reasoning_report.blocking:
            limitations.append("Reasoning result is incomplete; returning partial decision.")
            return replace(reasoning_result, recommendation=reasoning_result.recommendation or "Partial decision only", confidence=confidence, limitations=tuple(dict.fromkeys(limitations)))
        return replace(reasoning_result, confidence=confidence, limitations=tuple(dict.fromkeys(limitations)))
