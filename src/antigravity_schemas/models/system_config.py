"""
Pydantic model for Master Configuration (~/.gemini/config/config.json).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PluginState(BaseModel):
    enabled: bool = Field(default=True, description="Enable or disable plugin.")


class PermissionGrants(BaseModel):
    allow: Optional[List[str]] = Field(default_factory=list, description="Global allowlist rules.")
    deny: Optional[List[str]] = Field(default_factory=list, description="Global denylist rules.")


class MasterUserSettings(BaseModel):
    artifactReviewMode: Optional[str] = Field(default=None, description="Artifact review policy mode.")
    autoExecutionPolicy: Optional[str] = Field(default=None, description="Command cascade auto execution policy.")
    browserJsExecutionPolicy: Optional[str] = Field(default=None, description="Browser JS execution safety mode.")
    enableTerminalSandbox: Optional[bool] = Field(default=False, description="Enable terminal execution sandbox.")
    globalPermissionGrants: Optional[PermissionGrants] = Field(default=None, description="Global permission grants allow/deny lists.")
    nonWorkspaceFileAccessPolicy: Optional[str] = Field(default=None, description="Access policy for files outside workspace.")
    queuedMessageDeliveryStrategy: Optional[str] = Field(default=None, description="Delivery mode for queued agent messages.")
    remoteControlHostname: Optional[str] = Field(default=None, description="Remote control device hostname.")
    themeMode: Optional[str] = Field(default=None, description="UI visual theme mode.")


class MasterConfigSchema(BaseModel):
    plugins: Dict[str, PluginState] = Field(
        default_factory=dict,
        description="Map of plugin identifiers to activation state."
    )
    userSettings: Optional[MasterUserSettings] = Field(
        default=None,
        description="Global master user settings configuration."
    )

    class Config:
        extra = "allow"
