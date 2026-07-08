from __future__ import annotations

from typing import Any

from platform_integration import DeploymentReadinessLayer, UnifiedPlatformRuntimeRegistry

from .module_catalog import generate_module_catalog


def generate_architecture_summary(
    runtime_registry: UnifiedPlatformRuntimeRegistry,
    deployment_readiness: DeploymentReadinessLayer,
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    module_catalog = generate_module_catalog(runtime_registry)
    deployment_snapshot = deployment_readiness.export_deployment_snapshot()
    return {
        "summary_type": "architecture_summary",
        "platform": "AI Decision Intelligence Platform - Project-1",
        "status": "documented",
        "runtime_component_count": module_catalog["module_count"],
        "deployment_status": deployment_snapshot["status"],
        "validation_status": validation_summary["status"],
        "phases": module_catalog["phases"],
    }


def generate_dependency_graph(runtime_registry: UnifiedPlatformRuntimeRegistry) -> tuple[str, ...]:
    lines = []
    for component in runtime_registry.list_runtime_components():
        dependencies = ", ".join(component.dependencies) if component.dependencies else "none"
        lines.append(f"{component.module_id} -> {dependencies}")
    return tuple(sorted(lines))


def generate_integration_catalog(deployment_readiness: DeploymentReadinessLayer, validation_summary: dict[str, Any]) -> dict[str, Any]:
    deployment_snapshot = deployment_readiness.export_deployment_snapshot()
    inventory = deployment_snapshot["platform_inventory"]
    return {
        "catalog_type": "integration_catalog",
        "platform_components": inventory["platform_components"],
        "gateway_routes": inventory["gateway_routes"],
        "deployment_module": deployment_snapshot["module"],
        "validation_modules": validation_summary["modules"],
        "integration_points": (
            "PI-001 platform execution boundary",
            "PI-002 runtime registry source of truth",
            "PI-004 internal API gateway",
            "PI-008 deployment readiness boundary",
            "VB-001 through VB-005 validation and benchmarking",
        ),
    }
