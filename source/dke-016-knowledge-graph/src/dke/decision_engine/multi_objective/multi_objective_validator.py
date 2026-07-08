from __future__ import annotations

from .models import BalancedResult, MultiObjective, MultiObjectiveDecisionPackage, ObjectiveScore, TradeoffMatrix


class MultiObjectiveValidator:
    def validate_objectives(self, objectives: tuple[MultiObjective, ...]) -> None:
        if not objectives:
            raise ValueError("Multi-objective weights are required")
        total = sum(objective.weight for objective in objectives)
        if abs(total - 1.0) > 0.00001:
            raise ValueError(f"Multi-objective weights must sum to 1.0, got {total:.6f}")
        for objective in objectives:
            if not objective.objective_id.strip() or not objective.name.strip():
                raise ValueError("MultiObjective id and name are required")
            if not 0.0 <= objective.weight <= 1.0:
                raise ValueError(f"objective weight must be between 0 and 1 for {objective.name}")

    def validate_objective_score(self, score: ObjectiveScore) -> None:
        if not score.alternative_id.strip():
            raise ValueError("ObjectiveScore.alternative_id is required")
        self._validate_unit(score.weighted_score, "weighted score")
        self._validate_unit(score.source_learning_score, "source learning score")
        for name, value in score.scores.items():
            if not name.strip():
                raise ValueError("objective score name is required")
            self._validate_unit(value, f"objective score {name}")

    def validate_tradeoff_matrix(self, matrix: TradeoffMatrix) -> None:
        for alternative in matrix.alternatives:
            if alternative not in matrix.matrix:
                raise ValueError(f"tradeoff matrix missing alternative {alternative}")
        for left, distances in matrix.pairwise_tradeoffs.items():
            if left not in matrix.alternatives:
                raise ValueError(f"unknown tradeoff alternative {left}")
            for right, distance in distances.items():
                if right not in matrix.alternatives:
                    raise ValueError(f"unknown tradeoff comparison {right}")
                self._validate_unit(distance, "tradeoff distance")

    def validate_balanced_result(self, result: BalancedResult) -> None:
        if not result.alternative_id.strip():
            raise ValueError("BalancedResult.alternative_id is required")
        self._validate_unit(result.balance_score, "balance score")
        self._validate_unit(result.tradeoff_score, "tradeoff score")
        self.validate_objective_score(result.objective_score)

    def validate_package(self, package: MultiObjectiveDecisionPackage) -> None:
        if not isinstance(package, MultiObjectiveDecisionPackage):
            raise ValueError("Expected MultiObjectiveDecisionPackage")
        self.validate_objectives(package.objectives)
        for score in package.objective_scores:
            self.validate_objective_score(score)
        self.validate_tradeoff_matrix(package.tradeoff_matrix)
        for result in package.balanced_results:
            self.validate_balanced_result(result)
        if package.balanced_results and package.selected_result is None:
            raise ValueError("selected result is required when balanced results exist")
        if not package.balanced_results and package.selected_result is not None:
            raise ValueError("selected result must be None when no balanced results exist")
        if package.selected_result is not None and package.selected_result not in package.balanced_results:
            raise ValueError("selected result must be present in balanced results")

    def _validate_unit(self, value: float, field_name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field_name} must be between 0 and 1")
