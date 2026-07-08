from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .claims_errors import InconsistentTraceabilityError, MissingEvidenceReferenceError


@dataclass(frozen=True)
class ClaimTraceability:
    innovation_id: str
    claim_id: str
    modules: tuple[str, ...]
    apis: tuple[str, ...]
    evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.innovation_id or not self.claim_id or not self.modules:
            raise InconsistentTraceabilityError("claim traceability requires innovation, claim, and modules")
        if not self.evidence:
            raise MissingEvidenceReferenceError(f"claim lacks evidence references: {self.claim_id}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "innovation_id": self.innovation_id,
            "claim_id": self.claim_id,
            "modules": self.modules,
            "apis": self.apis,
            "evidence": self.evidence,
        }


def generate_traceability_report(traceability: tuple[ClaimTraceability, ...]) -> dict[str, Any]:
    return {
        "module": "PAT-002",
        "report_type": "claims_traceability",
        "status": "generated",
        "trace_count": len(traceability),
        "traces": tuple(item.snapshot() for item in sorted(traceability, key=lambda item: item.claim_id)),
    }
