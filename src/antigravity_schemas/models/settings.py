"""
Pydantic model for Antigravity CLI settings.json (~/.gemini/antigravity-cli/settings.json).
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class ToolPermissionEnum(str, Enum):
    REQUEST_REVIEW = "request-review"
    PROCEED_IN_SANDBOX = "proceed-in-sandbox"
    ALWAYS_PROCEED = "always-proceed"
    STRICT = "strict"


class ArtifactReviewPolicyEnum(str, Enum):
    ASKS_FOR_REVIEW = "asks-for-review"
    AGENT_DECIDES = "agent-decides"
    ALWAYS_PROCEED = "always-proceed"


class ColorSchemeEnum(str, Enum):
    LIGHT = "light"
    SOLARIZED_LIGHT = "solarized light"
    COLORBLIND_FRIENDLY_LIGHT = "colorblind-friendly light"
    DARK = "dark"
    SOLARIZED_DARK = "solarized dark"
    COLORBLIND_FRIENDLY_DARK = "colorblind-friendly dark"
    TOKYO_NIGHT = "tokyo night"
    TERMINAL = "terminal"


class AltScreenModeEnum(str, Enum):
    DEFAULT = "default"
    ALWAYS = "always"
    NEVER = "never"


class EditorModeEnum(str, Enum):
    DEFAULT = "default"
    VIM = "vim"


class VerbosityEnum(str, Enum):
    HIGH = "high"
    LOW = "low"


class RunningLightSpeedEnum(str, Enum):
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    OFF = "off"


class FooterConfig(BaseModel):
    items: Optional[List[str]] = Field(
        default=None,
        description="List of widget IDs displayed in the status footer."
    )


class UIConfig(BaseModel):
    language: Optional[str] = Field(default="us", description="Interface language code.")
    footer: Optional[FooterConfig] = Field(default=None, description="Footer widget configuration.")


class CommandScriptConfig(BaseModel):
    type: str = Field(default="command", description="Type of script execution.")
    command: str = Field(..., description="Executable path or command.")
    padding: Optional[int] = Field(default=0, description="Padding in spaces.")
    enabled: Optional[bool] = Field(default=True, description="Enable or disable custom status script.")
    stack_with_default: Optional[bool] = Field(default=False, description="Stack custom output with default status line.")


class PermissionsConfig(BaseModel):
    allow: Optional[List[str]] = Field(default_factory=list, description="Allowlist rules.")
    deny: Optional[List[str]] = Field(default_factory=list, description="Denylist rules.")
    ask: Optional[List[str]] = Field(default_factory=list, description="Asklist rules.")


class GeneralConfig(BaseModel):
    preferredEditor: Optional[str] = Field(default=None, description="Preferred code editor binary or alias.")
    openEditorInNewWindow: Optional[bool] = Field(default=False, description="Open editor in a new window.")
    vimMode: Optional[bool] = Field(default=False, description="Enable Vim keybindings globally.")


class SettingsSchema(BaseModel):
    toolPermission: Optional[ToolPermissionEnum] = Field(
        default=ToolPermissionEnum.REQUEST_REVIEW,
        description="Global permission policy for tool execution."
    )
    artifactReviewPolicy: Optional[ArtifactReviewPolicyEnum] = Field(
        default=ArtifactReviewPolicyEnum.ASKS_FOR_REVIEW,
        description="Review policy for artifact generation."
    )
    enableTerminalSandbox: Optional[bool] = Field(
        default=False,
        description="Run terminal commands in an isolated sandbox environment."
    )
    allowNonWorkspaceAccess: Optional[bool] = Field(
        default=False,
        description="Allow reading/writing files outside the active workspace root."
    )
    trustedWorkspaces: Optional[List[str]] = Field(
        default_factory=list,
        description="List of trusted local repository directory paths."
    )
    colorScheme: Optional[ColorSchemeEnum] = Field(
        default=ColorSchemeEnum.TERMINAL,
        description="TUI color palette theme."
    )
    altScreenMode: Optional[AltScreenModeEnum] = Field(
        default=AltScreenModeEnum.DEFAULT,
        description="Terminal alternate screen mode usage."
    )
    notifications: Optional[bool] = Field(
        default=False,
        description="Enable desktop OS notifications."
    )
    showTips: Optional[bool] = Field(
        default=True,
        description="Display helpful usage tips in UI."
    )
    showFeedbackSurvey: Optional[bool] = Field(
        default=True,
        description="Prompt for periodic feedback surveys."
    )
    ui: Optional[UIConfig] = Field(
        default=None,
        description="User interface configuration settings."
    )
    editor: Optional[str] = Field(
        default="auto",
        description="External editor command or auto-detection mode."
    )
    editorMode: Optional[EditorModeEnum] = Field(
        default=EditorModeEnum.DEFAULT,
        description="Keyboard navigation mode for input editor."
    )
    vimInsertFirst: Optional[bool] = Field(
        default=False,
        description="Default to insert mode when opening editor with Vim mode."
    )
    verbosity: Optional[VerbosityEnum] = Field(
        default=VerbosityEnum.HIGH,
        description="Output verbosity level."
    )
    runningLightSpeed: Optional[RunningLightSpeedEnum] = Field(
        default=RunningLightSpeedEnum.MEDIUM,
        description="Animation speed of the running indicator light."
    )
    useG1Credits: Optional[bool] = Field(
        default=False,
        description="Use Google One credits for external model calls."
    )
    enableTelemetry: Optional[bool] = Field(
        default=True,
        description="Enable anonymous usage telemetry."
    )
    model: Optional[str] = Field(
        default=None,
        description="Persisted default model selection string (e.g. 'Gemini 3.5 Flash (Low)')."
    )
    title: Optional[CommandScriptConfig] = Field(
        default=None,
        description="Custom script for dynamic terminal title rendering."
    )
    statusLine: Optional[CommandScriptConfig] = Field(
        default=None,
        description="Custom status line script configuration."
    )
    permissions: Optional[PermissionsConfig] = Field(
        default=None,
        description="Explicit tool permission rules (allow/deny/ask)."
    )
    general: Optional[GeneralConfig] = Field(
        default=None,
        description="General application preferences."
    )
    policyPaths: Optional[List[str]] = Field(
        default_factory=list,
        description="Paths to user custom policy files."
    )
    adminPolicyPaths: Optional[List[str]] = Field(
        default_factory=list,
        description="Paths to system/admin policy files."
    )

    class Config:
        extra = "allow"
