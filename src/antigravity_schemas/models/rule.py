"""
Pydantic model for Antigravity Rule Files (AGENTS.md, GEMINI.md, .agents/rules/*.md).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RuleDefinition(BaseModel):
    rule_id: Optional[str] = Field(default=None, description="Unique rule identifier tag (e.g. RULE[user_global]).")
    description: str = Field(..., description="Behavioral constraint or instruction summary.")
    incorrect_example: Optional[str] = Field(default=None, description="Contrastive bad practice snippet.")
    correct_example: Optional[str] = Field(default=None, description="Contrastive good practice snippet.")


class RuleFileSchema(BaseModel):
    name: Optional[str] = Field(default=None, description="Rule set name or file header.")
    scope: Optional[str] = Field(default="workspace", description="Rule scope ('global', 'workspace', 'plugin').")
    rules: List[RuleDefinition] = Field(default_factory=list, description="List of structured rule definitions.")
    content: Optional[str] = Field(default=None, description="Raw rule markdown body.")

    class Config:
        extra = "allow"
