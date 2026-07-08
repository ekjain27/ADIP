from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .paper_errors import DuplicateAcronymError, MalformedPaperMetadataError


@dataclass(frozen=True)
class AcronymEntry:
    acronym: str
    expansion: str

    def __post_init__(self) -> None:
        if not self.acronym.strip() or not self.expansion.strip():
            raise MalformedPaperMetadataError("acronym and expansion are required")

    def snapshot(self) -> dict[str, str]:
        return {"acronym": self.acronym, "expansion": self.expansion}


def default_acronyms() -> tuple[AcronymEntry, ...]:
    return (
        AcronymEntry("ADBM", "Adaptive Decision Behavior Model"),
        AcronymEntry("ADWG", "Adaptive Decision Workflow Graph"),
        AcronymEntry("DDGM", "Dynamic Decision Governance Mesh"),
        AcronymEntry("DHMF", "Decision Health Monitoring Framework"),
        AcronymEntry("DIE", "Decision Intelligence Engine"),
        AcronymEntry("DKE", "Domain Knowledge Extraction"),
        AcronymEntry("DOC", "Documentation"),
        AcronymEntry("DPG", "Decision Provenance Graph"),
        AcronymEntry("DRIF", "Decision Recommendation Interface Framework"),
        AcronymEntry("EDOF", "Enterprise Decision Orchestration Framework"),
        AcronymEntry("PAT", "Patent Preparation"),
        AcronymEntry("PI", "Platform Integration"),
        AcronymEntry("RP", "Research Paper"),
        AcronymEntry("TDLL", "Temporal Decision Lineage Ledger"),
        AcronymEntry("VB", "Validation And Benchmarking"),
    )


def generate_acronym_registry(acronyms: tuple[AcronymEntry, ...] | None = None) -> dict[str, Any]:
    entries = tuple(sorted(acronyms or default_acronyms(), key=lambda entry: entry.acronym))
    seen: set[str] = set()
    for entry in entries:
        if entry.acronym in seen:
            raise DuplicateAcronymError(f"duplicate acronym: {entry.acronym}")
        seen.add(entry.acronym)
    return {
        "module": "RP-001",
        "registry_type": "acronym_registry",
        "status": "generated",
        "acronym_count": len(entries),
        "acronyms": tuple(entry.snapshot() for entry in entries),
    }
