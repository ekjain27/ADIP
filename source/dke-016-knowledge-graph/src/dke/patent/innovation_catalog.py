from __future__ import annotations

from typing import Any, Mapping

INNOVATION_MODULES = ("DPG", "DDGM", "TDLL", "ADBM", "ADWG", "DHMF", "DRIF", "EDOF")

INNOVATION_TITLES: Mapping[str, str] = {
    "DPG": "Decision Provenance Graph",
    "DDGM": "Dynamic Decision Governance Mesh",
    "TDLL": "Temporal Decision Lineage Ledger",
    "ADBM": "Adaptive Decision Behavior Model",
    "ADWG": "Autonomous Decision Workflow Graph",
    "DHMF": "Decision Health Monitoring Fabric",
    "DRIF": "Decision Recommendation Intelligence Framework",
    "EDOF": "Enterprise Decision Orchestration Fabric",
}

ARCHITECTURAL_CONTRIBUTIONS: Mapping[str, str] = {
    "DPG": "Links decisions to deterministic provenance records and evidence lineage.",
    "DDGM": "Applies governance validation as a reusable platform-level compliance boundary.",
    "TDLL": "Maintains temporal lineage continuity across multi-stage decision workflows.",
    "ADBM": "Captures adaptive behavior state without mutating core decision generation logic.",
    "ADWG": "Coordinates workflow execution across platform components through a stable orchestration boundary.",
    "DHMF": "Unifies health, metrics, traces, and audit-forwarding for decision operations.",
    "DRIF": "Produces recommendation-facing outputs from governed and traceable decision payloads.",
    "EDOF": "Provides enterprise-level orchestration over integrated decision platform services.",
}


def novelty_summary(component_id: str) -> str:
    return (
        f"{INNOVATION_TITLES[component_id]} is implemented as part of a deterministic, "
        "registry-discoverable decision intelligence architecture with validation and documentation traceability."
    )


def innovation_description(component_id: str, runtime_metadata: Mapping[str, Any]) -> str:
    capabilities = ", ".join(runtime_metadata.get("capabilities", ())) or "platform capability"
    return f"{INNOVATION_TITLES[component_id]} exposes {capabilities} through module {component_id}."
