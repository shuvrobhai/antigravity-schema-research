"""
Pydantic model for Trusted Hooks Configuration (trusted_hooks.json).
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, RootModel


class TrustedHooksSchema(BaseModel):
    trusted_hashes: Optional[Dict[str, str]] = Field(default_factory=dict, description="Map of script paths to approved SHA-256 hashes.")
    trusted_scripts: Optional[List[str]] = Field(default_factory=list, description="List of auto-approved hook script paths.")
    auto_approve_sandbox: Optional[bool] = Field(default=False, description="Auto-approve hooks executing inside isolated sandbox.")

    class Config:
        extra = "allow"
