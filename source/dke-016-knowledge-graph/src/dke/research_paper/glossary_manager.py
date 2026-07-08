from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .paper_errors import GlossaryConsistencyError


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    definition: str
    source_module: str

    def __post_init__(self) -> None:
        if not self.term.strip() or not self.definition.strip() or not self.source_module.strip():
            raise GlossaryConsistencyError("glossary term, definition, and source module are required")

    def snapshot(self) -> dict[str, str]:
        return {"term": self.term, "definition": self.definition, "source_module": self.source_module}


def default_glossary_terms() -> tuple[GlossaryTerm, ...]:
    return (
        GlossaryTerm("contract adapter", "A deterministic mapping layer for cross-engine payload normalization.", "PI-003"),
        GlossaryTerm("deployment readiness", "A deterministic assessment of platform readiness without executing deployment.", "PI-008"),
        GlossaryTerm("innovation registry", "A structured catalog of architecture mechanisms prepared for patent-support artifacts.", "PAT-001"),
        GlossaryTerm("platform integration layer", "A reusable boundary for registering and executing platform components.", "PI-001"),
        GlossaryTerm("runtime registry", "A deterministic registry for module metadata, dependencies, capabilities, and compatibility.", "PI-002"),
        GlossaryTerm("validation benchmark", "A deterministic framework for measuring regression, quality, performance, governance, and stress behavior.", "VB"),
    )


def generate_glossary(terms: tuple[GlossaryTerm, ...] | None = None) -> dict[str, Any]:
    entries = tuple(sorted(terms or default_glossary_terms(), key=lambda entry: entry.term))
    seen: set[str] = set()
    for entry in entries:
        if entry.term in seen:
            raise GlossaryConsistencyError(f"duplicate glossary term: {entry.term}")
        seen.add(entry.term)
    return {
        "module": "RP-001",
        "registry_type": "terminology_glossary",
        "status": "generated",
        "term_count": len(entries),
        "terms": tuple(entry.snapshot() for entry in entries),
    }
