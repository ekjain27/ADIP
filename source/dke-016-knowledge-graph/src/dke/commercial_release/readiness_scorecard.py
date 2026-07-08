from __future__ import annotations

from typing import Any

READINESS_SCORECARD_VERSION = "REL-005.1"

CERTIFICATION_AREAS = (
    "documentation",
    "validation",
    "commercial",
    "deployment",
    "research",
    "patent",
    "repository",
)


def generate_readiness_score(readiness: dict[str, Any] | None = None) -> dict[str, Any]:
    areas = readiness.get("certification_areas", {}) if readiness else _default_areas()
    scores = {
        area: _score_area(areas.get(area, {}))
        for area in CERTIFICATION_AREAS
    }
    overall = round(sum(scores.values()) / len(scores), 2)
    final_score = 0 if any(score == 0 for score in scores.values()) else min(overall, scores["validation"], scores["repository"])
    return {
        "module": "REL-005",
        "scorecard_version": READINESS_SCORECARD_VERSION,
        "status": "generated",
        "scores": {
            "Documentation": scores["documentation"],
            "Validation": scores["validation"],
            "Commercial": scores["commercial"],
            "Deployment": scores["deployment"],
            "Research": scores["research"],
            "Patent": scores["patent"],
            "Repository": scores["repository"],
            "Overall Readiness": overall,
            "Final Production Score": final_score,
        },
        "decision": _decision(final_score),
        "scoring_policy": {
            "complete_area_score": 100,
            "incomplete_area_score": 0,
            "ready_for_release_candidate_threshold": 85,
            "ready_for_production_threshold": 100,
        },
    }


def _score_area(area: dict[str, Any]) -> int:
    artifacts = area.get("artifacts", ())
    if area.get("status") != "complete" or not artifacts:
        return 0
    return 100 if all(artifact.get("status") == "complete" for artifact in artifacts) else 0


def _decision(final_score: float) -> str:
    if final_score >= 100:
        return "READY_FOR_PRODUCTION"
    if final_score >= 85:
        return "READY_FOR_RELEASE_CANDIDATE"
    return "NOT_READY"


def _default_areas() -> dict[str, Any]:
    return {
        area: {"status": "complete", "artifacts": ({"artifact_id": f"{area}-default", "status": "complete"},)}
        for area in CERTIFICATION_AREAS
    }
