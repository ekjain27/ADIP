from __future__ import annotations

from typing import Any

from .models import clamp_confidence


class ContextLoader:
    def load(self, context_package: Any) -> dict[str, Any]:
        package = self._as_mapping(context_package)
        metadata = self._as_mapping(self._get(package, "metadata", default={}))

        semantic_results = self._first_present(
            package,
            ("semantic_results", "semantic", "semantic_chunks", "chunks", "results"),
            default=(),
        )
        graph_results = self._first_present(
            package,
            ("graph_results", "graph", "facts", "nodes", "relationships"),
            default=(),
        )
        evidence = self._first_present(package, ("evidence", "evidence_set"), default=())
        query = self._first_present(package, ("query", "question", "objective"), default="")
        confidence_values = self._extract_confidence_values(package, metadata)

        return {
            "query": query,
            "semantic_results": self._as_sequence(semantic_results),
            "graph_results": self._as_sequence(graph_results),
            "evidence": self._as_sequence(evidence),
            "metadata": metadata,
            "confidence_values": confidence_values,
            "context_confidence": self._context_confidence(confidence_values),
            "raw_context": context_package,
        }

    def _extract_confidence_values(self, package: Any, metadata: dict[str, Any]) -> dict[str, float]:
        values: dict[str, float] = {}
        for key in ("confidence", "semantic_confidence", "graph_confidence", "retrieval_confidence"):
            value = self._get(package, key)
            if value is not None:
                values[key] = clamp_confidence(value)
        nested = self._get(package, "confidence_values", default={})
        for key, value in self._as_mapping(nested).items():
            values[str(key)] = clamp_confidence(value)
        for key in ("confidence", "semantic_confidence", "graph_confidence"):
            if key in metadata:
                values[f"metadata_{key}"] = clamp_confidence(metadata[key])
        return values

    def _context_confidence(self, confidence_values: dict[str, float]) -> float:
        if not confidence_values:
            return 0.0
        return clamp_confidence(sum(confidence_values.values()) / len(confidence_values))

    def _first_present(self, item: Any, keys: tuple[str, ...], default: Any = None) -> Any:
        for key in keys:
            value = self._get(item, key)
            if value is not None:
                return value
        return default

    def _get(self, item: Any, key: str, default: Any = None) -> Any:
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def _as_mapping(self, item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if isinstance(item, dict):
            return dict(item)
        if hasattr(item, "_asdict"):
            return dict(item._asdict())
        if hasattr(item, "__dict__"):
            return dict(vars(item))
        return {}

    def _as_sequence(self, item: Any) -> tuple[Any, ...]:
        if item is None:
            return ()
        if isinstance(item, (str, bytes)):
            return (item,)
        if isinstance(item, dict):
            return (item,)
        try:
            return tuple(item)
        except TypeError:
            return (item,)
