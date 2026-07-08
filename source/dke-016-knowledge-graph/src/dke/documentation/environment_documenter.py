from __future__ import annotations

from typing import Any

from platform_integration import DeploymentReadinessLayer, VALID_CONFIG_PROFILES, create_config, export_config_snapshot

from .operations_errors import MalformedEnvironmentDefinitionError, UnsupportedDeploymentEnvironmentError

SUPPORTED_DEPLOYMENT_ENVIRONMENTS = VALID_CONFIG_PROFILES


class EnvironmentDocumenter:
    def generate_environment_documentation(self, environment: str | None = None) -> dict[str, Any]:
        environments = (self._normalize_environment(environment),) if environment is not None else SUPPORTED_DEPLOYMENT_ENVIRONMENTS
        definitions = tuple(self._environment_definition(item) for item in environments)
        return {
            "documentation_type": "environment_documentation",
            "status": "generated",
            "environments": definitions,
        }

    def generate_environment_readiness_report(self, deployment_readiness) -> dict[str, Any]:
        reports = []
        for environment in SUPPORTED_DEPLOYMENT_ENVIRONMENTS:
            profile_readiness = DeploymentReadinessLayer(
                platform_layer=deployment_readiness.platform_layer,
                runtime_registry=deployment_readiness.runtime_registry,
                api_gateway=deployment_readiness.api_gateway,
                config=create_config(environment),
                persistence_layer=deployment_readiness.persistence_layer,
                observability_layer=deployment_readiness.observability_layer,
                validator=deployment_readiness.validator,
            )
            readiness = profile_readiness.generate_readiness_report(environment)
            reports.append(
                {
                    "environment": environment,
                    "status": readiness["status"],
                    "checks": readiness["checks"],
                    "configuration_profile": readiness["profile"],
                }
            )
        return {
            "report_type": "environment_readiness",
            "status": "ready",
            "environment_count": len(reports),
            "reports": tuple(reports),
        }

    def _environment_definition(self, environment: str) -> dict[str, Any]:
        config = create_config(environment)
        snapshot = export_config_snapshot(config)
        if snapshot["profile"] != environment:
            raise MalformedEnvironmentDefinitionError(f"malformed environment definition: {environment}")
        return {
            "environment": environment,
            "configuration": snapshot,
            "deployment_mode": "internal_deterministic",
            "external_services_required": False,
            "readiness_profile": environment,
        }

    def _normalize_environment(self, environment: str) -> str:
        if not isinstance(environment, str) or not environment.strip():
            raise MalformedEnvironmentDefinitionError("deployment environment is required")
        normalized = environment.strip().lower()
        if normalized not in SUPPORTED_DEPLOYMENT_ENVIRONMENTS:
            raise UnsupportedDeploymentEnvironmentError(f"unsupported deployment environment: {normalized}")
        return normalized
