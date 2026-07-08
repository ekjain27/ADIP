from __future__ import annotations

from decision_engine.adaptive import AdaptiveDecision

from .models import ExceptionPath


class ExceptionHandler:
    def build(self, decision: AdaptiveDecision) -> tuple[ExceptionPath, ...]:
        clean = decision.alternative_id.lower().replace(" ", "-").replace("_", "-")
        paths = [
            ExceptionPath(
                path_id=f"ex-{clean}-approval-failure",
                trigger="approval failure",
                recovery_action="retry approval after stakeholder review",
                severity="medium",
                metadata={"route": "alternative_path"},
            ),
            ExceptionPath(
                path_id=f"ex-{clean}-policy-violation",
                trigger="policy violation",
                recovery_action="route to governance review",
                severity="high",
                metadata={"route": "governance_gate"},
            ),
            ExceptionPath(
                path_id=f"ex-{clean}-execution-failure",
                trigger="execution failure",
                recovery_action="activate fallback workflow",
                severity="high",
                metadata={"route": "fallback_path"},
            ),
        ]
        if decision.behavior_profile.checkpoint_frequency == "high":
            paths.append(
                ExceptionPath(
                    path_id=f"ex-{clean}-adaptive-drift",
                    trigger="adaptive drift",
                    recovery_action="increase monitoring and reroute to validation",
                    severity="medium",
                    metadata={"route": "adaptive_path"},
                )
            )
        return tuple(paths)
