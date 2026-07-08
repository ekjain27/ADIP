from __future__ import annotations

from typing import Any

from .models import DecisionPackage, DecisionQuery, DecisionTrace, ReasoningResult


class DecisionPackageBuilder:
    def build(self, query: DecisionQuery, reasoning_result: ReasoningResult, context_package: Any, trace: DecisionTrace) -> DecisionPackage:
        recommendation = reasoning_result.recommendation or "No strong recommendation"
        evidence = tuple(reasoning_result.evidence or getattr(context_package, "evidence", ()) or ())
        return DecisionPackage(
            decision_id=trace.decision_id,
            query=query.text,
            recommendation=recommendation,
            confidence=reasoning_result.confidence,
            reasoning_summary=reasoning_result.reasoning_summary,
            supporting_factors=tuple(reasoning_result.supporting_factors),
            risk_factors=tuple(reasoning_result.risk_factors),
            evidence=evidence,
            assumptions=tuple(reasoning_result.assumptions),
            limitations=tuple(reasoning_result.limitations),
            trace=trace,
            metadata={
                "orchestrator": "DKE-019",
                "context_confidence": getattr(context_package, "confidence", None),
                "reasoning_metadata": dict(reasoning_result.metadata),
            },
        )


def build_decision_package(reasoning_result: ReasoningResult, query: DecisionQuery | None = None, context_package: Any | None = None, trace: DecisionTrace | None = None) -> DecisionPackage:
    decision_trace = trace or DecisionTrace(decision_id="decision-preview").add("package_preview")
    decision_query = query or DecisionQuery(text=str(reasoning_result.metadata.get("query", "decision")))
    return DecisionPackageBuilder().build(decision_query, reasoning_result, context_package, decision_trace)
