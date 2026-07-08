from .decision_package import DecisionPackageBuilder, build_decision_package
from .fallback import FallbackPolicy
from .models import (
    DecisionPackage,
    DecisionQuery,
    DecisionState,
    DecisionStatus,
    DecisionTrace,
    DecisionTraceEvent,
    ReasoningResult,
    ValidationIssue,
    ValidationReport,
)
from .orchestrator import DecisionReasoningOrchestrator, ReasoningAdapter, RetrievalAdapter
from .pipeline import DecisionPipeline
from .state import create_decision_state
from .trace import InMemoryTraceStore
from .validators import validate_context, validate_reasoning
from .workflow import DecisionWorkflow

_default_orchestrator: DecisionReasoningOrchestrator | None = None


def _get_default_orchestrator() -> DecisionReasoningOrchestrator:
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = DecisionReasoningOrchestrator()
    return _default_orchestrator


def start_decision(query):
    return _get_default_orchestrator().start_decision(query)


def run_pipeline(query, constraints=None):
    return _get_default_orchestrator().run_pipeline(query, constraints)


def get_trace(decision_id):
    return _get_default_orchestrator().get_trace(decision_id)


__all__ = [
    "DecisionPackage",
    "DecisionPackageBuilder",
    "DecisionPipeline",
    "DecisionQuery",
    "DecisionReasoningOrchestrator",
    "DecisionState",
    "DecisionStatus",
    "DecisionTrace",
    "DecisionTraceEvent",
    "DecisionWorkflow",
    "FallbackPolicy",
    "InMemoryTraceStore",
    "ReasoningAdapter",
    "ReasoningResult",
    "RetrievalAdapter",
    "ValidationIssue",
    "ValidationReport",
    "build_decision_package",
    "create_decision_state",
    "get_trace",
    "run_pipeline",
    "start_decision",
    "validate_context",
    "validate_reasoning",
]
