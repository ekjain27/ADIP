from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any

from .models import Evidence, clamp_confidence, utc_now


class EvidenceNormalizer:
    def normalize(self, loaded_context: dict[str, Any]) -> tuple[Evidence, ...]:
        candidates: list[Evidence] = []
        for item in loaded_context.get("semantic_results", ()):
            candidates.append(self._from_item(item, default_source="semantic"))
        for item in loaded_context.get("graph_results", ()):
            candidates.append(self._from_item(item, default_source="graph"))
        for item in loaded_context.get("evidence", ()):
            candidates.append(self._from_item(item, default_source="context"))
        for item in self._metadata_facts(loaded_context.get("metadata", {})):
            candidates.append(self._from_item(item, default_source="metadata"))
        return self._deduplicate(candidates)

    def _metadata_facts(self, metadata: Any) -> tuple[Any, ...]:
        data = self._as_mapping(metadata)
        facts = []
        for key in ("facts", "metadata_facts", "evidence", "context_facts"):
            facts.extend(self._as_sequence(data.get(key)))
        return tuple(facts)

    def _from_item(self, item: Any, default_source: str) -> Evidence:
        data = self._as_mapping(item)
        text = self._text_for(item, data)
        source = str(data.get("source") or data.get("origin") or default_source)
        evidence_id = str(data.get("id") or data.get("evidence_id") or self._stable_id(text, source))
        confidence = data.get("confidence", data.get("score", 0.5 if text else 0.0))
        score = data.get("score", confidence)
        relationships = self._as_sequence(data.get("relationships", data.get("edges", ())))
        timestamp = self._timestamp_for(data.get("timestamp", data.get("created_at")))
        domain = str(data.get("domain") or data.get("type") or "general")
        metadata = dict(data.get("metadata") or {})
        if not metadata and data:
            metadata = {k: v for k, v in data.items() if k not in {"id", "evidence_id", "source", "origin", "text"}}
        return Evidence(
            id=evidence_id,
            source=source,
            text=text,
            confidence=clamp_confidence(confidence, default=0.5 if text else 0.0),
            score=clamp_confidence(score, default=0.5 if text else 0.0),
            timestamp=timestamp,
            domain=domain,
            relationships=relationships,
            metadata=metadata,
        )

    def _text_for(self, item: Any, data: dict[str, Any]) -> str:
        for key in ("text", "excerpt", "content", "summary", "fact", "name", "description"):
            value = data.get(key)
            if value is not None:
                return str(value)
        if isinstance(item, str):
            return item
        if data:
            return str(data)
        return ""

    def _stable_id(self, text: str, source: str) -> str:
        digest = sha256(f"{source}|{text}".encode("utf-8")).hexdigest()[:16]
        return f"ev-{digest}"

    def _timestamp_for(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return utc_now()
        return utc_now()

    def _deduplicate(self, evidence: list[Evidence]) -> tuple[Evidence, ...]:
        seen: set[tuple[str, str]] = set()
        unique: list[Evidence] = []
        for item in evidence:
            key = (item.text.strip().lower(), item.source.strip().lower())
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return tuple(unique)

    def _as_mapping(self, item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if isinstance(item, dict):
            return dict(item)
        if is_dataclass(item):
            return asdict(item)
        if hasattr(item, "__dict__"):
            return dict(vars(item))
        return {}

    def _as_sequence(self, item: Any) -> tuple[Any, ...]:
        if item is None:
            return ()
        if isinstance(item, (str, bytes)):
            return (item,)
        try:
            return tuple(item)
        except TypeError:
            return (item,)
