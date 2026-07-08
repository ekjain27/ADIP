from __future__ import annotations

from typing import Any

from .models import Constraint


class ConstraintEngine:
    KEYWORDS = {
        "budget": ("budget", "cost", "price", "spend"),
        "time": ("time", "deadline", "schedule", "duration", "within"),
        "risk": ("risk", "uncertain", "exposure", "failure"),
        "legal": ("legal", "law", "regulation", "compliance"),
        "policy": ("policy", "standard", "procedure", "rule"),
        "technical": ("technical", "architecture", "integration", "latency", "scalability"),
        "business": ("business", "revenue", "customer", "market", "strategy"),
        "user_preference": ("preference", "prefer", "must have", "nice to have"),
    }

    def extract(self, loaded_context: dict[str, Any]) -> tuple[Constraint, ...]:
        constraints: list[Constraint] = []
        metadata = self._as_mapping(loaded_context.get("metadata", {}))
        text = " ".join(
            str(part)
            for part in (
                self._query_text(loaded_context.get("query")),
                metadata.get("context", ""),
                metadata.get("notes", ""),
                metadata.get("description", ""),
            )
            if part
        )
        constraints.extend(self._detect_keywords(text, "query"))

        for item in self._as_sequence(metadata.get("constraints")):
            constraints.append(self._constraint_from(item, "metadata"))
        for item in self._as_sequence(metadata.get("requirements")):
            constraints.extend(self._detect_keywords(str(item), "metadata"))

        return self._deduplicate(constraints)

    def _detect_keywords(self, text: str, source: str) -> list[Constraint]:
        lowered = text.lower()
        constraints = []
        for constraint_type, keywords in self.KEYWORDS.items():
            matches = tuple(keyword for keyword in keywords if keyword in lowered)
            if matches:
                constraints.append(
                    Constraint(
                        type=constraint_type,
                        severity="medium",
                        source=source,
                        parameters={"keywords": matches},
                        metadata={"matched_text": text[:500]},
                    )
                )
        return constraints

    def _constraint_from(self, item: Any, source: str) -> Constraint:
        data = self._as_mapping(item)
        if data:
            return Constraint(
                type=str(data.get("type") or data.get("name") or "general"),
                severity=str(data.get("severity") or "medium"),
                source=str(data.get("source") or source),
                parameters=dict(data.get("parameters") or {}),
                metadata=dict(data.get("metadata") or {}),
            )
        detected = self._detect_keywords(str(item), source)
        if detected:
            return detected[0]
        return Constraint(type="general", severity="medium", source=source, parameters={"text": str(item)})

    def _deduplicate(self, constraints: list[Constraint]) -> tuple[Constraint, ...]:
        seen: set[tuple[str, str]] = set()
        unique: list[Constraint] = []
        for constraint in constraints:
            key = (constraint.type, constraint.source)
            if key in seen:
                continue
            seen.add(key)
            unique.append(constraint)
        return tuple(unique)

    def _query_text(self, query: Any) -> str:
        if isinstance(query, str):
            return query
        data = self._as_mapping(query)
        return str(data.get("text") or data.get("query") or data.get("objective") or "")

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
