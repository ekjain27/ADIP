from __future__ import annotations

from typing import Any

from .constraint_engine import ConstraintEngine
from .context_loader import ContextLoader
from .decision_package import DecisionPackageBuilder
from .decision_state_builder import DecisionStateBuilder
from .evidence_normalizer import EvidenceNormalizer
from .goal_extractor import GoalExtractor
from .models import DecisionPackage


class DIECore:
    def __init__(
        self,
        context_loader: ContextLoader | None = None,
        evidence_normalizer: EvidenceNormalizer | None = None,
        goal_extractor: GoalExtractor | None = None,
        constraint_engine: ConstraintEngine | None = None,
        decision_state_builder: DecisionStateBuilder | None = None,
        decision_package_builder: DecisionPackageBuilder | None = None,
    ) -> None:
        self.context_loader = context_loader or ContextLoader()
        self.evidence_normalizer = evidence_normalizer or EvidenceNormalizer()
        self.goal_extractor = goal_extractor or GoalExtractor()
        self.constraint_engine = constraint_engine or ConstraintEngine()
        self.decision_state_builder = decision_state_builder or DecisionStateBuilder()
        self.decision_package_builder = decision_package_builder or DecisionPackageBuilder()

    def process(self, context_package: Any) -> DecisionPackage:
        loaded_context = self.context_loader.load(context_package)
        evidence = self.evidence_normalizer.normalize(loaded_context)
        goals = self.goal_extractor.extract(loaded_context)
        constraints = self.constraint_engine.extract(loaded_context)
        decision_state = self.decision_state_builder.build(evidence, goals, constraints, loaded_context)
        return self.decision_package_builder.build(decision_state, loaded_context)
