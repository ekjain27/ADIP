from __future__ import annotations

from typing import Any, Callable, Mapping

from .observability_errors import HealthCheckError


class HealthRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], Mapping[str, Any]]] = {}

    def register_health_check(self, component: str, callback: Callable[[], Mapping[str, Any]]) -> None:
        normalized = self._normalize_component(component)
        if not callable(callback):
            raise HealthCheckError("health check callback must be callable")
        if normalized in self._checks:
            raise HealthCheckError(f"health check already registered: {normalized}")
        self._checks[normalized] = callback

    def run_health_checks(self, component: str | None = None) -> dict[str, Any]:
        if component is not None:
            normalized = self._normalize_component(component)
            if normalized not in self._checks:
                raise HealthCheckError(f"unknown health check component: {normalized}")
            components = (normalized,)
        else:
            components = tuple(sorted(self._checks))
        results = {}
        for name in components:
            result = self._checks[name]()
            if not isinstance(result, Mapping) or "status" not in result:
                raise HealthCheckError(f"health check returned malformed result: {name}")
            results[name] = dict(sorted(result.items()))
        return {
            "status": "healthy" if all(result["status"] == "healthy" for result in results.values()) else "degraded",
            "component_count": len(results),
            "components": results,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "health_check_count": len(self._checks),
            "components": tuple(sorted(self._checks)),
        }

    def _normalize_component(self, component: str) -> str:
        if not isinstance(component, str) or not component.strip():
            raise HealthCheckError("health check component is required")
        return component.strip().upper()
