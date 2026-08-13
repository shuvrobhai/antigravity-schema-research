"""
Pydantic model for Workspace Projects Index (~/.gemini/projects.json).
"""

from typing import Dict
from pydantic import BaseModel, Field


class ProjectsIndexSchema(BaseModel):
    projects: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of absolute repository folder paths to project aliases."
    )

    class Config:
        extra = "allow"
