from __future__ import annotations

import importlib
import inspect
from typing import Any

from .interfaces import ReasoningPort, RetrievalPort
from .models import DecisionPackage, DecisionQuery, ReasoningResult
from .pipeline import DecisionPipeline
from .trace import InMemoryTraceStore


class RetrievalAdapter:
    def __init__(self, retrieval_module: Any | None = None) -> None:
        if retrieval_module is None:
            import knowledge_retrieval as retrieval_module
        self._retrieval = retrieval_module

    def retrieve_context(self, query: DecisionQuery) -> Any:
        retrieval_query = getattr(self._retrieval, "RetrievalQuery", None)
        if retrieval_query is not None:
            return self._retrieval.retrieve_context(self._build_retrieval_query(retrieval_query, query))
        return self._retrieval.retrieve_context(query.text)

    def retrieve_broader_context(self, query: DecisionQuery) -> Any:
        retrieval_query = getattr(self._retrieval, "RetrievalQuery", None)
        if retrieval_query is not None:
            return self._retrieval.retrieve_context(
                self._build_retrieval_query(
                    retrieval_query,
                    query,
                    broader_options={"max_results": 25, "max_depth": 4, "min_confidence": 0.0},
                )
            )
        return self.retrieve_context(query)

    def _build_retrieval_query(
        self,
        retrieval_query: Any,
        query: DecisionQuery,
        broader_options: dict[str, Any] | None = None,
    ) -> Any:
        kwargs = self._supported_retrieval_kwargs(retrieval_query)
        text_key = "query" if "query" in kwargs else "text"
        candidate: dict[str, Any] = {text_key: query.text}
        if "metadata" in kwargs:
            candidate["metadata"] = query.metadata
        for key, value in (broader_options or {}).items():
            if key in kwargs:
                candidate[key] = value
        try:
            return retrieval_query(**candidate)
        except TypeError:
            fallback_key = "text" if text_key == "query" else "query"
            candidate.pop(text_key, None)
            candidate[fallback_key] = query.text
            return retrieval_query(**candidate)

    def _supported_retrieval_kwargs(self, retrieval_query: Any) -> set[str]:
        try:
            signature = inspect.signature(retrieval_query)
        except (TypeError, ValueError):
            return {"text", "query", "metadata", "max_results", "max_depth", "min_confidence"}
        supported = set(signature.parameters)
        return supported or {"text", "query", "metadata", "max_results", "max_depth", "min_confidence"}


