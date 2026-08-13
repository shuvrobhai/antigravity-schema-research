"""
Pydantic model for Custom Agent YAML frontmatter (.agents/agents/<name>.md).
"""

from typing import List, Optional, Union, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class CommandExecutionPolicyEnum(str, Enum):
    OFF = "off"
    AUTO = "auto"
    EAGER = "eager"
    SANDBOX = "sandbox"


class AgentFrontmatterSchema(BaseModel):
    name: str = Field(
        ...,
        description="Unique identifier for the subagent/custom agent (lowercase, hyphens)."
    )
    description: str = Field(
        ...,
        description="Detailed description used by the planner to determine subagent delegation."
    )
    tools: Optional[List[str]] = Field(
        default_factory=list,
        description="List of permitted built-in or MCP tool names for this agent."
    )
    mainAgent: Optional[bool] = Field(
        default=True,
        description="Whether this agent can be selected as the primary agent in chat."
    )
    subagent: Optional[bool] = Field(
        default=True,
        description="Whether this agent can be invoked via `invoke_subagent`."
    )
    model: Optional[str] = Field(
        default="inherit",
        description="Model tier specification ('inherit', 'flash', 'pro', 'flash_lite')."
    )
    commandExecutionPolicy: Optional[CommandExecutionPolicyEnum] = Field(
        default=CommandExecutionPolicyEnum.SANDBOX,
        description="Shell execution safety policy for run_command."
    )
    mcpServers: Optional[List[Union[str, Dict[str, Any]]]] = Field(
        default_factory=list,
        description="Custom MCP servers or server references bound to this subagent."
    )
    skills: Optional[List[str]] = Field(
        default_factory=list,
        description="List of relative skill paths pre-loaded for this agent."
    )
    plugins: Optional[List[str]] = Field(
        default_factory=list,
        description="List of plugin dependencies required by this agent."
    )

    class Config:
        extra = "allow"
