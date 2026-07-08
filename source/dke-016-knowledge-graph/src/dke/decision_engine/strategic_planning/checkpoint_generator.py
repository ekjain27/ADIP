from __future__ import annotations

from .models import Checkpoint


class CheckpointGenerator:
    DEFAULT_CHECKPOINTS = (
        ("budget-exceeded", "Budget exceeded", "budget variance exceeds approved tolerance", "Review strategy and reprioritize scope.", "high"),
        ("confidence-decreases", "Confidence decreases", "decision confidence decreases materially", "Re-evaluate plan assumptions and evidence.", "high"),
        ("milestone-delayed", "Milestone delayed", "milestone misses target completion window", "Reschedule execution and rebalance dependencies.", "medium"),
        ("risk-increases", "Risk increases", "risk indicators increase during execution", "Escalate mitigation and review checkpoints.", "high"),
    )

    def generate(self, alternative_id: str) -> tuple[Checkpoint, ...]:
        clean_id = alternative_id.lower().replace(" ", "-").replace("_", "-")
        return tuple(
            Checkpoint(
                checkpoint_id=f"cp-{clean_id}-{key}",
                title=title,
                condition=condition,
                action=action,
                priority=priority,
                metadata={"adaptive": True},
            )
            for key, title, condition, action, priority in self.DEFAULT_CHECKPOINTS
        )
