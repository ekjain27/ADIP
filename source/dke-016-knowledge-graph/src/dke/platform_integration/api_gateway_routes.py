from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .api_gateway_errors import ApiRequestValidationError, ApiUnauthorizedActionError


VALID_GATEWAY_METHODS: tuple[str, ...] = ("GET", "POST")


@dataclass(frozen=True)
class GatewayRequest:
    route: str
    method: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    action: str = "read"

    def normalized(self) -> "GatewayRequest":
        route = normalize_route(self.route)
        method = normalize_method(self.method)
        if not isinstance(self.payload, Mapping):
            raise ApiRequestValidationError("gateway payload must be a mapping")
        if self.action.startswith("external_") or self.action in {"delete", "admin", "network"}:
            raise ApiUnauthorizedActionError(f"unauthorized internal action: {self.action}")
        return GatewayRequest(route=route, method=method, payload=dict(sorted(self.payload.items())), action=self.action)


@dataclass(frozen=True)
class GatewayResponse:
    route: str
    method: str
    status: str
    payload: Any
    validation_metadata: Mapping[str, Any]
    errors: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "method": self.method,
            "status": self.status,
            "payload": self.payload,
            "validation_metadata": dict(self.validation_metadata),
            "errors": self.errors,
        }


@dataclass(frozen=True)
class GatewayRoute:
    path: str
    method: str
    handler: Callable[[GatewayRequest], Any]
    required_fields: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    def validate_request(self, request: GatewayRequest) -> GatewayRequest:
        normalized = request.normalized()
        if normalized.route != self.path or normalized.method != self.method:
            raise ApiRequestValidationError("request does not match gateway route")
        missing = tuple(field_name for field_name in self.required_fields if field_name not in normalized.payload)
        if missing:
            raise ApiRequestValidationError(f"gateway payload missing required field(s): {', '.join(missing)}")
        return normalized

    def snapshot(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "method": self.method,
            "required_fields": tuple(sorted(self.required_fields)),
            "description": self.description,
        }


def normalize_route(route: str) -> str:
    if not isinstance(route, str) or not route.strip():
        raise ApiRequestValidationError("gateway route is required")
    normalized = route.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized


def normalize_method(method: str) -> str:
    if not isinstance(method, str) or not method.strip():
        raise ApiRequestValidationError("gateway method is required")
    normalized = method.strip().upper()
    if normalized not in VALID_GATEWAY_METHODS:
        raise ApiRequestValidationError(f"invalid gateway method: {normalized}")
    return normalized
