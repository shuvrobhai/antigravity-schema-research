"""
Pydantic model for Antigravity CLI Installation State (state.json).
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ProviderStatus(BaseModel):
    id: str = Field(..., description="Provider identifier (e.g. 'github', 'google').")
    status: str = Field(..., description="Auth status ('authenticated', 'unauthenticated').")
    scopes: List[str] = Field(default_factory=list, description="Granted OAuth scopes list.")


class InstalledTools(BaseModel):
    mcp_servers: List[str] = Field(default_factory=list, description="Installed MCP server names.")
    plugins: List[str] = Field(default_factory=list, description="Installed plugin names.")


class CLIStateSchema(BaseModel):
    schema_uri: Optional[str] = Field(default=None, alias="$schema", description="JSON Schema URI.")
    runtimes: Optional[Dict[str, Union[str, bool]]] = Field(default_factory=dict, description="Detected local runtime binary versions.")
    providers: Optional[List[ProviderStatus]] = Field(default_factory=list, description="Connected service providers list.")
    installed_tools: Optional[InstalledTools] = Field(default=None, description="Installed MCP servers and plugins breakdown.")

    class Config:
        extra = "allow"
        populate_by_name = True
