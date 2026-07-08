from __future__ import annotations

from typing import Any

from .invention_registry import InnovationRecord
from .patent_errors import MalformedDisclosureError


def generate_invention_disclosure(innovation_registry: dict[str, Any], documentation_trace: dict[str, Any]) -> dict[str, Any]:
    if innovation_registry.get("module") != "PAT-001" or not innovation_registry.get("innovations"):
        raise MalformedDisclosureError("innovation registry is required for disclosure")
    disclosure = {
        "module": "PAT-001",
        "artifact_type": "invention_disclosure",
        "status": "generated",
        "title": "AI Decision Intelligence Platform Architecture",
        "technical_field": "Deterministic decision intelligence, governance, provenance, validation, and enterprise orchestration.",
        "problem_statement": "Enterprise decision systems require traceable, governed, validated, and reproducible integration boundaries.",
        "solution_summary": "The platform integrates decision, provenance, governance, lineage, monitoring, recommendation, and orchestration components through deterministic registry-discoverable infrastructure.",
        "innovation_count": innovation_registry["innovation_count"],
        "innovation_ids": tuple(item["innovation_id"] for item in innovation_registry["innovations"]),
        "documentation_trace": documentation_trace,
    }
    validate_invention_disclosure(disclosure)
    return disclosure


def validate_invention_disclosure(disclosure: dict[str, Any]) -> dict[str, Any]:
    required = ("module", "artifact_type", "status", "title", "technical_field", "problem_statement", "solution_summary", "innovation_ids")
    missing = tuple(field for field in required if field not in disclosure or disclosure[field] in (None, "", ()))
    if missing:
        raise MalformedDisclosureError(f"malformed invention disclosure: {', '.join(missing)}")
    return {"module": "PAT-001", "status": "valid", "innovation_count": len(disclosure["innovation_ids"])}


def export_disclosure_markdown(disclosure: dict[str, Any], innovations: tuple[InnovationRecord, ...]) -> str:
    validate_invention_disclosure(disclosure)
    lines = [
        "# Invention Disclosure Draft",
        "",
        f"Title: {disclosure['title']}",
        f"Technical field: {disclosure['technical_field']}",
        "",
        "## Problem Statement",
        disclosure["problem_statement"],
        "",
        "## Solution Summary",
        disclosure["solution_summary"],
        "",
        "## Innovations",
    ]
    for record in sorted(innovations, key=lambda item: item.innovation_id):
        lines.append(f"- {record.innovation_id}: {record.title}")
        lines.append(f"  - Related modules: {', '.join(record.related_modules)}")
        lines.append(f"  - Contribution: {record.architectural_contribution}")
        lines.append(f"  - Novelty: {record.novelty_summary}")
    return "\n".join(lines) + "\n"
