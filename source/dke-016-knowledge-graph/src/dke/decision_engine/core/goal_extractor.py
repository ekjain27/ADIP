from __future__ import annotations

from typing import Any

from .models import Goal


class GoalExtractor:
    def extract(self, loaded_context: dict[str, Any]) -> tuple[Goal, ...]:
        goals: list[Goal] = []
        metadata = self._as_mapping(loaded_context.get("metadata", {}))
        query_text = self._query_text(loaded_context.get("query"))

        for item in self._as_sequence(metadata.get("goals")):
            goals.append(self._goal_from(item, "secondary"))
        for item in self._as_sequence(metadata.get("objectives")):
            goals.append(self._goal_from(item, "secondary"))

        context_goals = metadata.get("context", {}).get("goals") if isinstance(metadata.get("context"), dict) else ()
        for item in self._as_sequence(context_goals):
            goals.append(self._goal_from(item, "secondary"))

        primary_objective = metadata.get("primary_goal") or metadata.get("objective") or query_text
        if not primary_objective:
            primary_objective = "Produce a decision package from the available context"
        goals.insert(0, self._goal_from(primary_objective, "primary"))

        return self._deduplicate(goals)

    def _goal_from(self, item: Any, default_priority: str) -> Goal:
        data = self._as_mapping(item)
        if data:
            objective = str(data.get("objective") or data.get("goal") or data.get("text") or item)
            priority = str(data.get("priority") or default_priority)
            measurable = bool(data.get("measurable", self._looks_measurable(objective)))
            dependencies = self._as_string_tuple(data.get("dependencies", ()))
            metadata = dict(data.get("metadata") or {})
        else:
            objective = str(item).strip()
            priority = default_priority
            measurable = self._looks_measurable(objective)
            dependencies = ()
            metadata = {}
        return Goal(
            objective=objective or "Produce a decision package from the available context",
            priority=priority,
            measurable=measurable,
            dependencies=dependencies,
            metadata=metadata,
        )

    def _query_text(self, query: Any) -> str:
        if isinstance(query, str):
            return query.strip()
        data = self._as_mapping(query)
        return str(data.get("text") or data.get("query") or data.get("objective") or "").strip()

    def _looks_measurable(self, text: str) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in ("measure", "metric", "kpi", "within", "under", "by ", "%", "$"))

    def _deduplicate(self, goals: list[Goal]) -> tuple[Goal, ...]:
        seen: set[str] = set()
        unique: list[Goal] = []
        for goal in goals:
            key = goal.objective.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(goal)
        return tuple(unique)

    def _as_mapping(self, item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            return dict(item)
        if hasattr(item, "__dict__"):
            return dict(vars(item))
        return {}

    def _as_sequence(self, item: Any) -> tuple[Any, ...]:
        if item is None:
            return ()
        if isinstance(item, (str, bytes, dict)):
            return (item,)
        try:
            return tuple(item)
        except TypeError:
            return (item,)

    def _as_string_tuple(self, item: Any) -> tuple[str, ...]:
        return tuple(str(value) for value in self._as_sequence(item) if str(value))
