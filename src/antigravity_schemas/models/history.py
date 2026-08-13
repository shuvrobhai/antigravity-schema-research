"""
Pydantic model for CLI Prompt History Entry (history.jsonl).
"""

from typing import Optional
from pydantic import BaseModel, Field


class CLIHistoryEntrySchema(BaseModel):
    timestamp: str = Field(..., description="Invocation timestamp (ISO-8601 or epoch).")
    prompt: str = Field(..., description="Executed prompt text input.")
    session_id: Optional[str] = Field(default=None, description="Associated session UUID.")
    conversation_id: Optional[str] = Field(default=None, description="Active conversation UUID.")
    cwd: Optional[str] = Field(default=None, description="Working directory path at execution time.")
    exit_code: Optional[int] = Field(default=0, description="Process exit code.")

    class Config:
        extra = "allow"
