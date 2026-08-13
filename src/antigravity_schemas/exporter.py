"""
JSON Schema Exporter Utility for Antigravity Schemas.
Delegates schema resolution and export operations to SchemaRegistry.
"""

from pathlib import Path
from typing import Dict, Type
from pydantic import BaseModel

from .registry import registry

# Backward-compatible dynamic schema mapping
SCHEMA_MAPPING: Dict[str, Type[BaseModel]] = registry.schema_mapping()


def export_all_schemas(output_dir: Path) -> Dict[str, Path]:
    """
    Exports all Pydantic models to JSON Schema files in output_dir.
    Returns mapping of schema name to path.
    """
    return registry.export_all(output_dir)
