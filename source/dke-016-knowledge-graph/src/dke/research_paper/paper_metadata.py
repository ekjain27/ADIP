from __future__ import annotations

from typing import Any

from .paper_errors import MalformedPaperMetadataError
from .publication_profiles import validate_publication_profile

PAPER_METADATA_VERSION = "RP-001.1"
DETERMINISTIC_GENERATED_TIMESTAMP = "2026-06-29T00:00:00Z"


def generate_metadata(
    authors: tuple[dict[str, Any], ...] | None = None,
    affiliations: tuple[str, ...] | None = None,
    correspondence: dict[str, str] | None = None,
    publication_profile: str = "technical_report",
    target_venue_profile: str = "arXiv",
) -> dict[str, Any]:
    validate_publication_profile(publication_profile, target_venue_profile)
    active_authors = authors or ({"name": "Configurable Author", "affiliation_id": "AFF-001", "orcid": ""},)
    active_affiliations = affiliations or ("AFF-001: Configurable Research Organization",)
    active_correspondence = correspondence or {"name": "Configurable Author", "email": "correspondence@example.invalid"}
    _validate_authors(active_authors)
    if not active_affiliations or any(not isinstance(item, str) or not item.strip() for item in active_affiliations):
        raise MalformedPaperMetadataError("affiliations are required")
    if not active_correspondence.get("name") or not active_correspondence.get("email"):
        raise MalformedPaperMetadataError("correspondence metadata requires name and email")
    return {
        "module": "RP-001",
        "metadata_version": PAPER_METADATA_VERSION,
        "version": "1.0.0",
        "revision": "RP-001",
        "generated_timestamp": DETERMINISTIC_GENERATED_TIMESTAMP,
        "document_identifier": "AIDIP-PROJECT1-RP-001",
        "publication_profile": publication_profile,
        "target_venue_profile": target_venue_profile,
        "authors": tuple(dict(author) for author in active_authors),
        "affiliations": active_affiliations,
        "correspondence": dict(active_correspondence),
    }


def _validate_authors(authors: tuple[dict[str, Any], ...]) -> None:
    if not authors:
        raise MalformedPaperMetadataError("at least one author is required")
    for author in authors:
        if not author.get("name") or not author.get("affiliation_id"):
            raise MalformedPaperMetadataError("author metadata requires name and affiliation_id")
