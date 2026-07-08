from __future__ import annotations

from typing import Any

from .adapters import DecisionPackageAdapter, EvidenceAdapter
from .models import ClaimEvidenceLink


class EvidenceLinker:
    def __init__(self) -> None:
        self.evidence_adapter = EvidenceAdapter()

    def link_evidence(self, decision_package: Any, context_package: Any | None = None) -> tuple[ClaimEvidenceLink, ...]:
        package = DecisionPackageAdapter(decision_package)
        evidence_items = list(package.evidence())
        if context_package is not None:
            evidence_items.extend(tuple(getattr(context_package, "evidence", ()) or ()))
        refs = tuple({ref.evidence_id: ref for ref in (self.evidence_adapter.to_reference(item) for item in evidence_items)}.values())
        return tuple(ClaimEvidenceLink(claim=claim, evidence_refs=refs, supported=bool(refs)) for claim in package.claims())
