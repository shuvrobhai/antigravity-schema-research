"""
Pydantic model for TUI Keybindings (keybindings.json).
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class KeybindingsSchema(BaseModel):
    bindings: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of TUI action names (e.g., 'cli.escape') to hotkey arrays (e.g. ['Escape'])."
    )

    class Config:
        extra = "allow"
