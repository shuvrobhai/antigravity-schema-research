"""
Live System Auditor for Google Antigravity local files (~/.gemini/).
Validates local configuration files, plugin manifests, MCP configs, custom agents, skills, and brain transcripts against Pydantic models.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import yaml
from pydantic import ValidationError

from .models import (
    SettingsSchema,
    PluginManifestSchema,
    AgentFrontmatterSchema,
    SkillFrontmatterSchema,
    MCPConfigSchema,
    HooksConfigSchema,
    TranscriptStepSchema,
    KeybindingsSchema,
)


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown file content."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return {}
    return {}


class SystemAuditor:
    def __init__(self, gemini_root: Path = Path.home() / ".gemini"):
        self.gemini_root = gemini_root

    def audit_settings(self) -> Dict[str, Any]:
        settings_path = self.gemini_root / "antigravity-cli" / "settings.json"
        if not settings_path.exists():
            return {"status": "SKIPPED", "message": f"File not found: {settings_path}"}
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            SettingsSchema.model_validate(data)
            return {"status": "VALID", "path": str(settings_path), "keys_validated": len(data)}
        except Exception as e:
            return {"status": "INVALID", "path": str(settings_path), "error": str(e)}

    def audit_mcp_configs(self) -> List[Dict[str, Any]]:
        results = []
        paths = [
            self.gemini_root / "config" / "mcp_config.json",
            self.gemini_root / "antigravity-cli" / "mcp_config.json",
        ]
        for p in paths:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    MCPConfigSchema.model_validate(data)
                    results.append({"status": "VALID", "path": str(p)})
                except Exception as e:
                    results.append({"status": "INVALID", "path": str(p), "error": str(e)})
        return results

    def audit_skills(self) -> List[Dict[str, Any]]:
        results = []
        skills_dir = self.gemini_root / "config" / "skills"
        if not skills_dir.exists():
            return results

        for skill_file in skills_dir.glob("**/SKILL.md"):
            try:
                content = skill_file.read_text(encoding="utf-8")
                frontmatter = parse_frontmatter(content)
                SkillFrontmatterSchema.model_validate(frontmatter)
                results.append({"status": "VALID", "path": str(skill_file)})
            except Exception as e:
                results.append({"status": "INVALID", "path": str(skill_file), "error": str(e)})
        return results

    def audit_agents(self) -> List[Dict[str, Any]]:
        results = []
        agents_dir = self.gemini_root / "config" / "agents"
        if not agents_dir.exists():
            return results

        for agent_file in agents_dir.glob("*.md"):
            try:
                content = agent_file.read_text(encoding="utf-8")
                frontmatter = parse_frontmatter(content)
                AgentFrontmatterSchema.model_validate(frontmatter)
                results.append({"status": "VALID", "path": str(agent_file)})
            except Exception as e:
                results.append({"status": "INVALID", "path": str(agent_file), "error": str(e)})
        return results

    def audit_transcripts(self, max_files: int = 5) -> List[Dict[str, Any]]:
        results = []
        brain_dir = self.gemini_root / "antigravity-cli" / "brain"
        if not brain_dir.exists():
            return results

        transcript_files = list(brain_dir.glob("**/.system_generated/logs/transcript.jsonl"))[:max_files]
        for t_file in transcript_files:
            valid_steps = 0
            invalid_steps = 0
            errors = []
            try:
                with open(t_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if not line.strip():
                            continue
                        try:
                            step_data = json.loads(line)
                            TranscriptStepSchema.model_validate(step_data)
                            valid_steps += 1
                        except Exception as err:
                            invalid_steps += 1
                            errors.append(f"Line {line_num}: {err}")
                results.append({
                    "status": "VALID" if invalid_steps == 0 else "INVALID",
                    "path": str(t_file),
                    "valid_steps": valid_steps,
                    "invalid_steps": invalid_steps,
                    "sample_errors": errors[:3]
                })
            except Exception as file_err:
                results.append({"status": "ERROR", "path": str(t_file), "error": str(file_err)})
        return results

    def run_full_audit(self) -> Dict[str, Any]:
        return {
            "settings": self.audit_settings(),
            "mcp_configs": self.audit_mcp_configs(),
            "skills": self.audit_skills(),
            "agents": self.audit_agents(),
            "transcripts": self.audit_transcripts(),
        }