class ReasoningAdapter:
    def __init__(self, reasoning_service: Any | None = None) -> None:
        if reasoning_service is None:
            try:
                reasoning_service = importlib.import_module("knowledge_reasoning")
            except ModuleNotFoundError:
                reasoning_service = None
        self._reasoning = reasoning_service

    def reason(self, context_package: Any, query: DecisionQuery) -> ReasoningResult:
        if self._reasoning is None:
            raise RuntimeError(
                "DKE-017 public API is not importable as knowledge_reasoning; inject a DKE-017 service or wrapper exposing reason(...)."
            )
        if hasattr(self._reasoning, "reason"):
            raw = self._call_reason(self._reasoning.reason, context_package, query)
        elif hasattr(self._reasoning, "service") and hasattr(self._reasoning.service, "reason"):
            raw = self._call_reason(self._reasoning.service.reason, context_package, query)
        elif callable(self._reasoning):
            raw = self._call_reason(self._reasoning, context_package, query)
        else:
            raise TypeError("reasoning_service must be callable or expose reason(context_package, query)")
        return self._normalize_reasoning_result(raw, context_package, query)

    def _call_reason(self, reason_callable: Any, context_package: Any, query: DecisionQuery) -> Any:
        reasoning_query = self._build_reasoning_query(context_package, query)
        try:
            parameters = inspect.signature(reason_callable).parameters
        except (TypeError, ValueError):
            parameters = {}
        if len(parameters) <= 1:
            return reason_callable(reasoning_query)
        return reason_callable(context_package, query)

    def _build_reasoning_query(self, context_package: Any, query: DecisionQuery) -> dict[str, Any]:
        facts = tuple(getattr(context_package, "facts", ()) or ())
        first_fact = facts[0] if facts else None
        source_node_id = getattr(first_fact, "id", None) if first_fact is not None else None
        source_name = getattr(first_fact, "name", getattr(first_fact, "canonicalName", None)) if first_fact is not None else None
        return {
            "sourceNodeId": source_node_id,
            "sourceCanonicalName": source_name,
            "maxDepth": query.constraints.get("max_depth", 2),
            "minConfidence": query.constraints.get("min_confidence", 0.0),
            "includeConflicts": True,
            "includeMissingLinkSuggestions": True,
        }

    def _normalize_reasoning_result(self, raw: Any, context_package: Any, query: DecisionQuery) -> ReasoningResult:
        if isinstance(raw, ReasoningResult):
            return raw
        if isinstance(raw, dict):
            if "recommendation" in raw or "limitations" in raw:
                return ReasoningResult(**raw)
            return self._from_dke017_result(raw, context_package, query)
        return ReasoningResult(
            recommendation=getattr(raw, "recommendation", None),
            confidence=float(getattr(raw, "confidence", 0.0)),
            reasoning_summary=str(getattr(raw, "reasoning_summary", getattr(raw, "summary", ""))),
            supporting_factors=tuple(getattr(raw, "supporting_factors", ())),
            risk_factors=tuple(getattr(raw, "risk_factors", ())),
            evidence=tuple(getattr(raw, "evidence", getattr(context_package, "evidence", ()) or ())),
            assumptions=tuple(getattr(raw, "assumptions", ())),
            limitations=tuple(getattr(raw, "limitations", ())),
            unsupported_conclusions=tuple(getattr(raw, "unsupported_conclusions", ())),
            metadata=getattr(raw, "metadata", {}),
        )

    def _from_dke017_result(self, raw: dict[str, Any], context_package: Any, query: DecisionQuery) -> ReasoningResult:
        conclusions = tuple(raw.get("conclusions", ()) or ())
        conflicts = tuple(raw.get("conflicts", ()) or ())
        explanation = raw.get("explanation", {}) or {}
        confidence_values = [float(conclusion.get("confidence", 0.0)) for conclusion in conclusions if isinstance(conclusion, dict)]
        confidence = max(confidence_values, default=0.0)
        if confidence > 1:
            confidence = confidence / 100
        limitations = tuple(() if conclusions else ("DKE-017 returned no conclusions.",))
        return ReasoningResult(
            recommendation=None,
            confidence=confidence,
            reasoning_summary=str(explanation.get("summary", "DKE-017 reasoning completed.")),
            supporting_factors=tuple(str(conclusion.get("summary", conclusion.get("id", ""))) for conclusion in conclusions if isinstance(conclusion, dict)),
            risk_factors=tuple(str(conflict.get("description", conflict.get("id", ""))) for conflict in conflicts if isinstance(conflict, dict)),
            evidence=tuple(raw.get("evidence", getattr(context_package, "evidence", ()) or ())),
            assumptions=tuple(raw.get("assumptions", ())),
            limitations=limitations,
            unsupported_conclusions=tuple(raw.get("unsupported_conclusions", ())),
            metadata={"query": query.text, "source": "DKE-017", "raw": raw},
        )


class DecisionReasoningOrchestrator:
    def __init__(
        self,
        retrieval_adapter: RetrievalPort | None = None,
        reasoning_adapter: ReasoningPort | None = None,
        trace_store: InMemoryTraceStore | None = None,
    ) -> None:
        self.trace_store = trace_store or InMemoryTraceStore()
        self.pipeline = DecisionPipeline(
            retrieval_adapter=retrieval_adapter or RetrievalAdapter(),
            reasoning_adapter=reasoning_adapter or ReasoningAdapter(),
            trace_store=self.trace_store,
        )

    def start_decision(self, query: str | DecisionQuery) -> DecisionPackage:
        return self.run_pipeline(query)

    def run_pipeline(self, query: str | DecisionQuery, constraints: dict | None = None) -> DecisionPackage:
        return self.pipeline.run(query, constraints)

    def get_trace(self, decision_id: str) -> Any | None:
        return self.trace_store.get_trace(decision_id)
