from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .novelty_errors import InconsistentNoveltyTraceabilityError, MalformedComparisonRecordError


@dataclass(frozen=True)
class NoveltyComparisonRecord:
    analysis_id: str
    innovation_id: str
    reference_id: str
    comparison_summary: str
    distinguishing_characteristics: tuple[str, ...]
    implementation_evidence: tuple[str, ...]
    supporting_modules: tuple[str, ...]

    def __post_init__(self) -> None:
        required = {
            "analysis_id": self.analysis_id,
            "innovation_id": self.innovation_id,
            "reference_id": self.reference_id,
            "comparison_summary": self.comparison_summary,
        }
        missing = tuple(field for field, value in required.items() if not isinstance(value, str) or not value.strip())
        if missing:
            raise MalformedComparisonRecordError(f"malformed comparison record: {', '.join(missing)}")
        if not self.distinguishing_characteristics or not self.supporting_modules:
            raise MalformedComparisonRecordError(f"comparison record lacks distinguishing support: {self.analysis_id}")
        if not self.implementation_evidence:
            raise InconsistentNoveltyTraceabilityError(f"comparison record lacks implementation evidence: {self.analysis_id}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "innovation_id": self.innovation_id,
            "reference_id": self.reference_id,
            "comparison_summary": self.comparison_summary,
            "distinguishing_characteristics": self.distinguishing_characteristics,
            "implementation_evidence": self.implementation_evidence,
            "supporting_modules": self.supporting_modules,
        }


def export_novelty_matrix_markdown(records: tuple[NoveltyComparisonRecord, ...]) -> str:
    lines = [
        "# Novelty Matrix",
        "",
        "| Analysis ID | Innovation | Reference | Distinguishing Characteristics | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in sorted(records, key=lambda item: item.analysis_id):
        lines.append(
            f"| {record.analysis_id} | {record.innovation_id} | {record.reference_id} | "
            f"{'; '.join(record.distinguishing_characteristics)} | {', '.join(record.implementation_evidence)} |"
        )
    return "\n".join(lines) + "\n"
