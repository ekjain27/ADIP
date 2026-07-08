from types import SimpleNamespace

import decision_orchestrator as do


def test_context_validation_requires_non_empty_context():
    report = do.validate_context(SimpleNamespace(facts=(), evidence=(), confidence=0.8))
    assert not report.valid
    assert any(issue.code == "empty_context" for issue in report.issues)


def test_reasoning_validation_requires_recommendation_or_limitation():
    report = do.validate_reasoning(do.ReasoningResult(confidence=0.7, evidence=("e1",)))
    assert not report.valid
    assert any(issue.code == "missing_recommendation_or_limitation" for issue in report.issues)


def test_reasoning_validation_flags_unsupported_conclusions():
    report = do.validate_reasoning(
        do.ReasoningResult(recommendation="Proceed", confidence=0.7, evidence=("e1",), unsupported_conclusions=("claim",))
    )
    assert report.valid
    assert any(issue.code == "unsupported_conclusions" for issue in report.issues)
