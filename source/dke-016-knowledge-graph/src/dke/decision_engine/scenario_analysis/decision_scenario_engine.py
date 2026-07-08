from __future__ import annotations

import logging

from decision_engine.uncertainty import UncertaintyDecisionPackage, UncertaintyResult

from .models import ScenarioAnalysisDecisionPackage, ScenarioComparison
from .scenario_comparator import ScenarioComparator
from .scenario_evaluator import ScenarioEvaluator
from .scenario_generator import ScenarioGenerator
from .scenario_package import ScenarioPackageBuilder

logger = logging.getLogger(__name__)


class DecisionScenarioEngine:
    STRATEGY = "deterministic_multi_scenario_analysis"

    def __init__(
        self,
        scenario_generator: ScenarioGenerator | None = None,
        evaluator: ScenarioEvaluator | None = None,
        comparator: ScenarioComparator | None = None,
        package_builder: ScenarioPackageBuilder | None = None,
    ) -> None:
        self.scenario_generator = scenario_generator or ScenarioGenerator()
        self.evaluator = evaluator or ScenarioEvaluator()
        self.comparator = comparator or ScenarioComparator()
        self.package_builder = package_builder or ScenarioPackageBuilder()

    def analyze(self, uncertainty_package: UncertaintyDecisionPackage) -> ScenarioAnalysisDecisionPackage:
        if not isinstance(uncertainty_package, UncertaintyDecisionPackage):
            raise ValueError("DecisionScenarioEngine.analyze requires an UncertaintyDecisionPackage")
        logger.info("Running multi-scenario decision analysis")
        scenarios = self.scenario_generator.generate()
        comparisons = tuple(self._compare_result(result, scenarios) for result in uncertainty_package.uncertainty_results)
        selected = self._selected_comparison(comparisons, uncertainty_package.selected_result)
        return self.package_builder.build(
            comparisons,
            selected,
            scenario_strategy=self.STRATEGY,
            metadata={"source_uncertainty_strategy": uncertainty_package.uncertainty_strategy, "scenario_count": len(scenarios)},
        )

    def _compare_result(self, result: UncertaintyResult, scenarios) -> ScenarioComparison:
        evaluations = tuple(self.evaluator.evaluate(result, scenario) for scenario in scenarios)
        return self.comparator.compare(result.alternative_id, evaluations)

    def _selected_comparison(
        self,
        comparisons: tuple[ScenarioComparison, ...],
        selected_result: UncertaintyResult | None,
    ) -> ScenarioComparison | None:
        if not comparisons:
            return None
        if selected_result is not None:
            for comparison in comparisons:
                if comparison.alternative_id == selected_result.alternative_id:
                    return comparison
        return max(comparisons, key=lambda item: (item.average_score, item.stability_score))
