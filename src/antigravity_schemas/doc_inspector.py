"""
AST-Aware Markdown Document Section Parser and Spec-Sync Inspector.
Extracts schema sections from Markdown reference guides and verifies field-level documentation coverage in context.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Optional

from .registry import registry, SchemaDescriptor


@dataclass
class DocSection:
    title: str
    content: str
    documented_fields: Set[str] = field(default_factory=set)


@dataclass
class SchemaSyncResult:
    descriptor: SchemaDescriptor
    section_found: bool
    schema_file_exists: bool
    total_fields: int
    documented_fields: List[str]
    missing_fields: List[str]
    coverage_pct: float

    @property
    def is_synced(self) -> bool:
        return self.schema_file_exists and self.section_found and self.coverage_pct >= 50.0



class MarkdownSectionParser:
    """Parses markdown files into contextual sections and extracts documented field names."""

    @staticmethod
    def parse_sections(markdown_text: str) -> List[DocSection]:
        sections: List[DocSection] = []
        current_title = "Header"
        current_lines: List[str] = []

        for line in markdown_text.splitlines():
            if line.startswith("### ") or line.startswith("## "):
                if current_lines:
                    content = "\n".join(current_lines)
                    sections.append(
                        DocSection(
                            title=current_title,
                            content=content,
                            documented_fields=MarkdownSectionParser.extract_fields(content),
                        )
                    )
                current_title = line.lstrip("#").strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            content = "\n".join(current_lines)
            sections.append(
                DocSection(
                    title=current_title,
                    content=content,
                    documented_fields=MarkdownSectionParser.extract_fields(content),
                )
            )

        return sections

    @staticmethod
    def extract_fields(section_content: str) -> Set[str]:
        """Extracts field names enclosed in backticks from markdown table rows or text."""
        fields = set()
        for line in section_content.splitlines():
            if "|" in line:
                # Extract first code-formatted column in table row: | `field_name` | ... |
                matches = re.findall(r"`([a-zA-Z0-9_\$]+)`", line)
                if matches:
                    fields.add(matches[0])
            else:
                # Also capture bullet points like: - `field_name`: description
                matches = re.findall(r"^[\s\*\-]+\`([a-zA-Z0-9_\$]+)\`", line)
                for m in matches:
                    fields.add(m)
        return fields


class DocSyncInspector:
    """Context-aware specification synchronization inspector."""

    def __init__(self, doc_path: Path, schemas_dir: Path):
        self.doc_path = doc_path
        self.schemas_dir = schemas_dir

    def inspect(self) -> List[SchemaSyncResult]:
        if not self.doc_path.exists():
            raise FileNotFoundError(f"Reference document not found: {self.doc_path}")

        doc_text = self.doc_path.read_text(encoding="utf-8")
        sections = MarkdownSectionParser.parse_sections(doc_text)
        results: List[SchemaSyncResult] = []

        for desc in registry.all_descriptors():
            model_cls = desc.model_cls
            schema_file_path = self.schemas_dir / desc.filename
            has_schema_file = schema_file_path.exists()

            # Find matching section in markdown document
            matching_section: Optional[DocSection] = None
            for sec in sections:
                if model_cls.__name__ in sec.title or desc.key in sec.title.lower():
                    matching_section = sec
                    break

            if hasattr(model_cls, "model_fields"):
                model_fields = list(model_cls.model_fields.keys())
            elif hasattr(model_cls, "__fields__"):
                model_fields = list(model_cls.__fields__.keys())
            else:
                model_fields = []

            documented: List[str] = []
            missing: List[str] = []

            if matching_section:
                for f in model_fields:
                    if f in matching_section.documented_fields or f in matching_section.content:
                        documented.append(f)
                    else:
                        missing.append(f)
            else:
                missing = list(model_fields)

            total = len(model_fields)
            coverage = (len(documented) / total * 100.0) if total > 0 else 100.0

            results.append(
                SchemaSyncResult(
                    descriptor=desc,
                    section_found=matching_section is not None,
                    schema_file_exists=has_schema_file,
                    total_fields=total,
                    documented_fields=documented,
                    missing_fields=missing,
                    coverage_pct=coverage,
                )
            )

        return results
