from __future__ import annotations

from copy import deepcopy
from typing import Protocol

from .persistence_errors import (
    DuplicatePersistenceRecordError,
    ImmutablePersistenceRecordError,
    PersistenceRecordError,
    PersistenceTransactionError,
    UnsupportedPersistenceBackendError,
)
from .persistence_models import PersistenceRecord, serialize_record


class PersistenceBackend(Protocol):
    backend_type: str

    def save_record(self, record: PersistenceRecord) -> PersistenceRecord:
        ...

    def load_record(self, record_id: str) -> PersistenceRecord:
        ...

    def delete_record(self, record_id: str) -> PersistenceRecord:
        ...

    def list_records(self) -> tuple[PersistenceRecord, ...]:
        ...

    def begin_transaction(self) -> None:
        ...

    def commit_transaction(self) -> None:
        ...

    def rollback_transaction(self) -> None:
        ...

    def export_snapshot(self) -> dict:
        ...


class InMemoryPersistenceBackend:
    backend_type = "memory"

    def __init__(self) -> None:
        self._records: dict[str, PersistenceRecord] = {}
        self._transaction_records: dict[str, PersistenceRecord] | None = None

    def save_record(self, record: PersistenceRecord) -> PersistenceRecord:
        if not isinstance(record, PersistenceRecord):
            raise PersistenceRecordError("record must be a PersistenceRecord")
        records = self._active_records()
        if record.record_id in records:
            raise DuplicatePersistenceRecordError(f"record already exists: {record.record_id}")
        records[record.record_id] = record
        return record

    def load_record(self, record_id: str) -> PersistenceRecord:
        normalized = self._normalize_record_id(record_id)
        records = self._active_records()
        try:
            return records[normalized]
        except KeyError as exc:
            raise PersistenceRecordError(f"record is not persisted: {normalized}") from exc

    def delete_record(self, record_id: str) -> PersistenceRecord:
        normalized = self._normalize_record_id(record_id)
        records = self._active_records()
        record = self.load_record(normalized)
        if record.immutable:
            raise ImmutablePersistenceRecordError(f"record is immutable: {normalized}")
        del records[normalized]
        return record

    def list_records(self) -> tuple[PersistenceRecord, ...]:
        records = self._active_records()
        return tuple(records[record_id] for record_id in sorted(records))

    def begin_transaction(self) -> None:
        if self._transaction_records is not None:
            raise PersistenceTransactionError("transaction already active")
        self._transaction_records = deepcopy(self._records)

    def commit_transaction(self) -> None:
        if self._transaction_records is None:
            raise PersistenceTransactionError("cannot commit without an active transaction")
        self._records = self._transaction_records
        self._transaction_records = None

    def rollback_transaction(self) -> None:
        if self._transaction_records is None:
            raise PersistenceTransactionError("cannot rollback without an active transaction")
        self._transaction_records = None

    def export_snapshot(self) -> dict:
        return {
            "backend_type": self.backend_type,
            "transaction_active": self._transaction_records is not None,
            "record_count": len(self._active_records()),
            "records": tuple(record.to_dict() for record in self.list_records()),
            "serialized_records": tuple(serialize_record(record) for record in self.list_records()),
        }

    def _active_records(self) -> dict[str, PersistenceRecord]:
        return self._transaction_records if self._transaction_records is not None else self._records

    def _normalize_record_id(self, record_id: str) -> str:
        if not isinstance(record_id, str) or not record_id.strip():
            raise PersistenceRecordError("record_id is required")
        return record_id.strip()


class FilePersistenceBackend:
    backend_type = "file"

    def __init__(self, location: str = "") -> None:
        self.location = location

    def save_record(self, record: PersistenceRecord) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def load_record(self, record_id: str) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def delete_record(self, record_id: str) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def list_records(self) -> tuple[PersistenceRecord, ...]:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def begin_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def commit_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def rollback_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("file persistence backend is an interface stub")

    def export_snapshot(self) -> dict:
        return {"backend_type": self.backend_type, "location": self.location, "status": "stub"}


class DatabasePersistenceBackend:
    backend_type = "database"

    def __init__(self, connection_name: str = "") -> None:
        self.connection_name = connection_name

    def save_record(self, record: PersistenceRecord) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def load_record(self, record_id: str) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def delete_record(self, record_id: str) -> PersistenceRecord:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def list_records(self) -> tuple[PersistenceRecord, ...]:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def begin_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def commit_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def rollback_transaction(self) -> None:
        raise UnsupportedPersistenceBackendError("database persistence backend is an interface stub")

    def export_snapshot(self) -> dict:
        return {"backend_type": self.backend_type, "connection_name": self.connection_name, "status": "stub"}
