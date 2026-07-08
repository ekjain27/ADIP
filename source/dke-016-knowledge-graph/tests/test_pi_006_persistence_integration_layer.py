import pytest

from platform_integration import (
    DuplicatePersistenceRecordError,
    ImmutablePersistenceRecordError,
    PersistenceBackendRegistrationError,
    PersistenceIntegrationLayer,
    PersistenceRecord,
    PersistenceRecordError,
    PersistenceTransactionError,
    PlatformContract,
    PlatformIntegrationLayer,
    RuntimeComponentMetadata,
    UnifiedPlatformRuntimeRegistry,
    UnsupportedPersistenceBackendError,
    create_config,
    create_database_persistence_backend,
    create_file_persistence_backend,
    deserialize_record,
    freeze_config,
    serialize_record,
)


class EchoComponent:
    def execute(self, payload):
        return payload


class InvalidBackend:
    backend_type = "unsupported"


def test_backend_registration():
    layer = PersistenceIntegrationLayer()
    file_backend = create_file_persistence_backend("unused")
    result = layer.register_backend("file", file_backend)
    assert result == file_backend
    assert tuple(layer.backends()) == ("file", "memory")


def test_duplicate_backend_rejected():
    layer = PersistenceIntegrationLayer()
    with pytest.raises(PersistenceBackendRegistrationError, match="already registered"):
        layer.register_backend("memory", create_file_persistence_backend())


def test_crud_operations():
    layer = PersistenceIntegrationLayer()
    record = _record("r1", {"value": 1})
    layer.save_record(record)
    assert layer.load_record("r1") == record
    assert layer.list_records() == (record,)
    assert layer.delete_record("r1") == record
    assert layer.list_records() == ()


def test_duplicate_record_id_rejected():
    layer = PersistenceIntegrationLayer()
    layer.save_record(_record("r1", {"value": 1}))
    with pytest.raises(DuplicatePersistenceRecordError, match="already exists"):
        layer.save_record(_record("r1", {"value": 2}))


def test_transaction_lifecycle_commit():
    layer = PersistenceIntegrationLayer()
    layer.begin_transaction()
    layer.save_record(_record("r1", {"value": 1}))
    assert len(layer.list_records()) == 1
    layer.commit_transaction()
    assert layer.load_record("r1").payload == {"value": 1}


def test_transaction_rollback_correctness():
    layer = PersistenceIntegrationLayer()
    layer.save_record(_record("persisted", {"value": 1}))
    layer.begin_transaction()
    layer.save_record(_record("transient", {"value": 2}))
    layer.delete_record("persisted")
    assert tuple(record.record_id for record in layer.list_records()) == ("transient",)
    layer.rollback_transaction()
    assert tuple(record.record_id for record in layer.list_records()) == ("persisted",)


def test_transaction_misuse_rejected():
    layer = PersistenceIntegrationLayer()
    with pytest.raises(PersistenceTransactionError, match="commit without"):
        layer.commit_transaction()
    with pytest.raises(PersistenceTransactionError, match="rollback without"):
        layer.rollback_transaction()
    layer.begin_transaction()
    with pytest.raises(PersistenceTransactionError, match="already active"):
        layer.begin_transaction()


def test_deterministic_serialization():
    record = _record("r1", {"z": 2, "a": 1})
    first = serialize_record(record)
    second = serialize_record(record)
    assert first == second
    assert deserialize_record(first) == record


def test_schema_validation_rejected():
    with pytest.raises(PersistenceRecordError, match="record_id is required"):
        PersistenceRecord("", "config", 1, {})
    with pytest.raises(PersistenceRecordError, match="positive integer"):
        PersistenceRecord("r1", "config", 0, {})
    with pytest.raises(PersistenceRecordError, match="payload must be a mapping"):
        PersistenceRecord("r1", "config", 1, [])


def test_unsupported_backend_rejected():
    layer = PersistenceIntegrationLayer()
    with pytest.raises(UnsupportedPersistenceBackendError, match="unsupported"):
        layer.register_backend("bad", InvalidBackend())
    with pytest.raises(UnsupportedPersistenceBackendError, match="interface stub"):
        create_file_persistence_backend().save_record(_record("r1", {}))
    with pytest.raises(UnsupportedPersistenceBackendError, match="interface stub"):
        create_database_persistence_backend().save_record(_record("r1", {}))


def test_immutable_snapshot_protection():
    layer = PersistenceIntegrationLayer()
    record = _record("immutable", {"value": 1}, immutable=True)
    layer.save_record(record)
    with pytest.raises(ImmutablePersistenceRecordError, match="immutable"):
        layer.delete_record("immutable")


def test_snapshot_export_is_deterministic():
    layer = PersistenceIntegrationLayer()
    layer.save_record(_record("r1", {"value": 1}))
    first = layer.export_persistence_snapshot()
    second = layer.export_persistence_snapshot()
    assert first == second
    assert first["module"] == "PI-006"
    assert first["record_count"] == 1


def test_integration_with_pi_001_platform_layer():
    persistence = PersistenceIntegrationLayer()
    platform = PlatformIntegrationLayer()
    platform.register_component("DKE", EchoComponent(), PlatformContract("DKE", "knowledge_extraction", "execute"))
    record = persistence.persist_platform_layer(platform)
    assert record.record_type == "platform_integration_layer"
    assert persistence.load_record("pi-001-platform-layer").payload == {"components": ("DKE",)}


def test_integration_with_pi_002_runtime_registry():
    persistence = PersistenceIntegrationLayer()
    registry = UnifiedPlatformRuntimeRegistry()
    registry.register_runtime_component(
        RuntimeComponentMetadata("PI-006", "Persistence Integration Layer", "platform_integration", capabilities=("persistence",))
    )
    record = persistence.persist_runtime_registry(registry)
    assert record.record_type == "runtime_registry"
    assert persistence.load_record("pi-002-runtime-registry").metadata == {"module": "PI-002"}


def test_integration_with_pi_005_config_layer():
    persistence = PersistenceIntegrationLayer()
    config = freeze_config(create_config("test"))
    record = persistence.persist_config(config)
    assert record.immutable is True
    assert record.metadata == {"module": "PI-005", "profile": "test"}
    with pytest.raises(ImmutablePersistenceRecordError, match="immutable"):
        persistence.delete_record("pi-005-config")


def _record(record_id, payload, immutable=False):
    return PersistenceRecord(
        record_id=record_id,
        record_type="test_record",
        version=1,
        payload=payload,
        immutable=immutable,
    )
