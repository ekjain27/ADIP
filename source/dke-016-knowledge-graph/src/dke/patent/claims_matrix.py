from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .claims_errors import MalformedClaimMetadataError
from .claims_traceability import ClaimTraceability


@dataclass(frozen=True)
class ClaimMapping:
    claim_id: str
    innovation_id: str
    claim_type: str
    claim_candidate: str
    supporting_modules: tuple[str, ...]
    supporting_apis: tuple[str, ...]
    architectural_mechanisms: tuple[str, ...]
    implementation_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.claim_type not in {"independent", "dependent"}:
            raise MalformedClaimMetadataError(f"malformed claim type: {self.claim_type}")
        required = {
            "claim_id": self.claim_id,
            "innovation_id": self.innovation_id,
            "claim_candidate": self.claim_candidate,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MalformedClaimMetadataError(f"malformed claim metadata: {', '.join(missing)}")
        if not self.supporting_modules or not self.architectural_mechanisms or not self.implementation_evidence:
            raise MalformedClaimMetadataError(f"claim mapping lacks support: {self.claim_id}")

    def traceability(self) -> ClaimTraceability:
        return ClaimTraceability(
            innovation_id=self.innovation_id,
            claim_id=self.claim_id,
            modules=self.supporting_modules,
            apis=self.supporting_apis,
            evidence=self.implementation_evidence,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "innovation_id": self.innovation_id,
            "claim_type": self.claim_type,
            "claim_candidate": self.claim_candidate,
            "supporting_modules": self.supporting_modules,
            "supporting_apis": self.supporting_apis,
            "supporting_architectural_mechanisms": self.architectural_mechanisms,
            "implementation_evidence": self.implementation_evidence,
        }


def export_claims_matrix_markdown(mappings: tuple[ClaimMapping, ...]) -> str:
    lines = [
        "# Claims Mapping Matrix",
        "",
        "| Claim ID | Innovation | Type | Supporting Modules | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mapping in sorted(mappings, key=lambda item: item.claim_id):
        lines.append(
            f"| {mapping.claim_id} | {mapping.innovation_id} | {mapping.claim_type} | "
            f"{', '.join(mapping.supporting_modules)} | {', '.join(mapping.implementation_evidence)} |"
        )
    return "\n".join(lines) + "\n"
