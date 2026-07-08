from __future__ import annotations

from .models import ScenarioAnalysisDecisionPackage, ScenarioComparison, ScenarioDefinition, ScenarioEvaluation


class ScenarioValidator:
    VALID_RECOMMENDATIONS = {"strong", "moderate", "weak", "unstable"}

    def validate_scenario(self, scenario: ScenarioDefinition) -> None:
        if not scenario.scenario_id.strip():
            raise ValueError("ScenarioDefinition.scenario_id is required")
        if not 0.0 <= scenario.probability <= 1.0:
            raise ValueError(f"Scenario probability must be between 0 and 1 for {scenario.scenario_id}")

    def validate_evaluation(self, evaluation: ScenarioEvaluation) -> None:
        self.validate_scenario(evaluation.scenario)
        if not evaluation.alternative_id.strip():
            raise ValueError("ScenarioEvaluation.alternative_id is required")
        for field_name in ("decision_score", "risk_score", "confidence", "robustness"):
            value = getattr(evaluation, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")

    def validate_comparison(self, comparison: ScenarioComparison) -> None:
        if not comparison.alternative_id.strip():
            raise ValueError("ScenarioComparison.alternative_id is required")
        for field_name in ("average_score", "best_score", "worst_score", "stability_score"):
            value = getattr(comparison, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
        if comparison.recommendation not in self.VALID_RECOMMENDATIONS:
            raise ValueError(f"Invalid scenario recommendation: {comparison.recommendation}")
        scenario_ids = [evaluation.scenario.scenario_id for evaluation in comparison.evaluations]
        if len(scenario_ids) != len(set(scenario_ids)):
            raise ValueError("Scenario evaluations must reference unique scenarios")
        for evaluation in comparison.evaluations:
            if evaluation.alternative_id != comparison.alternative_id:
                raise ValueError("Scenario evaluation alternative_id does not match comparison")
            self.validate_evaluation(evaluation)

    def validate_package(self, package: ScenarioAnalysisDecisionPackage) -> None:
        if not isinstance(package, ScenarioAnalysisDecisionPackage):
            raise ValueError("Expected ScenarioAnalysisDecisionPackage")
        if package.scenario_comparisons and package.selected_comparison is None:
            raise ValueError("selected_comparison is required when scenario comparisons exist")
        if not package.scenario_comparisons and package.selected_comparison is not None:
            raise ValueError("selected_comparison must be None when no comparisons exist")
        for comparison in package.scenario_comparisons:
            self.validate_comparison(comparison)
