from __future__ import annotations

from typing import Any

from platform_integration import UnifiedPlatformRuntimeRegistry

from .documentation_errors import DocumentationRegistryError


def generate_module_catalog(runtime_registry: UnifiedPlatformRuntimeRegistry) -> dict[str, Any]:
    if not isinstance(runtime_registry, UnifiedPlatformRuntimeRegistry):
        raise DocumentationRegistryError("runtime_registry must be UnifiedPlatformRuntimeRegistry")
    components = runtime_registry.list_runtime_components()
    phases: dict[str, list[str]] = {}
    catalog_entries = []
    for component in components:
        phases.setdefault(component.phase, []).append(component.module_id)
        catalog_entries.append(
            {
                "module_id": component.module_id,
                "name": component.name,
                "phase": component.phase,
                "version": component.version,
                "status": component.status,
                "capabilities": component.capabilities,
                "dependencies": component.dependencies,
                "contracts": component.contracts,
                "frozen": component.frozen,
            }
        )
    return {
        "catalog_type": "module_catalog",
        "module_count": len(catalog_entries),
        "phases": tuple((phase, tuple(sorted(module_ids))) for phase, module_ids in sorted(phases.items())),
        "modules": tuple(sorted(catalog_entries, key=lambda item: item["module_id"])),
    }
