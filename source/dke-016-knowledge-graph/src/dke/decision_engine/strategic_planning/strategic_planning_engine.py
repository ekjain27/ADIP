from __future__ import annotations

import logging

from decision_engine.multi_objective import BalancedResult, MultiObjectiveDecisionPackage

from .checkpoint_generator import CheckpointGenerator
from .dependency_graph import DependencyGraphBuilder
from .execution_planner import ExecutionPlanner
from .goal_decomposer import GoalDecomposer
from .milestone_generator import MilestoneGenerator
from .models import StrategicPlan, StrategicPlanningGraph
from .planning_package import PlanningPackageBuilder
from .planning_validator import PlanningValidator

logger = logging.getLogger(__name__)


class StrategicPlanningEngine:
    STRATEGY = "deterministic_hierarchical_strategic_planning_graph"

    def __init__(
        self,
        goal_decomposer: GoalDecomposer | None = None,
        milestone_generator: MilestoneGenerator | None = None,
        dependency_graph_builder: DependencyGraphBuilder | None = None,
        execution_planner: ExecutionPlanner | None = None,
        checkpoint_generator: CheckpointGenerator | None = None,
        package_builder: PlanningPackageBuilder | None = None,
        validator: PlanningValidator | None = None,
    ) -> None:
        self.goal_decomposer = goal_decomposer or GoalDecomposer()
        self.milestone_generator = milestone_generator or MilestoneGenerator()
        self.dependency_graph_builder = dependency_graph_builder or DependencyGraphBuilder()
        self.execution_planner = execution_planner or ExecutionPlanner()
        self.checkpoint_generator = checkpoint_generator or CheckpointGenerator()
        self.package_builder = package_builder or PlanningPackageBuilder()
        self.validator = validator or PlanningValidator()

    def plan(self, multi_objective_package: MultiObjectiveDecisionPackage):
        if not isinstance(multi_objective_package, MultiObjectiveDecisionPackage):
            raise ValueError("StrategicPlanningEngine.plan requires a MultiObjectiveDecisionPackage")
        logger.info("Running deterministic strategic planning")
        plans = tuple(self._plan_result(result, multi_objective_package.summary) for result in multi_objective_package.balanced_results)
        selected = self._selected_plan(plans, multi_objective_package.selected_result)
        return self.package_builder.build(
            plans,
            selected,
            planning_strategy=self.STRATEGY,
            metadata={
                "source_optimization_strategy": multi_objective_package.optimization_strategy,
                "balanced_result_count": len(multi_objective_package.balanced_results),
            },
        )

    def _plan_result(self, result: BalancedResult, package_summary: str) -> StrategicPlan:
        goals, objectives = self.goal_decomposer.decompose(result)
        milestones = self.milestone_generator.generate(result.alternative_id, objectives)
        phases = self.execution_planner.generate(result.alternative_id, milestones)
        checkpoints = self.checkpoint_generator.generate(result.alternative_id)
        dependencies = self.dependency_graph_builder.build(goals, objectives, milestones, phases)
        graph = StrategicPlanningGraph(
            vision=f"Execute {result.alternative_id} as a balanced strategic decision.",
            strategic_goals=goals,
            objective_nodes=objectives,
            milestones=milestones,
            execution_phases=phases,
            dependencies=dependencies,
            checkpoints=checkpoints,
            metadata={
                "hspg_version": "1.0",
                "source_summary": package_summary,
                "balance_score": result.balance_score,
            },
        )
        self.validator.validate_graph(graph)
        return StrategicPlan(
            alternative_id=result.alternative_id,
            planning_graph=graph,
            timeline_summary=self._timeline_summary(milestones, phases),
            execution_summary=f"Execute {len(phases)} phases across {len(milestones)} milestones.",
            risk_summary=self._risk_summary(result),
            recommendations=self._recommendations(result),
            metadata={"selected_reason": result.selected_reason},
        )

    def _selected_plan(self, plans: tuple[StrategicPlan, ...], selected_result: BalancedResult | None) -> StrategicPlan | None:
        if not plans:
            return None
        if selected_result is not None:
            for plan in plans:
                if plan.alternative_id == selected_result.alternative_id:
                    return plan
        return plans[0]

    def _timeline_summary(self, milestones, phases) -> str:
        if not milestones:
            return "No milestones are required."
        return f"{len(milestones)} milestones planned from {milestones[0].target_completion} to {milestones[-1].target_completion} across {len(phases)} phases."

    def _risk_summary(self, result: BalancedResult) -> str:
        risk_score = result.objective_score.scores.get("risk", 0.0)
        if risk_score >= 0.75:
            return "Risk posture is favorable; monitor adaptive checkpoints."
        if risk_score >= 0.5:
            return "Risk posture is moderate; maintain mitigation checkpoints."
        return "Risk posture requires active mitigation and escalation readiness."

    def _recommendations(self, result: BalancedResult) -> tuple[str, ...]:
        return (
            "Assign accountable owners for each strategic goal.",
            "Review objective KPI progress at every adaptive checkpoint.",
            f"Preserve the selected balance score of {result.balance_score:.3f} during execution.",
        )
