from __future__ import annotations

from typing import Any

from .publication_errors import MalformedPublicationProfileError

SUPPORTED_PUBLICATION_VENUES = ("IEEE", "ACM", "Springer", "Elsevier", "arXiv")

_PROFILE_DETAILS: dict[str, dict[str, Any]] = {
    "IEEE": {
        "profile_type": "conference_or_journal",
        "citation_style": "numeric",
        "requires_camera_ready_claim": False,
        "supports_preprint": False,
        "formatting_status": "template_ready_markdown",
    },
    "ACM": {
        "profile_type": "conference_or_journal",
        "citation_style": "author_year_or_numeric",
        "requires_camera_ready_claim": False,
        "supports_preprint": False,
        "formatting_status": "template_ready_markdown",
    },
    "Springer": {
        "profile_type": "conference_or_journal",
        "citation_style": "venue_specific",
        "requires_camera_ready_claim": False,
        "supports_preprint": False,
        "formatting_status": "template_ready_markdown",
    },
    "Elsevier": {
        "profile_type": "journal",
        "citation_style": "venue_specific",
        "requires_camera_ready_claim": False,
        "supports_preprint": False,
        "formatting_status": "template_ready_markdown",
    },
    "arXiv": {
        "profile_type": "preprint",
        "citation_style": "user_supplied",
        "requires_camera_ready_claim": False,
        "supports_preprint": True,
        "formatting_status": "preprint_markdown",
    },
}


def generate_publication_profile(venue: str = "arXiv") -> dict[str, Any]:
    normalized = _normalize_venue(venue)
    details = _PROFILE_DETAILS[normalized]
    profile = {
        "module": "RP-005",
        "profile_version": "RP-005.1",
        "venue": normalized,
        "status": "generated",
        "supported_venues": SUPPORTED_PUBLICATION_VENUES,
        "profile_type": details["profile_type"],
        "citation_style": details["citation_style"],
        "formatting_status": details["formatting_status"],
        "requires_camera_ready_claim": details["requires_camera_ready_claim"],
        "supports_preprint": details["supports_preprint"],
        "submission_material_policy": {
            "references_must_be_user_supplied": True,
            "reviewer_responses_fabricated": False,
            "acceptance_claims_fabricated": False,
            "experimental_results_fabricated": False,
        },
    }
    validate_publication_package_profile(profile)
    return profile


def validate_publication_package_profile(profile: dict[str, Any]) -> dict[str, Any]:
    venue = profile.get("venue")
    if venue not in SUPPORTED_PUBLICATION_VENUES:
        raise MalformedPublicationProfileError(f"unsupported publication venue: {venue}")
    required = (
        "module",
        "profile_version",
        "venue",
        "status",
        "profile_type",
        "citation_style",
        "formatting_status",
        "submission_material_policy",
    )
    missing = tuple(field for field in required if field not in profile or profile[field] in ("", None))
    if missing:
        raise MalformedPublicationProfileError(f"malformed publication profile: {missing}")
    policy = profile["submission_material_policy"]
    if policy.get("reviewer_responses_fabricated") is not False or policy.get("acceptance_claims_fabricated") is not False:
        raise MalformedPublicationProfileError("publication profile cannot claim reviewer responses or acceptance")
    return {
        "module": "RP-005",
        "status": "valid",
        "venue": venue,
    }


def _normalize_venue(venue: str) -> str:
    if not isinstance(venue, str) or not venue.strip():
        raise MalformedPublicationProfileError("publication venue is required")
    lookup = {item.lower(): item for item in SUPPORTED_PUBLICATION_VENUES}
    normalized = lookup.get(venue.strip().lower())
    if normalized is None:
        raise MalformedPublicationProfileError(f"unsupported publication venue: {venue}")
    return normalized
