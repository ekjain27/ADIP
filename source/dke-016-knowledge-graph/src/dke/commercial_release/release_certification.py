from __future__ import annotations

from typing import Any

from .production_readiness import generate_production_readiness, validate_release_candidate
from .readiness_scorecard import generate_readiness_score
from .release_metrics import generate_release_metrics

RELEASE_CERTIFICATION_VERSION = "REL-005.1"


def generate_release_certification(readiness: dict[str, Any] | None = None) -> dict[str, Any]:
    active_readiness = readiness or generate_production_readiness()
    validation = validate_release_candidate(active_readiness)
    scorecard = active_readiness["scorecard"]
    certification = {
        "module": "REL-005",
        "certification_version": RELEASE_CERTIFICATION_VERSION,
        "status": "certified",
        "decision": scorecard["decision"],
        "final_production_score": scorecard["scores"]["Final Production Score"],
        "production_readiness": active_readiness,
        "release_metrics": active_readiness["release_metrics"],
        "release_scorecard": scorecard,
        "validation": validation,
        "reports": {
            **active_readiness["reports"],
            "release_certification.md": _release_certification_markdown(scorecard),
        },
        "json_artifacts": {
            "production_readiness.json": active_readiness,
            "release_certification.json": {
                "module": "REL-005",
                "status": "certified",
                "decision": scorecard["decision"],
                "final_production_score": scorecard["scores"]["Final Production Score"],
            },
            "release_metrics.json": active_readiness["release_metrics"],
            "release_scorecard.json": scorecard,
        },
        "integrity": {
            "deployment_actions_performed": False,
            "infrastructure_executed": False,
            "production_modules_modified": False,
        },
    }
    return certification


def certify_production_release(readiness: dict[str, Any] | None = None) -> dict[str, Any]:
    return generate_release_certification(readiness)


def _release_certification_markdown(scorecard: dict[str, Any]) -> str:
    return (
        "# Release Certification\n\n"
        f"Decision: {scorecard['decision']}\n\n"
        f"Overall Readiness: {scorecard['scores']['Overall Readiness']}\n\n"
        f"Final Production Score: {scorecard['scores']['Final Production Score']}\n\n"
        "Certification is deterministic and does not deploy software."
    )


__all__ = [
    "certify_production_release",
    "generate_production_readiness",
    "generate_readiness_score",
    "generate_release_certification",
    "generate_release_metrics",
    "validate_release_candidate",
]
