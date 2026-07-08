from __future__ import annotations

import inspect
from typing import Any


def generate_api_catalog(api_objects: dict[str, object]) -> dict[str, Any]:
    entries = []
    for name, obj in sorted(api_objects.items()):
        public_methods = tuple(
            method_name
            for method_name, member in inspect.getmembers(obj.__class__, predicate=inspect.isfunction)
            if not method_name.startswith("_")
        )
        entries.append(
            {
                "component": name,
                "class": obj.__class__.__name__,
                "public_api": tuple(sorted(public_methods)),
            }
        )
    return {
        "catalog_type": "api_catalog",
        "component_count": len(entries),
        "components": tuple(entries),
    }
