from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .deployment_errors import DuplicateManifestEntryError


DETERMINISTIC_DEPLOYMENT_TIMESTAMP = "1970-01-01T00:00:00Z"
VALID_DEPLOYMENT_PROFILES: tuple[str, ...] = ("local", "test", "staging", "production")


@dataclass(frozen=True)
class ReleaseManifestEntry:
    module_id: str
    name: str
    version: str = "1.0.0"
    status: str = "ready"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "metadata": dict(sorted(self.metadata.items())),
        }


@dataclass(frozen=True)
class ReleaseManifest:
    manifest_id: str
    entries: tuple[ReleaseManifestEntry, ...]
    created_at: str = DETERMINISTIC_DEPLOYMENT_TIMESTAMP

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for entry in self.entries:
            if entry.module_id in seen:
                raise DuplicateManifestEntryError(f"duplicate manifest entry: {entry.module_id}")
            seen.add(entry.module_id)
        object.__setattr__(self, "entries", tuple(sorted(self.entries, key=lambda entry: entry.module_id)))

    def snapshot(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "created_at": self.created_at,
            "entry_count": len(self.entries),
            "entries": tuple(entry.snapshot() for entry in self.entries),
        }


def build_release_manifest(entries: tuple[ReleaseManifestEntry, ...]) -> ReleaseManifest:
    return ReleaseManifest(manifest_id="project-1-platform-integration-release", entries=entries)
