from __future__ import annotations

from .decision_package import DecisionPackageBuilder
from .fallback import FallbackPolicy
from .interfaces import ReasoningPort, RetrievalPort
from .models import DecisionPackage, DecisionQuery, DecisionStatus, ReasoningResult
from .state import create_decision_state
from .trace import InMemoryTraceStore
from .validators import validate_context, validate_reasoning
from .workflow import DecisionWorkflow


class DecisionPipeline:
    def __init__(
        self,
        retrieval_adapter: RetrievalPort,
        reasoning_adapter: ReasoningPort,
        trace_store: InMemoryTraceStore | None = None,
        fallback_policy: FallbackPolicy | None = None,
        package_builder: DecisionPackageBuilder | None = None,
    ) -> None:
        self.retrieval_adapter = retrieval_adapter
        self.reasoning_adapter = reasoning_adapter
        self.trace_store = trace_store or InMemoryTraceStore()
        self.fallback_policy = fallback_policy or FallbackPolicy()
        self.package_builder = package_builder or DecisionPackageBuilder()
        self.workflow = DecisionWorkflow()

    def run(self, query: str | DecisionQuery, constraints: dict | None = None) -> DecisionPackage:
        state = create_decision_state(query, constraints)
        self.trace_store.start(state.decision_id)
        self.trace_store.record(state.decision_id, "pipeline_started", {"workflow": self.workflow.names()})

        state = state.transition(DecisionStatus.RETRIEVING)
        self.trace_store.record(state.decision_id, "retrieve_context_started")
        context = self.retrieval_adapter.retrieve_context(state.query)
        self.trace_store.record(state.decision_id, "retrieve_context_completed", {"facts": len(getattr(context, "facts", ()) or ())})

        state = state.transition(DecisionStatus.VALIDATING_CONTEXT, context_package=context)
        context_report = validate_context(context)
        self.trace_store.record(state.decision_id, "context_validated", {"valid": context_report.valid, "issues": [issue.code for issue in context_report.issues]})
        improved_context = self.fallback_policy.improve_context(self.retrieval_adapter, state.query, context, context_report)
        if improved_context is not context:
            context = improved_context
            context_report = validate_context(context)
            self.trace_store.record(state.decision_id, "broader_retrieval_applied", {"valid": context_report.valid})

        state = state.transition(DecisionStatus.REASONING, context_package=context, context_validation=context_report)
        self.trace_store.record(state.decision_id, "reasoning_started")
        reasoning = self.reasoning_adapter.reason(context, state.query)
        if not isinstance(reasoning, ReasoningResult):
            reasoning = ReasoningResult(**reasoning)
        self.trace_store.record(state.decision_id, "reasoning_completed", {"confidence": reasoning.confidence})

        state = state.transition(DecisionStatus.VALIDATING_REASONING, reasoning_result=reasoning)
        reasoning_report = validate_reasoning(reasoning)
        self.trace_store.record(state.decision_id, "reasoning_validated", {"valid": reasoning_report.valid, "issues": [issue.code for issue in reasoning_report.issues]})

        state = state.transition(DecisionStatus.APPLYING_FALLBACK, reasoning_validation=reasoning_report)
        final_reasoning = self.fallback_policy.apply_reasoning_fallback(reasoning, context_report, reasoning_report)
        if final_reasoning != reasoning:
            self.trace_store.record(state.decision_id, "fallback_applied", {"confidence": final_reasoning.confidence})

        trace = self.trace_store.get_trace(state.decision_id)
        if trace is None:
            trace = state.trace
        package = self.package_builder.build(state.query, final_reasoning, context, trace)
        self.trace_store.record(state.decision_id, "decision_package_built", {"confidence": package.confidence})
        final_trace = self.trace_store.get_trace(state.decision_id) or trace
        return self.package_builder.build(state.query, final_reasoning, context, final_trace)
