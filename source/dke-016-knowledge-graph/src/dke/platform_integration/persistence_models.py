from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .persistence_errors import PersistenceRecordError


DETERMINISTIC_PERSISTENCE_TIMESTAMP = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class PersistenceRecord:
    record_id: str
    record_type: str
    version: int
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    immutable: bool = False
    created_at: str = DETERMINISTIC_PERSISTENCE_TIMESTAMP
    updated_at: str = DETERMINISTIC_PERSISTENCE_TIMESTAMP

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise PersistenceRecordError("record_id is required")
        if not isinstance(self.record_type, str) or not self.record_type.strip():
            raise PersistenceRecordError("record_type is required")
        if not isinstance(self.version, int) or self.version < 1:
            raise PersistenceRecordError("record version must be a positive integer")
        if not isinstance(self.payload, Mapping):
            raise PersistenceRecordError("record payload must be a mapping")
        if not isinstance(self.metadata, Mapping):
            raise PersistenceRecordError("record metadata must be a mapping")
        object.__setattr__(self, "record_id", self.record_id.strip())
        object.__setattr__(self, "record_type", self.record_type.strip())
        object.__setattr__(self, "payload", _deterministic_mapping(self.payload))
        object.__setattr__(self, "metadata", _deterministic_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "version": self.version,
            "payload": dict(self.payload),
            "metadata": dict(self.metadata),
            "immutable": self.immutable,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> "PersistenceRecord":
        if not isinstance(values, Mapping):
            raise PersistenceRecordError("serialized record must be a mapping")
        required = ("record_id", "record_type", "version", "payload")
        missing = tuple(key for key in required if key not in values)
        if missing:
            raise PersistenceRecordError(f"serialized record missing required field(s): {', '.join(missing)}")
        return cls(
            record_id=values["record_id"],
            record_type=values["record_type"],
            version=values["version"],
            payload=values["payload"],
            metadata=values.get("metadata", {}),
            immutable=values.get("immutable", False),
            created_at=values.get("created_at", DETERMINISTIC_PERSISTENCE_TIMESTAMP),
            updated_at=values.get("updated_at", DETERMINISTIC_PERSISTENCE_TIMESTAMP),
        )


def serialize_record(record: PersistenceRecord) -> str:
    if not isinstance(record, PersistenceRecord):
        raise PersistenceRecordError("record must be a PersistenceRecord")
    return json.dumps(record.to_dict(), sort_keys=True, separators=(",", ":"))


def deserialize_record(serialized: str) -> PersistenceRecord:
    if not isinstance(serialized, str) or not serialized:
        raise PersistenceRecordError("serialized record must be a non-empty string")
    try:
        values = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise PersistenceRecordError("serialized record is not valid JSON") from exc
    return PersistenceRecord.from_dict(values)


def _deterministic_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: values[key] for key in sorted(values)}
