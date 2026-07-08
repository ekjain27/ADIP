from __future__ import annotations

from typing import Any


def generate_developer_checklist() -> dict[str, Any]:
    items = (
        ("read_architecture_overview", "Review DOC-001 architecture summary"),
        ("inspect_module_registry", "Review DOC-002 module registry by phase"),
        ("study_api_reference", "Review DOC-003 API and integration documentation"),
        ("run_regression_suite", "Run python -m pytest -q"),
        ("validate_runtime_registry", "Inspect PI-002 runtime registry snapshot"),
        ("configure_test_profile", "Use deterministic test configuration profile"),
        ("extend_via_platform_boundary", "Register extensions through platform integration APIs"),
        ("update_documentation_tests", "Add documentation tests for new public APIs"),
    )
    return {
        "checklist_type": "developer_onboarding",
        "item_count": len(items),
        "items": tuple(
            {"id": item_id, "description": description, "required": True}
            for item_id, description in items
        ),
    }
