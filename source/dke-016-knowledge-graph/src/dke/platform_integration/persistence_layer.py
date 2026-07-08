from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .config_layer import PlatformConfig, export_config_snapshot
from .persistence_backends import DatabasePersistenceBackend, FilePersistenceBackend, InMemoryPersistenceBackend, PersistenceBackend
from .persistence_errors import (
    PersistenceBackendNotFoundError,
    PersistenceBackendRegistrationError,
    UnsupportedPersistenceBackendError,
)
from .persistence_models import PersistenceRecord
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry


SUPPORTED_BACKEND_TYPES: tuple[str, ...] = ("memory", "file", "database")


class PersistenceIntegrationLayer:
    MODULE = "PI-006"

    def __init__(self, default_backend: str = "memory") -> None:
        self._backends: dict[str, PersistenceBackend] = {}
        self._default_backend = default_backend
        self.register_backend("memory", InMemoryPersistenceBackend())

    def register_backend(self, name: str, backend: PersistenceBackend) -> PersistenceBackend:
        normalized = self._normalize_backend_name(name)
        if normalized in self._backends:
            raise PersistenceBackendRegistrationError(f"persistence backend already registered: {normalized}")
        backend_type = getattr(backend, "backend_type", None)
        if backend_type not in SUPPORTED_BACKEND_TYPES:
            raise UnsupportedPersistenceBackendError(f"unsupported persistence backend type: {backend_type}")
        required = (
            "save_record",
            "load_record",
            "delete_record",
            "list_records",
            "begin_transaction",
            "commit_transaction",
            "rollback_transaction",
            "export_snapshot",
        )
        missing = tuple(method for method in required if not callable(getattr(backend, method, None)))
        if missing:
            raise PersistenceBackendRegistrationError(f"backend missing method(s): {', '.join(missing)}")
        self._backends[normalized] = backend
        return backend

    def get_backend(self, name: str) -> PersistenceBackend:
        normalized = self._normalize_backend_name(name)
        try:
            return self._backends[normalized]
        except KeyError as exc:
            raise PersistenceBackendNotFoundError(f"persistence backend is not registered: {normalized}") from exc

    def save_record(self, record: PersistenceRecord) -> PersistenceRecord:
        return self._backend().save_record(record)

    def load_record(self, record_id: str) -> PersistenceRecord:
        return self._backend().load_record(record_id)

    def delete_record(self, record_id: str) -> PersistenceRecord:
        return self._backend().delete_record(record_id)

    def list_records(self) -> tuple[PersistenceRecord, ...]:
        return self._backend().list_records()

    def begin_transaction(self) -> None:
        self._backend().begin_transaction()

    def commit_transaction(self) -> None:
        self._backend().commit_transaction()

    def rollback_transaction(self) -> None:
        self._backend().rollback_transaction()

    def export_persistence_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "default_backend": self._default_backend,
            "backends": tuple(
                {
                    "name": name,
                    "backend_type": getattr(self._backends[name], "backend_type", ""),
                    "snapshot": self._backends[name].export_snapshot(),
                }
                for name in sorted(self._backends)
            ),
            "record_count": len(self.list_records()),
        }

    def persist_platform_layer(self, platform_layer: PlatformIntegrationLayer, record_id: str = "pi-001-platform-layer") -> PersistenceRecord:
        record = PersistenceRecord(
            record_id=record_id,
            record_type="platform_integration_layer",
            version=1,
            payload={"components": platform_layer.list_components()},
            metadata={"module": "PI-001"},
        )
        return self.save_record(record)

    def persist_runtime_registry(
        self,
        runtime_registry: UnifiedPlatformRuntimeRegistry,
        record_id: str = "pi-002-runtime-registry",
    ) -> PersistenceRecord:
        record = PersistenceRecord(
            record_id=record_id,
            record_type="runtime_registry",
            version=1,
            payload=runtime_registry.export_registry_snapshot(),
            metadata={"module": "PI-002"},
        )
        return self.save_record(record)

    def persist_config(self, config: PlatformConfig, record_id: str = "pi-005-config") -> PersistenceRecord:
        record = PersistenceRecord(
            record_id=record_id,
            record_type="platform_config",
            version=1,
            payload=export_config_snapshot(config),
            metadata={"module": "PI-005", "profile": config.profile},
            immutable=config.frozen,
        )
        return self.save_record(record)

    def backends(self) -> Mapping[str, PersistenceBackend]:
        return MappingProxyType(dict(sorted(self._backends.items())))

    def _backend(self) -> PersistenceBackend:
        return self.get_backend(self._default_backend)

    def _normalize_backend_name(self, name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise PersistenceBackendRegistrationError("persistence backend name is required")
        return name.strip()


def create_persistence_layer() -> PersistenceIntegrationLayer:
    return PersistenceIntegrationLayer()


def create_file_persistence_backend(location: str = "") -> FilePersistenceBackend:
    return FilePersistenceBackend(location=location)


def create_database_persistence_backend(connection_name: str = "") -> DatabasePersistenceBackend:
    return DatabasePersistenceBackend(connection_name=connection_name)
