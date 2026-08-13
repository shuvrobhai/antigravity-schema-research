"""
Pydantic model for session transcript JSONL steps (~/.gemini/antigravity-cli/brain/<id>/.system_generated/logs/transcript.jsonl).
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class StepSourceEnum(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    MODEL = "MODEL"
    SYSTEM = "SYSTEM"
    SUBAGENT = "SUBAGENT"


class StepTypeEnum(str, Enum):
    USER_INPUT = "USER_INPUT"
    PLANNER_RESPONSE = "PLANNER_RESPONSE"
    TOOL_CALL = "TOOL_CALL"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"
    SUBAGENT_DELEGATION = "SUBAGENT_DELEGATION"
    SUBAGENT_RESPONSE = "SUBAGENT_RESPONSE"
    ERROR = "ERROR"
    RECOVERY = "RECOVERY"


class StepStatusEnum(str, Enum):
    DONE = "DONE"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    ACTIVE = "ACTIVE"


class ToolCallDetail(BaseModel):
    name: str = Field(..., description="Tool name executed.")
    args: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arguments passed to tool.")
    result: Optional[Any] = Field(default=None, description="Returned result object or text.")


class TranscriptStepSchema(BaseModel):
    step_index: int = Field(..., description="0-indexed step sequence number.")
    source: Optional[Union[StepSourceEnum, str]] = Field(default=None, description="Origin source of step.")
    type: Union[StepTypeEnum, str] = Field(..., description="Type event identifier for step.")
    status: Optional[Union[StepStatusEnum, str]] = Field(default="DONE", description="Execution status.")
    content: Optional[str] = Field(default=None, description="Natural language prompt, text, or JSON snippet.")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Array of tool call objects.")
    is_truncated: Optional[bool] = Field(default=False, description="Flag indicating token-saving truncation in transcript.jsonl.")

    class Config:
        extra = "allow"
