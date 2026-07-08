import decision_orchestrator as do


def test_workflow_order():
    workflow = do.DecisionWorkflow()
    assert workflow.names() == (
        "create_state",
        "retrieve_context",
        "validate_context",
        "reason",
        "validate_reasoning",
        "apply_fallback",
        "build_decision_package",
    )
