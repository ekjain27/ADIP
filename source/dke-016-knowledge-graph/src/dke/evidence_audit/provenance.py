from __future__ import annotations

from typing import Any

from .adapters import DecisionPackageAdapter
from .evidence_linker import EvidenceLinker
from .models import ProvenanceRecord


class ProvenanceTracker:
    def create_records(self, decision_package: Any, context_package: Any | None = None) -> tuple[ProvenanceRecord, ...]:
        package = DecisionPackageAdapter(decision_package)
        links = EvidenceLinker().link_evidence(decision_package, context_package)
        records = [
            ProvenanceRecord(
                subject_id=package.decision_id,
                subject_type="decision",
                source_module="DKE-019",
                evidence_refs=tuple(ref for link in links for ref in link.evidence_refs),
                metadata={"recommendation": package.recommendation},
            )
        ]
        records.extend(
            ProvenanceRecord(
                subject_id=link.link_id,
                subject_type="claim",
                source_module="DKE-020",
                evidence_refs=link.evidence_refs,
                metadata={"claim": link.claim, "supported": link.supported},
            )
            for link in links
        )
        return tuple(records)
