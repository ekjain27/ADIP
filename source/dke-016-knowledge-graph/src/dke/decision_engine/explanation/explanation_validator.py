from __future__ import annotations

from .models import DecisionExplanation, ExplanationDecisionPackage, ExplanationSection


class ExplanationValidator:
    def validate(self, package: ExplanationDecisionPackage) -> None:
        if not isinstance(package, ExplanationDecisionPackage):
            raise ValueError("Expected ExplanationDecisionPackage")
        if package.total_explained != len(package.explanations):
            raise ValueError("total_explained does not match explanation count")
        if package.explanations and package.selected_explanation is None:
            raise ValueError("selected_explanation is required when explanations exist")
        if not package.explanations and package.selected_explanation is not None:
            raise ValueError("selected_explanation must be None when no explanations exist")
        for explanation in package.explanations:
            self.validate_explanation(explanation)

    def validate_explanation(self, explanation: DecisionExplanation) -> None:
        required_fields = (
            "alternative_id",
            "summary",
            "reasoning",
            "evidence_explanation",
            "risk_explanation",
            "scenario_explanation",
            "recommendation_explanation",
        )
        missing = [field for field in required_fields if not str(getattr(explanation, field, "")).strip()]
        if missing:
            raise ValueError(f"DecisionExplanation missing required fields: {', '.join(missing)}")
        if not 0.0 <= explanation.confidence <= 1.0:
            raise ValueError(f"Explanation confidence must be between 0 and 1 for {explanation.alternative_id}")
        if not explanation.sections:
            raise ValueError(f"DecisionExplanation sections are required for {explanation.alternative_id}")
        for section in explanation.sections:
            self.validate_section(section)

    def validate_section(self, section: ExplanationSection) -> None:
        if not section.section_id.strip():
            raise ValueError("ExplanationSection.section_id is required")
        if not section.title.strip():
            raise ValueError("ExplanationSection.title is required")
        if not section.content.strip():
            raise ValueError("ExplanationSection.content is required")
        if not 0.0 <= section.confidence <= 1.0:
            raise ValueError(f"Section confidence must be between 0 and 1 for {section.section_id}")
