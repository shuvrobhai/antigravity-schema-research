"""
Pydantic Schema Models for Google Antigravity Configuration and Runtime Objects.
"""

from .settings import SettingsSchema
from .plugin import PluginManifestSchema
from .agent import AgentFrontmatterSchema
from .skill import SkillFrontmatterSchema
from .mcp import MCPConfigSchema
from .hooks import HooksConfigSchema
from .transcript import TranscriptStepSchema
from .keybindings import KeybindingsSchema
from .status_line import StatusLinePayloadSchema
from .system_config import MasterConfigSchema
from .projects import ProjectsIndexSchema
from .desktop_state import DesktopStateSchema
from .ide_state import IDEStateSchema
from .rule import RuleFileSchema, RuleDefinition
from .cli_state import CLIStateSchema
from .history import CLIHistoryEntrySchema
from .trusted_hooks import TrustedHooksSchema

__all__ = [
    "SettingsSchema",
    "PluginManifestSchema",
    "AgentFrontmatterSchema",
    "SkillFrontmatterSchema",
    "MCPConfigSchema",
    "HooksConfigSchema",
    "TranscriptStepSchema",
    "KeybindingsSchema",
    "StatusLinePayloadSchema",
    "MasterConfigSchema",
    "ProjectsIndexSchema",
    "DesktopStateSchema",
    "IDEStateSchema",
    "RuleFileSchema",
    "RuleDefinition",
    "CLIStateSchema",
    "CLIHistoryEntrySchema",
    "TrustedHooksSchema",
]
