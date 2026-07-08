from __future__ import annotations

from .models import DecisionQuery, DecisionState, DecisionTrace, new_decision_id


def create_decision_state(query: str | DecisionQuery, constraints: dict | None = None) -> DecisionState:
    decision_query = query if isinstance(query, DecisionQuery) else DecisionQuery(text=query, constraints=constraints or {})
    decision_id = new_decision_id()
    return DecisionState(decision_id=decision_id, query=decision_query, trace=DecisionTrace(decision_id=decision_id).add("state_created"))
