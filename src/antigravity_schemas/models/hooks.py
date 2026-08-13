"""
Pydantic model for Lifecycle Hooks (hooks.json).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, RootModel


class HookAction(BaseModel):
    type: Optional[str] = Field(default="command", description="Type of hook action execution.")
    command: str = Field(..., description="Script path or shell command to execute.")
    timeout: Optional[int] = Field(default=30, description="Execution timeout in seconds.")


class HookRule(BaseModel):
    matcher: Optional[str] = Field(default="", description="Regex or string matcher for tool/invocation filter.")
    hooks: List[HookAction] = Field(..., description="List of hook actions to execute on match.")


class HookBinding(BaseModel):
    enabled: Optional[bool] = Field(default=True, description="Enable or disable hook set.")
    PreToolUse: Optional[List[HookRule]] = Field(default_factory=list, description="Hooks run before tool execution.")
    PostToolUse: Optional[List[HookRule]] = Field(default_factory=list, description="Hooks run after tool execution.")
    PreInvocation: Optional[List[HookRule]] = Field(default_factory=list, description="Hooks run before model invocation.")
    PostInvocation: Optional[List[HookRule]] = Field(default_factory=list, description="Hooks run after model invocation.")
    Stop: Optional[List[HookRule]] = Field(default_factory=list, description="Hooks run on session stop.")


class HooksConfigSchema(RootModel[Dict[str, HookBinding]]):
    root: Dict[str, HookBinding] = Field(
        default_factory=dict,
        description="Named hook set configurations."
    )
