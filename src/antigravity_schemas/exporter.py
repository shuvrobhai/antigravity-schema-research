"""
JSON Schema Exporter Utility for Antigravity Schemas.
Exports Pydantic v2 models to standard JSON Schema files in the output directory.
"""

import json
from pathlib import Path
from typing import Dict, Type
from pydantic import BaseModel

from .models import (
    SettingsSchema,
    PluginManifestSchema,
    AgentFrontmatterSchema,
    SkillFrontmatterSchema,
    MCPConfigSchema,
    HooksConfigSchema,
    TranscriptStepSchema,
    KeybindingsSchema,
    StatusLinePayloadSchema,
)

SCHEMA_MAPPING: Dict[str, Type[BaseModel]] = {
    "settings.schema.json": SettingsSchema,
    "plugin.schema.json": PluginManifestSchema,
    "agent.schema.json": AgentFrontmatterSchema,
    "skill.schema.json": SkillFrontmatterSchema,
    "mcp_config.schema.json": MCPConfigSchema,
    "hooks.schema.json": HooksConfigSchema,
    "transcript_step.schema.json": TranscriptStepSchema,
    "keybindings.schema.json": KeybindingsSchema,
    "status_line.schema.json": StatusLinePayloadSchema,
}


def export_all_schemas(output_dir: Path) -> Dict[str, Path]:
    """
    Exports all Pydantic models to JSON Schema files in output_dir.
    Returns mapping of schema name to path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    exported_files = {}

    for filename, model_cls in SCHEMA_MAPPING.items():
        schema_dict = model_cls.model_json_schema()
        target_path = output_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)
            f.write("\n")
        exported_files[filename] = target_path

    return exported_files
