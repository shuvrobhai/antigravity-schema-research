"""
Pydantic model and parser for Antigravity 2.0 Desktop Application State (~/.gemini/antigravity/antigravity_state.pbtxt).
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class PostOnboardingState(BaseModel):
    completed_steps: List[str] = Field(
        default_factory=list,
        description="List of completed desktop onboarding step enums."
    )


class SeenNuxsState(BaseModel):
    uids: List[int] = Field(
        default_factory=list,
        description="List of New User Experience (NUX) feature notice UIDs acknowledged by user."
    )


class MigrationEntry(BaseModel):
    key: int = Field(..., description="Migration step ID key.")
    value: str = Field(..., description="Migration status enum value.")


class DesktopStateSchema(BaseModel):
    post_onboarding: Optional[PostOnboardingState] = Field(
        default=None,
        description="Desktop app post-onboarding completion state."
    )
    seen_nuxs: Optional[SeenNuxsState] = Field(
        default=None,
        description="Acknowledged NUX dialogs state."
    )
    agent_onboarding_completed: Optional[str] = Field(
        default="AGENT_ONBOARDING_STATE_UNSPECIFIED",
        description="Agent onboarding completion status enum."
    )
    last_selected_agent_model: Optional[str] = Field(
        default=None,
        description="Last active model selection string in Desktop GUI."
    )
    migrate_convos_into_projects: Optional[str] = Field(
        default=None,
        description="Status of project conversation migration."
    )
    installation_uuid: Optional[str] = Field(
        default=None,
        description="Unique desktop application installation UUID."
    )
    migrate_retroactive_projects: Optional[str] = Field(
        default=None,
        description="Retroactive project migration status enum."
    )
    migrations: List[MigrationEntry] = Field(
        default_factory=list,
        description="List of system database migration status entries."
    )

    class Config:
        extra = "allow"


def parse_pbtxt_state(content: str) -> Dict[str, Any]:
    """
    Lightweight parser for protobuf text format (.pbtxt) used in antigravity_state.pbtxt.
    """
    result: Dict[str, Any] = {
        "post_onboarding": {"completed_steps": []},
        "seen_nuxs": {"uids": []},
        "migrations": [],
    }

    current_section = None
    section_buffer = []

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.endswith("{"):
            sec_name = line.split("{")[0].strip()
            current_section = sec_name
            continue
        elif line == "}":
            current_section = None
            continue

        if current_section == "post_onboarding":
            if line.startswith("completed_steps:"):
                val = line.split(":", 1)[1].strip()
                result["post_onboarding"]["completed_steps"].append(val)
        elif current_section == "seen_nuxs":
            if line.startswith("uids:"):
                val = line.split(":", 1)[1].strip()
                if val.isdigit():
                    result["seen_nuxs"]["uids"].append(int(val))
        elif current_section == "migrations":
            # Handles key/value pairs in section
            pass
        else:
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"')
                result[k] = v

    return result
