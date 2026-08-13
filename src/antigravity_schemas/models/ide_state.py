"""
Pydantic model for Antigravity IDE State (~/.gemini/antigravity-ide/).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BrowserRecordingSession(BaseModel):
    recording_id: str = Field(..., description="UUID of recorded browser session.")
    frame_count: Optional[int] = Field(default=0, description="Total captured JPEG frames.")
    path: str = Field(..., description="Directory path containing frame screenshots.")


class IDEStateSchema(BaseModel):
    installation_id: Optional[str] = Field(
        default=None,
        description="Unique installation identifier for Antigravity IDE."
    )
    active_conversations_count: Optional[int] = Field(
        default=0,
        description="Number of active IDE conversation databases (.db)."
    )
    html_artifacts_count: Optional[int] = Field(
        default=0,
        description="Number of generated HTML artifact previews in ide/html_artifacts/."
    )
    browser_recordings: List[BrowserRecordingSession] = Field(
        default_factory=list,
        description="List of recorded browser interaction playbacks."
    )

    class Config:
        extra = "allow"
