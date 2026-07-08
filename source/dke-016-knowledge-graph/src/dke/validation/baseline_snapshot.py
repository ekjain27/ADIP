from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .validation_errors import SnapshotMismatchError


@dataclass(frozen=True)
class BaselineSnapshot:
    snapshot_id: str
    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "payload": _normalize_mapping(self.payload),
        }


def create_baseline_snapshot(snapshot_id: str, payload: Mapping[str, Any]) -> BaselineSnapshot:
    return BaselineSnapshot(snapshot_id=snapshot_id, payload=_normalize_mapping(payload))


def compare_snapshots(current: Mapping[str, Any], baseline: BaselineSnapshot) -> dict[str, Any]:
    current_normalized = _normalize_mapping(current)
    baseline_payload = baseline.to_dict()["payload"]
    if current_normalized != baseline_payload:
        raise SnapshotMismatchError(f"snapshot mismatch: {baseline.snapshot_id}")
    return {
        "status": "matched",
        "snapshot_id": baseline.snapshot_id,
    }


def _normalize_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return payload
    normalized = {}
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, Mapping):
            normalized[key] = _normalize_mapping(value)
        elif isinstance(value, list):
            normalized[key] = tuple(_normalize_mapping(item) if isinstance(item, Mapping) else item for item in value)
        else:
            normalized[key] = value
    return normalized
