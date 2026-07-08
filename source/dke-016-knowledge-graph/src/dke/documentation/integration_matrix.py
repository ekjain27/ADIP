from __future__ import annotations

from typing import Any

from .api_errors import InconsistentIntegrationMappingError
from .api_models import IntegrationMapping


def generate_integration_matrix(mappings: tuple[IntegrationMapping, ...]) -> dict[str, Any]:
    seen: set[str] = set()
    rows = []
    for mapping in sorted(mappings, key=lambda item: item.mapping_id):
        if mapping.mapping_id in seen:
            raise InconsistentIntegrationMappingError(f"duplicate integration mapping: {mapping.mapping_id}")
        seen.add(mapping.mapping_id)
        rows.append(mapping.snapshot())
    return {
        "matrix_type": "integration_matrix",
        "mapping_count": len(rows),
        "mappings": tuple(rows),
    }
