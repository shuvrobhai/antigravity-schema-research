"""
Pydantic model for Antigravity plugin manifest (plugin.json).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PluginManifestSchema(BaseModel):
    schema_uri: Optional[str] = Field(
        default="https://antigravity.google/schemas/v1/plugin.json",
        alias="$schema",
        description="JSON Schema URI for plugin manifest validation."
    )
    name: Optional[str] = Field(
        default=None,
        description="Name of the plugin. Defaults to parent folder name if omitted."
    )
    version: Optional[str] = Field(
        default="1.0.0",
        description="Semantic version string."
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief description of the plugin functionality."
    )
    author: Optional[str] = Field(
        default=None,
        description="Author or organization name."
    )
    license: Optional[str] = Field(
        default=None,
        description="License identifier (e.g. MIT, Apache-2.0)."
    )
    dependencies: Optional[List[str]] = Field(
        default_factory=list,
        description="List of plugin dependencies required by this plugin."
    )

    class Config:
        populate_by_name = True
        extra = "allow"
