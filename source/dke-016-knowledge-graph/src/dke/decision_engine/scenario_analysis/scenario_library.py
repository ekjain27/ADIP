from __future__ import annotations

from .models import ScenarioDefinition


class ScenarioLibrary:
    def default_scenarios(self) -> tuple[ScenarioDefinition, ...]:
        return (
            ScenarioDefinition(
                "scenario-optimistic",
                "Optimistic",
                "Demand, resources, and execution conditions improve.",
                "upside",
                ("Resources remain available.", "Market response is favorable."),
                0.16,
                {"confidence_delta": 0.08, "risk_delta": -0.08, "score_delta": 0.08},
            ),
            ScenarioDefinition(
                "scenario-expected",
                "Expected",
                "Conditions follow the current expected path.",
                "baseline",
                ("Current evidence remains representative.",),
                0.28,
                {"confidence_delta": 0.0, "risk_delta": 0.0, "score_delta": 0.0},
            ),
            ScenarioDefinition(
                "scenario-pessimistic",
                "Pessimistic",
                "Execution conditions worsen and risks materialize.",
                "downside",
                ("Risk controls are tested.",),
                0.14,
                {"confidence_delta": -0.08, "risk_delta": 0.12, "score_delta": -0.12},
            ),
            ScenarioDefinition(
                "scenario-market-shift",
                "Market Shift",
                "External market conditions change after the decision.",
                "market",
                ("Customer or competitor behavior changes.",),
                0.12,
                {"confidence_delta": -0.03, "risk_delta": 0.06, "score_delta": -0.05},
            ),
            ScenarioDefinition(
                "scenario-resource-constraint",
                "Resource Constraint",
                "Budget, staffing, or time constraints tighten.",
                "resource",
                ("Available resources decrease.",),
                0.11,
                {"confidence_delta": -0.04, "risk_delta": 0.08, "score_delta": -0.09, "robustness_delta": -0.05},
            ),
            ScenarioDefinition(
                "scenario-policy-change",
                "Policy Change",
                "Policy or compliance requirements change.",
                "policy",
                ("Policy constraints become stricter.",),
                0.10,
                {"confidence_delta": -0.05, "risk_delta": 0.08, "score_delta": -0.08},
            ),
            ScenarioDefinition(
                "scenario-technical-failure",
                "Technical Failure",
                "A technical dependency fails or underperforms.",
                "technical",
                ("Technical fallback capacity is required.",),
                0.09,
                {"confidence_delta": -0.08, "risk_delta": 0.14, "score_delta": -0.12, "robustness_delta": -0.12},
            ),
        )
