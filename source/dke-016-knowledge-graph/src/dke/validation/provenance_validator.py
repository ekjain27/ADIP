from __future__ import annotations

from typing import Any, Mapping

from .governance_errors import GovernancePolicyViolationError, LineageConsistencyError, ProvenanceIntegrityError
from .governance_policies import GovernanceValidationPolicy


class ProvenanceValidator:
    def validate_provenance(self, decision_payload: Mapping[str, Any], policy: GovernanceValidationPolicy) -> dict[str, Any]:
        self._require_payload(decision_payload)
        errors: list[str] = []
        if "provenance_required" in policy.required_rules and decision_payload.get("provenance") != "linked":
            errors.append("missing provenance link")
        if "trace_complete" in policy.required_rules and "decision" not in decision_payload:
            errors.append("missing decision trace")
        if errors:
            raise ProvenanceIntegrityError("; ".join(errors))
        return {
            "status": "valid",
            "validator": "DPG",
            "provenance": decision_payload.get("provenance"),
            "trace_complete": "decision" in decision_payload,
            "errors": (),
        }

    def validate_governance(self, decision_payload: Mapping[str, Any], policy: GovernanceValidationPolicy) -> dict[str, Any]:
        self._require_payload(decision_payload)
        if "governance_compliant" in policy.required_rules and decision_payload.get("governance") != "compliant":
            raise GovernancePolicyViolationError("governance policy violation: governance is not compliant")
        return {
            "status": "valid",
            "validator": "DDGM",
            "governance": decision_payload.get("governance"),
            "policy_id": policy.policy_id,
            "errors": (),
        }

    def validate_lineage(self, decision_payload: Mapping[str, Any], policy: GovernanceValidationPolicy) -> dict[str, Any]:
        self._require_payload(decision_payload)
        errors: list[str] = []
        if "lineage_required" in policy.required_rules and decision_payload.get("lineage") != "tracked":
            errors.append("broken lineage chain")
        if "workflow_continuity" in policy.required_rules:
            required = ("decision", "provenance", "governance", "lineage")
            missing = tuple(field for field in required if field not in decision_payload)
            if missing:
                errors.append(f"workflow continuity missing: {', '.join(missing)}")
        if errors:
            raise LineageConsistencyError("; ".join(errors))
        return {
            "status": "valid",
            "validator": "TDLL",
            "lineage": decision_payload.get("lineage"),
            "workflow_continuity": True,
            "errors": (),
        }

    def validate_audit(self, decision_payload: Mapping[str, Any], policy: GovernanceValidationPolicy) -> dict[str, Any]:
        self._require_payload(decision_payload)
        if "audit_complete" not in policy.required_rules:
            return {"status": "valid", "validator": "audit", "audit_complete": True, "errors": ()}
        required = ("decision", "provenance", "governance", "lineage", "recommendation")
        missing = tuple(field for field in required if field not in decision_payload)
        if missing:
            raise ProvenanceIntegrityError(f"audit trail incomplete: {', '.join(missing)}")
        return {"status": "valid", "validator": "audit", "audit_complete": True, "errors": ()}

    def _require_payload(self, decision_payload: Mapping[str, Any]) -> None:
        if not isinstance(decision_payload, Mapping) or not decision_payload:
            raise ProvenanceIntegrityError("decision payload must be a non-empty mapping")
