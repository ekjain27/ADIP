import decision_orchestrator as do
import decision_orchestrator.interfaces as interfaces


def test_interfaces_and_public_apis_are_exported():
    assert hasattr(interfaces, "RetrievalPort")
    assert hasattr(interfaces, "ReasoningPort")
    expected = {
        "start_decision",
        "run_pipeline",
        "validate_context",
        "validate_reasoning",
        "build_decision_package",
        "get_trace",
    }
    assert expected.issubset(set(do.__all__))
