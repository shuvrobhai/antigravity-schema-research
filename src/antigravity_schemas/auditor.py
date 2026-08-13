"""
Live System Auditor for Google Antigravity local files (~/.gemini/).
Validates local configuration files, plugin manifests, MCP configs, custom agents, skills, and brain transcripts against Pydantic models.
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
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


class AuditStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class CategoryAuditResult:
    category: str
    status: AuditStatus
    path: str
    details: str
    valid_count: int = 0
    invalid_count: int = 0
    sample_errors: List[str] = field(default_factory=list)

    def to_table_row(self) -> tuple[str, str, str]:
        status_color = {
            AuditStatus.VALID: "green",
            AuditStatus.SKIPPED: "yellow",
            AuditStatus.INVALID: "red",
            AuditStatus.ERROR: "red",
        }.get(self.status, "white")
        formatted_status = f"[{status_color}]{self.status.value}[/{status_color}]"
        return (self.category, formatted_status, self.details)


@dataclass
class AuditReport:
    results: List[CategoryAuditResult]

    @property
    def total_audited(self) -> int:
        return len(self.results)

    @property
    def total_valid(self) -> int:
        return sum(1 for r in self.results if r.status == AuditStatus.VALID)

    @property
    def total_invalid(self) -> int:
        return sum(1 for r in self.results if r.status in (AuditStatus.INVALID, AuditStatus.ERROR))

    def to_table_rows(self) -> List[tuple[str, str, str]]:
        return [r.to_table_row() for r in self.results]



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

    def audit_settings(self) -> CategoryAuditResult:
        settings_path = self.gemini_root / "antigravity-cli" / "settings.json"
        if not settings_path.exists():
            return CategoryAuditResult(
                category="Settings",
                status=AuditStatus.SKIPPED,
                path=str(settings_path),
                details=f"File not found: {settings_path}",
            )
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            SettingsSchema.model_validate(data)
            return CategoryAuditResult(
                category="Settings",
                status=AuditStatus.VALID,
                path=str(settings_path),
                details=f"{str(settings_path)} ({len(data)} keys validated)",
                valid_count=1,
            )
        except Exception as e:
            return CategoryAuditResult(
                category="Settings",
                status=AuditStatus.INVALID,
                path=str(settings_path),
                details=f"Error: {e}",
                invalid_count=1,
                sample_errors=[str(e)],
            )

    def audit_mcp_configs(self) -> List[CategoryAuditResult]:
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
                    results.append(
                        CategoryAuditResult(
                            category="MCP Config",
                            status=AuditStatus.VALID,
                            path=str(p),
                            details=str(p),
                            valid_count=1,
                        )
                    )
                except Exception as e:
                    results.append(
                        CategoryAuditResult(
                            category="MCP Config",
                            status=AuditStatus.INVALID,
                            path=str(p),
                            details=f"Error: {e}",
                            invalid_count=1,
                            sample_errors=[str(e)],
                        )
                    )
        return results

    def _audit_frontmatters(self, category: str, directory: Path, pattern: str, model_cls: Any) -> CategoryAuditResult:
        if not directory.exists():
            return CategoryAuditResult(
                category=category,
                status=AuditStatus.SKIPPED,
                path=str(directory),
                details=f"Directory not found: {directory}",
            )

        md_files = list(directory.glob(pattern))
        valid_count = 0
        invalid_count = 0
        errors = []

        for md_file in md_files:
            try:
                frontmatter = parse_frontmatter(md_file.read_text(encoding="utf-8"))
                model_cls.model_validate(frontmatter)
                valid_count += 1
            except Exception as e:
                invalid_count += 1
                errors.append(f"{md_file.name}: {e}")

        status = AuditStatus.VALID if invalid_count == 0 else AuditStatus.INVALID
        return CategoryAuditResult(
            category=category,
            status=status,
            path=str(directory),
            details=f"{valid_count}/{len(md_files)} {category.lower()} valid",
            valid_count=valid_count,
            invalid_count=invalid_count,
            sample_errors=errors[:3],
        )

    def audit_skills(self) -> CategoryAuditResult:
        return self._audit_frontmatters("Skills", self.gemini_root / "config" / "skills", "**/SKILL.md", SkillFrontmatterSchema)

    def audit_agents(self) -> CategoryAuditResult:
        return self._audit_frontmatters("Agents", self.gemini_root / "config" / "agents", "*.md", AgentFrontmatterSchema)

    def audit_transcripts(self, max_files: int = 5) -> List[CategoryAuditResult]:
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

                status = AuditStatus.VALID if invalid_steps == 0 else AuditStatus.INVALID
                details = f"{t_file} ({valid_steps} valid steps, {invalid_steps} errors)"
                results.append(
                    CategoryAuditResult(
                        category="Transcript",
                        status=status,
                        path=str(t_file),
                        details=details,
                        valid_count=valid_steps,
                        invalid_count=invalid_steps,
                        sample_errors=errors[:3],
                    )
                )
            except Exception as file_err:
                results.append(
                    CategoryAuditResult(
                        category="Transcript",
                        status=AuditStatus.ERROR,
                        path=str(t_file),
                        details=f"File error: {file_err}",
                        sample_errors=[str(file_err)],
                    )
                )
        return results

    def run_full_audit(self) -> AuditReport:
        results: List[CategoryAuditResult] = []

        # Settings
        results.append(self.audit_settings())

        # MCP
        results.extend(self.audit_mcp_configs())

        # Skills & Agents
        results.append(self.audit_skills())
        results.append(self.audit_agents())

        # Transcripts
        results.extend(self.audit_transcripts())

        return AuditReport(results=results)
