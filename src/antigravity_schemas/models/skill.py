"""
Pydantic model for Skill YAML frontmatter (.agents/skills/<name>/SKILL.md).
"""

from typing import Optional
from pydantic import BaseModel, Field


class SkillFrontmatterSchema(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Unique skill name. Defaults to folder name if omitted."
    )
    description: str = Field(
        ...,
        description="Trigger description explaining what the skill does and when the agent should activate it."
    )

    class Config:
        extra = "allow"
