from __future__ import annotations

from typing import Any

from .paper_errors import InconsistentPublicationProfileError

SUPPORTED_TARGET_VENUES = ("IEEE", "Springer", "Elsevier", "arXiv")
SUPPORTED_PUBLICATION_PROFILES = ("conference", "journal", "preprint", "technical_report")


def validate_publication_profile(publication_profile: str, target_venue_profile: str) -> dict[str, Any]:
    if publication_profile not in SUPPORTED_PUBLICATION_PROFILES:
        raise InconsistentPublicationProfileError(f"unsupported publication profile: {publication_profile}")
    if target_venue_profile not in SUPPORTED_TARGET_VENUES:
        raise InconsistentPublicationProfileError(f"unsupported target venue profile: {target_venue_profile}")
    return {
        "module": "RP-001",
        "status": "valid",
        "publication_profile": publication_profile,
        "target_venue_profile": target_venue_profile,
    }
