from __future__ import annotations

import importlib
from typing import Any

from .models import EvidenceReference


class ModuleCompatibility:
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name

    def available(self) -> bool:
        try:
            importlib.import_module(self.module_name)
        except ModuleNotFoundError:
            return False
        return True


class DecisionPackageAdapter:
    def __init__(self, decision_package: Any) -> None:
        self.package = decision_package

    @property
    def decision_id(self) -> str:
        return str(getattr(self.package, "decision_id"))

    @property
    def query(self) -> str:
        return str(getattr(self.package, "query", ""))

    @property
    def recommendation(self) -> str:
        return str(getattr(self.package, "recommendation", ""))

    @property
    def confidence(self) -> float:
        value = float(getattr(self.package, "confidence", 0.0) or 0.0)
        return value if value <= 1 else value / 100

    def claims(self) -> tuple[str, ...]:
        values = (*tuple(getattr(self.package, "supporting_factors", ()) or ()), self.recommendation)
        return tuple(str(item) for item in values if item)

    def risks(self) -> tuple[str, ...]:
        return tuple(str(item) for item in getattr(self.package, "risk_factors", ()) or ())

    def assumptions(self) -> tuple[str, ...]:
        return tuple(str(item) for item in getattr(self.package, "assumptions", ()) or ())

    def limitations(self) -> tuple[str, ...]:
        return tuple(str(item) for item in getattr(self.package, "limitations", ()) or ())

    def evidence(self) -> tuple[Any, ...]:
        return tuple(getattr(self.package, "evidence", ()) or ())

    def trace_events(self) -> tuple[Any, ...]:
        trace = getattr(self.package, "trace", None)
        return tuple(getattr(trace, "events", ()) or ())


class DKE019DecisionPackageAdapter(DecisionPackageAdapter):
    module = ModuleCompatibility("decision_orchestrator")


class DKE018ContextPackageAdapter:
    module = ModuleCompatibility("knowledge_retrieval")

    def __init__(self, context_package: Any) -> None:
        self.context = context_package

    @property
    def query(self) -> Any:
        return getattr(self.context, "query", None)

    def facts(self) -> tuple[Any, ...]:
        return tuple(getattr(self.context, "facts", ()) or ())

    def relationships(self) -> tuple[Any, ...]:
        return tuple(getattr(self.context, "relationships", ()) or ())

    def evidence(self) -> tuple[Any, ...]:
        return tuple(getattr(self.context, "evidence", ()) or ())

    @property
    def confidence(self) -> float:
        value = float(getattr(self.context, "confidence", 0.0) or 0.0)
        return value if value <= 1 else value / 100


class EvidenceAdapter:
    def to_reference(self, item: Any) -> EvidenceReference:
        evidence_id = str(getattr(item, "id", getattr(item, "evidence_id", item)))
        confidence = float(getattr(item, "confidence", 1.0) or 0.0)
        return EvidenceReference(
            evidence_id=evidence_id,
            source=str(getattr(item, "source", "")),
            excerpt=str(getattr(item, "excerpt", "")),
            confidence=confidence,
            metadata=dict(getattr(item, "metadata", {}) or {}),
        )


class ReasoningOutputAdapter:
    module = ModuleCompatibility("knowledge_reasoning")

    def __init__(self, reasoning_output: Any) -> None:
        self.output = reasoning_output

    def evidence(self) -> tuple[Any, ...]:
        if isinstance(self.output, dict):
            return tuple(self.output.get("evidence", ()) or ())
        return tuple(getattr(self.output, "evidence", ()) or ())

    def unsupported_claims(self) -> tuple[str, ...]:
        if isinstance(self.output, dict):
            value = self.output.get("unsupported_conclusions", ())
        else:
            value = getattr(self.output, "unsupported_conclusions", ())
        return tuple(str(item) for item in value or ())

    def reasoning_steps(self) -> tuple[Any, ...]:
        if isinstance(self.output, dict):
            explanation = self.output.get("explanation", {}) or {}
            return tuple(explanation.get("steps", ()) or self.output.get("conclusions", ()) or ())
        explanation = getattr(self.output, "explanation", None)
        return tuple(getattr(explanation, "steps", ()) or getattr(self.output, "conclusions", ()) or ())


class DKE017ReasoningOutputAdapter(ReasoningOutputAdapter):
    module = ModuleCompatibility("knowledge_reasoning")
