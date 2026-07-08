import decision_orchestrator as do


def test_decision_state_creation():
    state = do.create_decision_state("choose supplier", {"region": "NA"})
    assert state.decision_id.startswith("decision-")
    assert state.query.text == "choose supplier"
    assert state.query.constraints["region"] == "NA"
    assert state.trace.events[0].name == "state_created"
