from __future__ import annotations

from typing import Any, Mapping


def generate_report(results: tuple[Mapping[str, Any], ...], diagnostics: tuple[str, ...] = ()) -> dict[str, Any]:
    failed = tuple(result for result in results if result["status"] != "passed")
    return {
        "module": "VB-001",
        "report_type": "end_to_end_regression",
        "status": "passed" if not failed and not diagnostics else "failed",
        "workflow_count": len(results),
        "failed_count": len(failed),
        "workflows": tuple(_normalize(result) for result in results),
        "diagnostics": diagnostics,
    }


def summarize_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "module": "VB-001",
        "status": report["status"],
        "workflow_count": report["workflow_count"],
        "failed_count": report["failed_count"],
        "diagnostic_count": len(report["diagnostics"]),
    }


def _normalize(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: payload[key] for key in sorted(payload)}
