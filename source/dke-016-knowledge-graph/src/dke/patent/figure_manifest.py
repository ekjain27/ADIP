from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .specification_errors import DuplicateFigureError, MalformedSpecificationSectionError

FIGURE_MANIFEST_VERSION = "PAT-004-FIG.1"


@dataclass(frozen=True)
class PatentFigure:
    figure_id: str
    title: str
    description: str
    related_modules: tuple[str, ...]
    figure_type: str = "architecture_metadata"

    def __post_init__(self) -> None:
        required = {
            "figure_id": self.figure_id,
            "title": self.title,
            "description": self.description,
            "figure_type": self.figure_type,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MalformedSpecificationSectionError(f"malformed figure metadata: {', '.join(missing)}")
        if not self.related_modules:
            raise MalformedSpecificationSectionError(f"figure lacks related modules: {self.figure_id}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "title": self.title,
            "description": self.description,
            "related_modules": self.related_modules,
            "figure_type": self.figure_type,
        }


def generate_figure_manifest(figures: tuple[PatentFigure, ...]) -> dict[str, Any]:
    validate_figure_manifest(figures)
    ordered = tuple(sorted(figures, key=lambda figure: figure.figure_id))
    return {
        "module": "PAT-004",
        "manifest_version": FIGURE_MANIFEST_VERSION,
        "manifest_type": "figure_manifest",
        "status": "generated",
        "figure_count": len(ordered),
        "figures": tuple(figure.snapshot() for figure in ordered),
    }


def validate_figure_manifest(figures: tuple[PatentFigure, ...]) -> dict[str, Any]:
    seen: set[str] = set()
    for figure in figures:
        if not isinstance(figure, PatentFigure):
            raise MalformedSpecificationSectionError("figure manifest entries must be PatentFigure")
        if figure.figure_id in seen:
            raise DuplicateFigureError(f"duplicate figure ID: {figure.figure_id}")
        seen.add(figure.figure_id)
    return {"module": "PAT-004", "status": "valid", "figure_count": len(figures)}
