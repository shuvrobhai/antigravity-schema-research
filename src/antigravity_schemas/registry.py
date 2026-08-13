"""
Centralized Schema Registry for Antigravity JSON Schemas.
Single source of truth for Pydantic model classes, CLI aliases, canonical schema filenames, and metadata.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Type
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
    MasterConfigSchema,
    ProjectsIndexSchema,
    DesktopStateSchema,
    IDEStateSchema,
    RuleFileSchema,
    CLIStateSchema,
    CLIHistoryEntrySchema,
    TrustedHooksSchema,
)


@dataclass(frozen=True)
class SchemaDescriptor:
    key: str
    model_cls: Type[BaseModel]
    filename: str
    category: str
    description: str


class SchemaRegistry:
    def __init__(self):
        self._registry: Dict[str, SchemaDescriptor] = {}
        self._by_filename: Dict[str, SchemaDescriptor] = {}
        self._by_model: Dict[Type[BaseModel], SchemaDescriptor] = {}
        self._bootstrap_defaults()

    def _bootstrap_defaults(self):
        descriptors = [
            SchemaDescriptor(
                key="settings",
                model_cls=SettingsSchema,
                filename="settings.schema.json",
                category="Core Config",
                description="Global CLI configuration and tool permissions",
            ),
            SchemaDescriptor(
                key="plugin",
                model_cls=PluginManifestSchema,
                filename="plugin.schema.json",
                category="Plugin System",
                description="Plugin manifest specification (plugin.json)",
            ),
            SchemaDescriptor(
                key="agent",
                model_cls=AgentFrontmatterSchema,
                filename="agent.schema.json",
                category="Agent System",
                description="Custom subagent markdown frontmatter",
            ),
            SchemaDescriptor(
                key="skill",
                model_cls=SkillFrontmatterSchema,
                filename="skill.schema.json",
                category="Agent System",
                description="Agent skill SKILL.md frontmatter",
            ),
            SchemaDescriptor(
                key="mcp",
                model_cls=MCPConfigSchema,
                filename="mcp_config.schema.json",
                category="Integration",
                description="Model Context Protocol (MCP) server configuration",
            ),
            SchemaDescriptor(
                key="hooks",
                model_cls=HooksConfigSchema,
                filename="hooks.schema.json",
                category="Lifecycle",
                description="Event hook configuration (pre/post execution hooks)",
            ),
            SchemaDescriptor(
                key="transcript",
                model_cls=TranscriptStepSchema,
                filename="transcript_step.schema.json",
                category="Runtime State",
                description="Agent brain execution step in transcript.jsonl",
            ),
            SchemaDescriptor(
                key="keybindings",
                model_cls=KeybindingsSchema,
                filename="keybindings.schema.json",
                category="Core Config",
                description="Keyboard shortcut and keybinding definitions",
            ),
            SchemaDescriptor(
                key="status_line",
                model_cls=StatusLinePayloadSchema,
                filename="status_line.schema.json",
                category="Runtime State",
                description="Live terminal status line context payload",
            ),
            SchemaDescriptor(
                key="master_config",
                model_cls=MasterConfigSchema,
                filename="master_config.schema.json",
                category="System Config",
                description="Master configuration manifest (master_config.json)",
            ),
            SchemaDescriptor(
                key="projects",
                model_cls=ProjectsIndexSchema,
                filename="projects.schema.json",
                category="System Config",
                description="Projects index manifest (projects.json)",
            ),
            SchemaDescriptor(
                key="desktop_state",
                model_cls=DesktopStateSchema,
                filename="desktop_state.schema.json",
                category="Ecosystem App",
                description="Antigravity 2.0 Desktop app state (state.pbtxt)",
            ),
            SchemaDescriptor(
                key="ide_state",
                model_cls=IDEStateSchema,
                filename="ide_state.schema.json",
                category="Ecosystem App",
                description="Antigravity IDE app state metadata",
            ),
            SchemaDescriptor(
                key="rule",
                model_cls=RuleFileSchema,
                filename="rule.schema.json",
                category="Agent System",
                description="Behavioral agent rules manifest (AGENTS.md, rules/*.md)",
            ),
            SchemaDescriptor(
                key="cli_state",
                model_cls=CLIStateSchema,
                filename="cli_state.schema.json",
                category="Runtime State",
                description="CLI installation state manifest (~/.gemini/antigravity-cli/state.json)",
            ),
            SchemaDescriptor(
                key="history",
                model_cls=CLIHistoryEntrySchema,
                filename="history_entry.schema.json",
                category="Runtime State",
                description="CLI prompt history entry (history.jsonl)",
            ),
            SchemaDescriptor(
                key="trusted_hooks",
                model_cls=TrustedHooksSchema,
                filename="trusted_hooks.schema.json",
                category="Lifecycle",
                description="Trusted security hook script hashes (trusted_hooks.json)",
            ),
        ]

        for desc in descriptors:
            self.register(desc)

    def register(self, descriptor: SchemaDescriptor):
        self._registry[descriptor.key] = descriptor
        self._by_filename[descriptor.filename] = descriptor
        self._by_model[descriptor.model_cls] = descriptor

    def get(self, key: str) -> Optional[SchemaDescriptor]:
        return self._registry.get(key)

    def get_by_filename(self, filename: str) -> Optional[SchemaDescriptor]:
        return self._by_filename.get(filename)

    def get_by_model(self, model_cls: Type[BaseModel]) -> Optional[SchemaDescriptor]:
        return self._by_model.get(model_cls)

    def all_descriptors(self) -> List[SchemaDescriptor]:
        return list(self._registry.values())

    def schema_mapping(self) -> Dict[str, Type[BaseModel]]:
        """Returns map of canonical filename to model class."""
        return {desc.filename: desc.model_cls for desc in self._registry.values()}

    def model_mapping(self) -> Dict[str, Type[BaseModel]]:
        """Returns map of CLI short key to model class."""
        return {desc.key: desc.model_cls for desc in self._registry.values()}

    def export_all(self, output_dir: Path) -> Dict[str, Path]:
        """Exports all registered Pydantic models to JSON Schema files in output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}

        for desc in self._registry.values():
            schema_dict = desc.model_cls.model_json_schema()
            target_path = output_dir / desc.filename
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(schema_dict, f, indent=2)
                f.write("\n")
            exported_files[desc.filename] = target_path

        return exported_files


# Default singleton instance
registry = SchemaRegistry()
