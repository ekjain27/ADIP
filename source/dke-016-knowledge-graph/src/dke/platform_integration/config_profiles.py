from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config_errors import InvalidConfigProfileError


VALID_CONFIG_PROFILES: tuple[str, ...] = ("local", "test", "staging", "production")
DETERMINISTIC_CONFIG_TIMESTAMP = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class ConfigFieldSpec:
    key: str
    value_type: type
    required: bool = True
    description: str = ""

    def metadata(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value_type": self.value_type.__name__,
            "required": self.required,
            "description": self.description,
        }


CONFIG_SCHEMA: tuple[ConfigFieldSpec, ...] = (
    ConfigFieldSpec("profile", str, description="Active platform configuration profile"),
    ConfigFieldSpec("platform_name", str, description="Platform display name"),
    ConfigFieldSpec("debug_enabled", bool, description="Internal debug mode flag"),
    ConfigFieldSpec("strict_validation", bool, description="Strict platform validation flag"),
    ConfigFieldSpec("gateway_enabled", bool, description="Internal gateway availability flag"),
    ConfigFieldSpec("runtime_registry_enabled", bool, description="Runtime registry availability flag"),
    ConfigFieldSpec("adapter_registry_enabled", bool, description="Contract adapter availability flag"),
    ConfigFieldSpec("max_pipeline_steps", int, description="Maximum deterministic pipeline length"),
)


def normalize_profile(profile: str) -> str:
    if not isinstance(profile, str) or not profile.strip():
        raise InvalidConfigProfileError("configuration profile is required")
    normalized = profile.strip().lower()
    if normalized not in VALID_CONFIG_PROFILES:
        raise InvalidConfigProfileError(f"invalid configuration profile: {normalized}")
    return normalized


def default_profile_values(profile: str) -> dict[str, Any]:
    normalized = normalize_profile(profile)
    values: dict[str, Any] = {
        "profile": normalized,
        "platform_name": "AI Decision Intelligence Platform",
        "debug_enabled": False,
        "strict_validation": True,
        "gateway_enabled": True,
        "runtime_registry_enabled": True,
        "adapter_registry_enabled": True,
        "max_pipeline_steps": 10,
    }
    if normalized in {"local", "test"}:
        values["debug_enabled"] = True
    if normalized == "test":
        values["max_pipeline_steps"] = 5
    if normalized == "production":
        values["max_pipeline_steps"] = 25
    return values
