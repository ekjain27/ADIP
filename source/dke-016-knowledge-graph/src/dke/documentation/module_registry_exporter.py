from __future__ import annotations

from typing import Any

from .module_registry_models import PHASE_LABELS, PHASE_ORDER, ModuleRegistryEntry


def export_registry_markdown(registry: dict[str, Any]) -> str:
    lines = [
        "# Project-1 Module Registry",
        "",
        f"Status: {registry['status']}",
        f"Module count: {registry['statistics']['module_count']}",
        "",
    ]
    grouped = registry["modules_by_phase"]
    for phase in PHASE_ORDER:
        label = PHASE_LABELS[phase]
        lines.extend([f"## {label}", ""])
        entries = grouped.get(phase, ())
        if not entries:
            lines.extend(["- No modules registered.", ""])
            continue
        for entry in entries:
            dependencies = ", ".join(entry["dependencies"]) if entry["dependencies"] else "none"
            interfaces = ", ".join(entry["public_interfaces"])
            lines.append(f"- {entry['module_id']} - {entry['module_name']} ({entry['status']}, v{entry['version']})")
            lines.append(f"  - Dependencies: {dependencies}")
            lines.append(f"  - Public interfaces: {interfaces}")
            lines.append(f"  - Description: {entry['description']}")
        lines.append("")
    return "\n".join(lines)


def export_registry_json(registry: dict[str, Any]) -> dict[str, Any]:
    return _normalize(registry)


def registry_entries_to_phase_map(entries: tuple[ModuleRegistryEntry, ...]) -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = {phase: [] for phase in PHASE_ORDER}
    for entry in entries:
        grouped[entry.phase].append(entry.snapshot())
    return {
        phase: tuple(sorted(values, key=lambda item: item["module_id"]))
        for phase, values in grouped.items()
    }


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize(item) for item in value)
    return value
