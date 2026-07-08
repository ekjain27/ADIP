import evidence_audit as ea
import evidence_audit.interfaces as interfaces


def test_package_imports_and_public_apis():
    assert hasattr(interfaces, "AuditStorage")
    expected = {
        "record_event",
        "record_decision",
        "build_trace",
        "link_evidence",
        "validate_evidence",
        "generate_audit_report",
        "get_audit_trail",
        "export_trace",
    }
    assert expected.issubset(set(ea.__all__))
