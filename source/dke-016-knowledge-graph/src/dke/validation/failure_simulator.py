from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .stress_errors import UnsupportedFailureSimulationError

SUPPORTED_FAILURE_MODES = ("none", "component_unavailable", "dependency_failure")


@dataclass(frozen=True)
class FailureSimulationResult:
    mode: str
    target: str
    status: str
    error: str | None
    recovery_action: str
    retry_attempts: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "target": self.target,
            "status": self.status,
            "error": self.error,
            "recovery_action": self.recovery_action,
            "retry_attempts": self.retry_attempts,
        }


class FailureSimulator:
    def simulate_failure(self, mode: str, target: str, retry_attempts: int = 1) -> FailureSimulationResult:
        if mode not in SUPPORTED_FAILURE_MODES:
            raise UnsupportedFailureSimulationError(f"unsupported failure simulation: {mode}")
        if mode == "none":
            return FailureSimulationResult(mode, target, "stable", None, "not_required", 0)
        if mode == "component_unavailable":
            return FailureSimulationResult(mode, target, "degraded", f"{target} unavailable", "fallback_route", retry_attempts)
        return FailureSimulationResult(mode, target, "degraded", f"{target} dependency failed", "retry_then_recover", retry_attempts)


def normalize_failure_result(result: FailureSimulationResult | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(result, FailureSimulationResult):
        return result.to_dict()
    return {key: result[key] for key in sorted(result)}
