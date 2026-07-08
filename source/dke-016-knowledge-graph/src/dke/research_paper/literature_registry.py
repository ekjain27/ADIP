from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .literature_errors import (
    DuplicateLiteratureEntryError,
    LiteratureRegistryValidationError,
    MalformedLiteratureRecordError,
)


@dataclass(frozen=True)
class LiteratureEntry:
    title: str
    authors: tuple[str, ...]
    publication_venue: str
    publication_year: int
    keywords: tuple[str, ...]
    research_domain: str
    summary: str
    relevance_tags: tuple[str, ...]
    identifier: str | None = None

    def to_record(self) -> dict[str, Any]:
        _validate_entry(self)
        literature_id = self.identifier.strip() if self.identifier else _derived_literature_id(self)
        return {
            "literature_id": literature_id,
            "title": self.title.strip(),
            "authors": tuple(author.strip() for author in self.authors),
            "publication_venue": self.publication_venue.strip(),
            "publication_year": self.publication_year,
            "identifier": self.identifier.strip() if self.identifier else None,
            "keywords": tuple(keyword.strip() for keyword in self.keywords),
            "research_domain": self.research_domain.strip(),
            "summary": self.summary.strip(),
            "relevance_tags": tuple(tag.strip() for tag in self.relevance_tags),
            "citation_fabricated": False,
        }


def register_literature(entries: tuple[LiteratureEntry, ...]) -> dict[str, Any]:
    if not entries:
        raise MalformedLiteratureRecordError("at least one literature entry is required")
    records = tuple(entry.to_record() for entry in entries)
    validate_literature_registry(records)
    ordered = tuple(sorted(records, key=lambda item: (item["publication_year"], item["title"].lower(), item["literature_id"])))
    return {
        "module": "RP-002",
        "registry_version": "RP-002.1",
        "status": "registered",
        "entry_count": len(ordered),
        "literature_ids": tuple(record["literature_id"] for record in ordered),
        "entries": ordered,
    }


def validate_literature_registry(records: tuple[dict[str, Any], ...] | dict[str, Any]) -> dict[str, Any]:
    active_records = tuple(records["entries"]) if isinstance(records, dict) and "entries" in records else tuple(records)
    ids: list[str] = []
    citation_keys: list[tuple[Any, ...]] = []
    identifiers: list[str] = []
    for record in active_records:
        _validate_record(record)
        ids.append(record["literature_id"])
        if record.get("identifier"):
            identifiers.append(record["identifier"].lower())
        citation_keys.append(
            (
                record["title"].lower(),
                tuple(author.lower() for author in record["authors"]),
                record["publication_year"],
            )
        )
    if len(ids) != len(set(ids)):
        raise DuplicateLiteratureEntryError("duplicate literature IDs are not allowed")
    if len(identifiers) != len(set(identifiers)):
        raise DuplicateLiteratureEntryError("duplicate literature identifiers are not allowed")
    if len(citation_keys) != len(set(citation_keys)):
        raise DuplicateLiteratureEntryError("duplicate literature citation metadata is not allowed")
    return {
        "module": "RP-002",
        "status": "valid",
        "entry_count": len(active_records),
        "unique_identifier_count": len(identifiers),
        "citation_fabricated": False,
    }


def _validate_entry(entry: LiteratureEntry) -> None:
    if not entry.title.strip():
        raise MalformedLiteratureRecordError("title is required")
    if not entry.authors or any(not author.strip() for author in entry.authors):
        raise MalformedLiteratureRecordError("authors are required")
    if not entry.publication_venue.strip():
        raise MalformedLiteratureRecordError("publication venue is required")
    if not isinstance(entry.publication_year, int) or entry.publication_year < 1900:
        raise MalformedLiteratureRecordError("valid publication year is required")
    if not entry.keywords or any(not keyword.strip() for keyword in entry.keywords):
        raise MalformedLiteratureRecordError("keywords are required")
    if not entry.research_domain.strip() or not entry.summary.strip():
        raise MalformedLiteratureRecordError("research domain and summary are required")
    if not entry.relevance_tags or any(not tag.strip() for tag in entry.relevance_tags):
        raise MalformedLiteratureRecordError("relevance tags are required")


def _validate_record(record: dict[str, Any]) -> None:
    required = (
        "literature_id",
        "title",
        "authors",
        "publication_venue",
        "publication_year",
        "keywords",
        "research_domain",
        "summary",
        "relevance_tags",
    )
    missing = tuple(field for field in required if field not in record or record[field] in ("", (), None))
    if missing:
        raise LiteratureRegistryValidationError(f"missing literature metadata: {missing}")


def _derived_literature_id(entry: LiteratureEntry) -> str:
    lead_author = entry.authors[0].split()[-1].lower()
    title_token = "".join(character.lower() for character in entry.title if character.isalnum())[:24]
    return f"{lead_author}-{entry.publication_year}-{title_token}"
