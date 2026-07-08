from __future__ import annotations

from typing import Any

from .operations_errors import DuplicateOperationalProcedureError

OPERATIONAL_PROCEDURES = (
    "deployment_architecture",
    "supported_environments",
    "installation_workflow",
    "configuration_workflow",
    "runtime_startup_sequence",
    "operational_lifecycle",
    "monitoring_guide",
    "logging_guide",
    "backup_restore_procedures",
    "upgrade_procedure",
    "rollback_procedure",
    "disaster_recovery_guide",
    "maintenance_schedule",
    "troubleshooting_guide",
    "security_recommendations",
)


def generate_operations_manual_content(context: dict[str, Any]) -> dict[str, Any]:
    procedures = (
        ("deployment_architecture", ("Use PI-008 readiness boundary", "Document platform services without external deployment execution")),
        ("supported_environments", tuple(context["environments"])),
        ("installation_workflow", ("Prepare environment", "Install project dependencies", "Run regression tests")),
        ("configuration_workflow", ("Create PI-005 config", "Validate config", "Freeze deployment snapshot")),
        ("runtime_startup_sequence", ("Initialize PI-001", "Load PI-002", "Enable PI-004", "Enable PI-007")),
        ("operational_lifecycle", ("Validate", "Observe", "Document", "Maintain")),
        ("monitoring_guide", ("Use PI-007 health checks", "Export observability snapshot")),
        ("logging_guide", ("Use deterministic log levels", "Forward audit events through PI-007")),
        ("backup_restore_procedures", ("Export config snapshot", "Export runtime registry snapshot", "Restore deterministic snapshots")),
        ("upgrade_procedure", context["maintenance_plan"]["upgrade_procedure"]),
        ("rollback_procedure", context["maintenance_plan"]["rollback_procedure"]),
        ("disaster_recovery_guide", ("Use latest exported manifests", "Rerun readiness report", "Rerun regression suite")),
        ("maintenance_schedule", tuple(item["procedure"] for item in context["maintenance_plan"]["schedule"])),
        ("troubleshooting_guide", ("Inspect readiness report", "Inspect observability snapshot", "Inspect runtime registry")),
        ("security_recommendations", ("Do not store secrets", "Keep configs immutable", "Use internal gateway actions only")),
    )
    section_ids = tuple(section for section, _ in procedures)
    duplicates = tuple(section for section in section_ids if section_ids.count(section) > 1)
    if duplicates:
        raise DuplicateOperationalProcedureError(f"duplicate operational procedure(s): {', '.join(sorted(set(duplicates)))}")
    return {
        "manual_type": "enterprise_operations_manual",
        "status": "generated",
        "procedures": tuple({"id": section, "steps": tuple(steps)} for section, steps in procedures),
    }


def export_operations_markdown(manual: dict[str, Any], manifest: dict[str, Any]) -> str:
    lines = [
        "# Enterprise Deployment Guide & Operations Manual",
        "",
        "Module: DOC-005",
        f"Manifest version: {manifest['manifest_version']}",
        "",
    ]
    for procedure in manual["procedures"]:
        lines.extend([f"## {procedure['id'].replace('_', ' ').title()}", ""])
        lines.extend(f"- {step}" for step in procedure["steps"])
        lines.append("")
    return "\n".join(lines)
