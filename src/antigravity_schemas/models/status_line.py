"""
Pydantic model for Status Line custom script stdin payload.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class StatusLinePayloadSchema(BaseModel):
    cwd: str = Field(..., description="Current working directory path.")
    session_id: Optional[str] = Field(default=None, description="Active session ID.")
    conversation_id: Optional[str] = Field(default=None, description="Active conversation ID.")
    transcript_path: Optional[str] = Field(default=None, description="Path to transcript JSONL log file.")
    model: Optional[Dict[str, Any]] = Field(default=None, description="Model metadata object {id, display_name}.")
    workspace: Optional[Dict[str, Any]] = Field(default=None, description="Workspace directories object.")
    version: Optional[str] = Field(default=None, description="Antigravity CLI version string.")
    context_window: Optional[Dict[str, Any]] = Field(default=None, description="Token usage & context statistics.")
    exceeds_200k_tokens: Optional[bool] = Field(default=False, description="Flag if context exceeds 200k tokens.")
    product: Optional[str] = Field(default="Antigravity CLI", description="Product application name.")
    quota: Optional[Dict[str, Any]] = Field(default=None, description="Quota usage buckets metadata.")
    agent_state: Optional[str] = Field(default="idle", description="Current state ('idle', 'thinking', 'working', 'tool_use', 'initializing').")
    vcs: Optional[Dict[str, Any]] = Field(default=None, description="VCS metadata {type, branch, client, dirty}.")
    sandbox: Optional[Dict[str, Any]] = Field(default=None, description="Sandbox configuration metadata.")
    artifact_count: Optional[int] = Field(default=0, description="Count of artifacts created in session.")
    plan_tier: Optional[str] = Field(default=None, description="Subscription plan tier.")
    email: Optional[str] = Field(default=None, description="Authenticated account email.")
    pending_input_count: Optional[int] = Field(default=0, description="Queued prompt inputs count.")
    tool_confirmation_pending: Optional[bool] = Field(default=False, description="True if confirmation dialog is open.")
    task_count: Optional[int] = Field(default=0, description="Background tasks running count.")
    terminal_width: Optional[int] = Field(default=80, description="Terminal width in columns.")
    execution_mode: Optional[str] = Field(default="planning", description="Execution mode ('planning', 'fast').")
    vim: Optional[Dict[str, Any]] = Field(default=None, description="Vim state mode metadata.")

    class Config:
        extra = "allow"
