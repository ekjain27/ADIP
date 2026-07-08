from __future__ import annotations

import logging

from decision_engine.optimization import OptimizedDecisionPackage, OptimizationResult

from .assumption_analyzer import AssumptionAnalyzer
from .models import UncertaintyDecisionPackage, UncertaintyResult
from .robustness_analyzer import RobustnessAnalyzer
from .sensitivity_analyzer import SensitivityAnalyzer
from .uncertainty_estimator import UncertaintyEstimator
from .uncertainty_package import UncertaintyPackageBuilder

logger = logging.getLogger(__name__)


class UncertaintyEngine:
    STRATEGY = "deterministic_uncertainty_sensitivity"

    def __init__(
        self,
        estimator: UncertaintyEstimator | None = None,
        sensitivity_analyzer: SensitivityAnalyzer | None = None,
        robustness_analyzer: RobustnessAnalyzer | None = None,
        assumption_analyzer: AssumptionAnalyzer | None = None,
        package_builder: UncertaintyPackageBuilder | None = None,
    ) -> None:
        self.estimator = estimator or UncertaintyEstimator()
        self.sensitivity_analyzer = sensitivity_analyzer or SensitivityAnalyzer()
        self.robustness_analyzer = robustness_analyzer or RobustnessAnalyzer()
        self.assumption_analyzer = assumption_analyzer or AssumptionAnalyzer()
        self.package_builder = package_builder or UncertaintyPackageBuilder()

    def analyze(self, optimized_package: OptimizedDecisionPackage) -> UncertaintyDecisionPackage:
        if not isinstance(optimized_package, OptimizedDecisionPackage):
            raise ValueError("UncertaintyEngine.analyze requires an OptimizedDecisionPackage")
        logger.info("Analyzing decision uncertainty and sensitivity")
        results = tuple(self._analyze_result(result) for result in optimized_package.optimized_results)
        selected = self._selected_result(results, optimized_package.selected_result)
        return self.package_builder.build(
            results,
            selected,
            uncertainty_strategy=self.STRATEGY,
            metadata={"source_optimization_strategy": optimized_package.optimization_strategy},
        )

    def _analyze_result(self, result: OptimizationResult) -> UncertaintyResult:
        uncertainty = self.estimator.estimate(result)
        reliability = self.estimator.reliability(result, uncertainty)
        interval = self.estimator.confidence_interval(result, uncertainty)
        sensitivity = self.sensitivity_analyzer.analyze(result)
        robustness = self.robustness_analyzer.analyze(result, sensitivity)
        assumptions = self.assumption_analyzer.analyze(result)
        return UncertaintyResult(
            alternative_id=result.alternative_id,
            uncertainty_score=uncertainty,
            reliability_score=reliability,
            confidence_interval=interval,
            robustness=robustness,
            sensitivity=sensitivity,
            assumptions=assumptions,
            explanation=self._explanation(result, uncertainty, reliability, robustness.robustness_score),
            metadata={
                "optimized_score": result.optimized_score,
                "original_score": result.original_score,
            },
        )

    def _selected_result(
        self,
        results: tuple[UncertaintyResult, ...],
        selected_optimized: OptimizationResult | None,
    ) -> UncertaintyResult | None:
        if not results:
            return None
        if selected_optimized is not None:
            for result in results:
                if result.alternative_id == selected_optimized.alternative_id:
                    return result
        return max(results, key=lambda result: result.reliability_score)

    def _explanation(
        self,
        result: OptimizationResult,
        uncertainty: float,
        reliability: float,
        robustness: float,
    ) -> str:
        return (
            f"Alternative {result.alternative_id} has uncertainty {uncertainty:.3f}, "
            f"reliability {reliability:.3f}, and robustness {robustness:.3f}."
        )
