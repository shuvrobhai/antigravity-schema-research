"""
Pydantic model for MCP Server Configuration (mcp_config.json).
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, model_validator


class OAuthConfig(BaseModel):
    clientId: str = Field(..., description="OAuth Client ID.")
    clientSecret: Optional[str] = Field(default=None, description="OAuth Client Secret.")


class MCPServerConfig(BaseModel):
    command: Optional[str] = Field(default=None, description="Executable binary path for Stdio transport.")
    args: Optional[List[str]] = Field(default_factory=list, description="Command line arguments for Stdio process.")
    env: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables dictionary.")
    cwd: Optional[str] = Field(default=None, description="Working directory for Stdio process.")
    serverUrl: Optional[str] = Field(default=None, description="URL for SSE/HTTP Remote transport.")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="HTTP headers for Remote transport.")
    authProviderType: Optional[str] = Field(default=None, description="Auth provider type (e.g. 'google_credentials').")
    oauth: Optional[OAuthConfig] = Field(default=None, description="Manual OAuth credentials configuration.")
    disabled: Optional[bool] = Field(default=False, description="Disable this MCP server without removing configuration.")
    disabledTools: Optional[List[str]] = Field(default_factory=list, description="List of specific tool names to hide.")
    timeout: Optional[float] = Field(default=None, description="Request timeout in seconds.")

    @model_validator(mode="after")
    def validate_transport(self):
        if not self.command and not self.serverUrl:
            raise ValueError("MCPServerConfig must specify either 'command' (Stdio) or 'serverUrl' (Remote transport).")
        return self

    class Config:
        extra = "allow"


class MCPConfigSchema(BaseModel):
    mcpServers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict,
        description="Dictionary mapping server names to server configurations."
    )

    class Config:
        extra = "allow"
