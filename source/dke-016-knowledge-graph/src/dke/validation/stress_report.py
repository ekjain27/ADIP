from __future__ import annotations

from typing import Any

from .resilience_scorecard import ResilienceScorecard


def generate_stress_report(scorecards: tuple[ResilienceScorecard, ...], executions: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    passed = sum(1 for scorecard in scorecards if scorecard.status == "passed")
    average_score = round(sum(scorecard.score for scorecard in scorecards) / len(scorecards), 6) if scorecards else 0.0
    return {
        "module": "VB-005",
        "report_type": "enterprise_stress_failure_testing",
        "status": "passed" if passed == len(scorecards) else "failed",
        "scenario_count": len(scorecards),
        "passed_count": passed,
        "failed_count": len(scorecards) - passed,
        "average_resilience_score": average_score,
        "scorecards": tuple(scorecard.to_dict() for scorecard in scorecards),
        "executions": tuple(_normalize_execution(execution) for execution in sorted(executions, key=lambda item: item["scenario_id"])),
    }


def _normalize_execution(execution: dict[str, Any]) -> dict[str, Any]:
    return {key: execution[key] for key in sorted(execution)}
