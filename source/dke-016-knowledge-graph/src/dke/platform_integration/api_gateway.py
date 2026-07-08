from __future__ import annotations

from typing import Any, Mapping

from .api_gateway_errors import (
    ApiGatewayError,
    ApiRequestValidationError,
    ApiRouteNotFoundError,
    ApiRouteRegistrationError,
)
from .api_gateway_routes import GatewayRequest, GatewayResponse, GatewayRoute, normalize_method, normalize_route
from .contract_adapter_registry import ContractAdapterRegistry
from .platform_integration_layer import PlatformIntegrationLayer
from .runtime_registry import UnifiedPlatformRuntimeRegistry


class EnterpriseApiGateway:
    MODULE = "PI-004"

    def __init__(
        self,
        platform_layer: PlatformIntegrationLayer | None = None,
        runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
        adapter_registry: ContractAdapterRegistry | None = None,
    ) -> None:
        self.platform_layer = platform_layer
        self.runtime_registry = runtime_registry
        self.adapter_registry = adapter_registry
        self._routes: dict[tuple[str, str], GatewayRoute] = {}
        self._register_default_routes()

    def register_route(
        self,
        route: str,
        method: str,
        handler,
        required_fields: tuple[str, ...] = (),
        description: str = "",
    ) -> GatewayRoute:
        path = normalize_route(route)
        normalized_method = normalize_method(method)
        key = (path, normalized_method)
        if key in self._routes:
            raise ApiRouteRegistrationError(f"gateway route already registered: {normalized_method} {path}")
        if not callable(handler):
            raise ApiRouteRegistrationError("gateway route handler must be callable")
        gateway_route = GatewayRoute(path, normalized_method, handler, tuple(sorted(required_fields)), description)
        self._routes[key] = gateway_route
        return gateway_route

    def list_routes(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._routes[key].snapshot() for key in sorted(self._routes))

    def validate_request(self, route: str, method: str, payload: Mapping[str, Any] | None = None, action: str = "read") -> GatewayRequest:
        request = GatewayRequest(route=route, method=method, payload=payload or {}, action=action).normalized()
        gateway_route = self._get_route(request.route, request.method)
        return gateway_route.validate_request(request)

    def handle_request(
        self,
        route: str,
        method: str,
        payload: Mapping[str, Any] | None = None,
        action: str = "read",
    ) -> GatewayResponse:
        try:
            request = self.validate_request(route, method, payload, action)
            gateway_route = self._get_route(request.route, request.method)
            result = gateway_route.handler(request)
            return self._response(request, "success", self._normalize_payload(result))
        except ApiGatewayError:
            raise
        except Exception as exc:  # pragma: no cover - defensive envelope for injected handlers
            normalized_route = normalize_route(route)
            normalized_method = normalize_method(method)
            return GatewayResponse(
                route=normalized_route,
                method=normalized_method,
                status="error",
                payload=None,
                validation_metadata=self._metadata(normalized_route, normalized_method),
                errors=(str(exc),),
            )

    def export_gateway_snapshot(self) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "status": "exported",
            "route_count": len(self._routes),
            "routes": self.list_routes(),
            "integrations": {
                "platform_layer": self.platform_layer is not None,
                "runtime_registry": self.runtime_registry is not None,
                "adapter_registry": self.adapter_registry is not None,
            },
        }

    def _register_default_routes(self) -> None:
        self.register_route("/platform/components", "GET", self._platform_components, description="List PI-001 components")
        self.register_route(
            "/platform/execute",
            "POST",
            self._platform_execute,
            required_fields=("component", "payload"),
            description="Execute a PI-001 component",
        )
        self.register_route("/runtime/snapshot", "GET", self._runtime_snapshot, description="Export PI-002 runtime registry")
        self.register_route("/adapters", "GET", self._adapter_snapshot, description="Export PI-003 adapter registry")
        self.register_route(
            "/adapters/adapt",
            "POST",
            self._adapter_adapt,
            required_fields=("source", "target", "payload"),
            description="Adapt payload through PI-003",
        )

    def _platform_components(self, request: GatewayRequest) -> Any:
        self._require_integration(self.platform_layer, "platform layer")
        return {"components": self.platform_layer.list_components()}

    def _platform_execute(self, request: GatewayRequest) -> Any:
        self._require_integration(self.platform_layer, "platform layer")
        result = self.platform_layer.execute_component(request.payload["component"], request.payload["payload"])
        return result.to_dict()

    def _runtime_snapshot(self, request: GatewayRequest) -> Any:
        self._require_integration(self.runtime_registry, "runtime registry")
        return self.runtime_registry.export_registry_snapshot()

    def _adapter_snapshot(self, request: GatewayRequest) -> Any:
        self._require_integration(self.adapter_registry, "adapter registry")
        return self.adapter_registry.export_adapter_snapshot()

    def _adapter_adapt(self, request: GatewayRequest) -> Any:
        self._require_integration(self.adapter_registry, "adapter registry")
        result = self.adapter_registry.adapt_payload(
            request.payload["source"],
            request.payload["target"],
            request.payload["payload"],
        )
        return result.to_dict()

    def _get_route(self, route: str, method: str) -> GatewayRoute:
        key = (normalize_route(route), normalize_method(method))
        try:
            return self._routes[key]
        except KeyError as exc:
            raise ApiRouteNotFoundError(f"gateway route is not registered: {key[1]} {key[0]}") from exc

    def _response(self, request: GatewayRequest, status: str, payload: Any, errors: tuple[str, ...] = ()) -> GatewayResponse:
        return GatewayResponse(
            route=request.route,
            method=request.method,
            status=status,
            payload=payload,
            validation_metadata=self._metadata(request.route, request.method),
            errors=errors,
        )

    def _metadata(self, route: str, method: str) -> dict[str, Any]:
        return {
            "module": self.MODULE,
            "route": route,
            "method": method,
            "routes": tuple(f"{method} {route}" for route, method in sorted(self._routes)),
        }

    def _normalize_payload(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {key: payload[key] for key in sorted(payload)}
        return payload

    def _require_integration(self, integration: Any, name: str) -> None:
        if integration is None:
            raise ApiRequestValidationError(f"gateway {name} integration is required")


def create_enterprise_api_gateway(
    platform_layer: PlatformIntegrationLayer | None = None,
    runtime_registry: UnifiedPlatformRuntimeRegistry | None = None,
    adapter_registry: ContractAdapterRegistry | None = None,
) -> EnterpriseApiGateway:
    return EnterpriseApiGateway(
        platform_layer=platform_layer,
        runtime_registry=runtime_registry,
        adapter_registry=adapter_registry,
    )
