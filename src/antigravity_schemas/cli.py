"""
CLI Command Entrypoint for antigravity-schemas (agy-schema).
Commands:
  export   - Export JSON Schema files to output directory
  audit    - Audit local ~/.gemini config and transcript files
  validate - Validate a specific JSON/YAML file against target model
  sync-doc - Check sync status between models, exported schemas, and research reference doc
"""

import sys
import json
import argparse
from pathlib import Path
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .exporter import export_all_schemas
from .auditor import SystemAuditor, parse_frontmatter
from .models import (
    SettingsSchema,
    PluginManifestSchema,
    AgentFrontmatterSchema,
    SkillFrontmatterSchema,
    MCPConfigSchema,
    HooksConfigSchema,
    TranscriptStepSchema,
    KeybindingsSchema,
    StatusLinePayloadSchema,
)

console = Console()

MODEL_MAPPING = {
    "settings": SettingsSchema,
    "plugin": PluginManifestSchema,
    "agent": AgentFrontmatterSchema,
    "skill": SkillFrontmatterSchema,
    "mcp": MCPConfigSchema,
    "hooks": HooksConfigSchema,
    "transcript": TranscriptStepSchema,
    "keybindings": KeybindingsSchema,
    "status_line": StatusLinePayloadSchema,
}


def handle_export(args):
    output_dir = Path(args.output)
    console.print(f"[bold blue]Exporting JSON Schemas to:[/bold blue] {output_dir.resolve()}")
    exported = export_all_schemas(output_dir)
    for name, path in exported.items():
        console.print(f"  [green]✓[/green] Exported [bold]{name}[/bold] -> {path}")
    console.print("[bold green]All schemas exported successfully![/bold green]")


def handle_audit(args):
    gemini_root = Path(args.root)
    console.print(f"[bold blue]Running System Audit on:[/bold blue] {gemini_root.resolve()}\n")
    auditor = SystemAuditor(gemini_root=gemini_root)
    report = auditor.run_full_audit()

    table = Table(title="Antigravity System Audit Report", show_lines=True)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Path / Details", style="white")

    # Settings
    s = report["settings"]
    status_style = "green" if s.get("status") == "VALID" else ("yellow" if s.get("status") == "SKIPPED" else "red")
    table.add_row("Settings", f"[{status_style}]{s.get('status')}[/{status_style}]", s.get("path") or s.get("message"))

    # MCP
    for m in report["mcp_configs"]:
        m_style = "green" if m.get("status") == "VALID" else "red"
        table.add_row("MCP Config", f"[{m_style}]{m.get('status')}[/{m_style}]", m.get("path"))

    # Skills summary
    skills = report["skills"]
    valid_skills = sum(1 for sk in skills if sk["status"] == "VALID")
    table.add_row("Skills", f"[green]VALID ({valid_skills}/{len(skills)})[/green]", f"{len(skills)} SKILL.md files audited")

    # Agents summary
    agents = report["agents"]
    valid_agents = sum(1 for ag in agents if ag["status"] == "VALID")
    table.add_row("Agents", f"[green]VALID ({valid_agents}/{len(agents)})[/green]", f"{len(agents)} agent frontmatters audited")

    # Transcripts
    transcripts = report["transcripts"]
    for tr in transcripts:
        t_style = "green" if tr.get("status") == "VALID" else "red"
        details = f"{tr.get('valid_steps', 0)} valid steps, {tr.get('invalid_steps', 0)} errors"
        table.add_row("Transcript", f"[{t_style}]{tr.get('status')}[/{t_style}]", f"{tr.get('path')} ({details})")

    console.print(table)


def handle_validate(args):
    file_path = Path(args.file)
    model_name = args.type.lower()

    if model_name not in MODEL_MAPPING:
        console.print(f"[bold red]Error:[/bold red] Unknown target schema type '{model_name}'. Options: {list(MODEL_MAPPING.keys())}")
        sys.exit(1)

    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        sys.exit(1)

    model_cls = MODEL_MAPPING[model_name]
    content = file_path.read_text(encoding="utf-8")

    try:
        if file_path.suffix in [".yaml", ".yml"] or model_name in ["agent", "skill"]:
            data = parse_frontmatter(content) if model_name in ["agent", "skill"] else yaml.safe_load(content)
        else:
            data = json.loads(content)

        model_cls.model_validate(data)
        console.print(Panel(f"[bold green]Validation Successful![/bold green]\nFile: {file_path}\nSchema: {model_cls.__name__}", title="Success", border_style="green"))
    except Exception as e:
        console.print(Panel(f"[bold red]Validation Failed![/bold red]\nFile: {file_path}\nError: {e}", title="Error", border_style="red"))
        sys.exit(1)


def handle_sync_doc(args):
    doc_path = Path(args.doc)
    schemas_dir = Path(args.schemas_dir)

    console.print(f"[bold blue]Checking Sync Status between Models, Schemas, and Doc:[/bold blue] {doc_path.name}\n")

    if not doc_path.exists():
        console.print(f"[bold red]Error:[/bold red] Reference document not found at {doc_path}")
        sys.exit(1)

    doc_text = doc_path.read_text(encoding="utf-8")

    table = Table(title="Spec & Code Synchronization Status", show_lines=True)
    table.add_column("Schema Model", style="cyan", no_wrap=True)
    table.add_column("JSON Schema File", style="magenta")
    table.add_column("Doc References", style="white")
    table.add_column("Sync Status", style="bold")

    from .exporter import SCHEMA_MAPPING as EXPORT_SCHEMA_MAPPING
    reverse_mapping = {model_cls: name for name, model_cls in EXPORT_SCHEMA_MAPPING.items()}

    for key, model_cls in MODEL_MAPPING.items():
        schema_file_name = reverse_mapping.get(model_cls, f"{key}.schema.json")
        schema_file_path = schemas_dir / schema_file_name
        has_schema_file = schema_file_path.exists()

        # Check model field coverage in doc
        if hasattr(model_cls, "model_fields"):
            fields = list(model_cls.model_fields.keys())
        elif hasattr(model_cls, "__fields__"):
            fields = list(model_cls.__fields__.keys())
        else:
            fields = []

        documented_count = sum(1 for f in fields if f in doc_text)
        coverage_pct = (documented_count / len(fields) * 100) if fields else 100.0

        status = "SYNCED" if has_schema_file and coverage_pct > 70 else "OUT OF SYNC"
        status_style = "green" if status == "SYNCED" else "yellow"

        table.add_row(
            model_cls.__name__,
            f"✓ {schema_file_name}" if has_schema_file else "✗ Missing",
            f"{documented_count}/{len(fields)} fields in doc ({coverage_pct:.0f}%)",
            f"[{status_style}]{status}[/{status_style}]"
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Antigravity Schemas CLI Utility (agy-schema)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export command
    p_export = subparsers.add_parser("export", help="Export JSON Schemas to directory")
    p_export.add_argument("-o", "--output", default="schemas", help="Output directory path (default: schemas)")
    p_export.set_defaults(func=handle_export)

    # Audit command
    p_audit = subparsers.add_parser("audit", help="Audit local ~/.gemini installation")
    p_audit.add_argument("-r", "--root", default=str(Path.home() / ".gemini"), help="Gemini config root path")
    p_audit.set_defaults(func=handle_audit)

    # Validate command
    p_validate = subparsers.add_parser("validate", help="Validate a file against a target schema")
    p_validate.add_argument("file", help="Path to JSON or Markdown file to validate")
    p_validate.add_argument("-t", "--type", required=True, help=f"Schema type: {', '.join(MODEL_MAPPING.keys())}")
    p_validate.set_defaults(func=handle_validate)

    # Sync-doc command
    p_sync = subparsers.add_parser("sync-doc", help="Check synchronization between code models, exported schemas, and reference document")
    p_sync.add_argument("-d", "--doc", default="antigravity-cli-reference.md", help="Path to reference markdown document")
    p_sync.add_argument("-s", "--schemas-dir", default="schemas", help="Directory containing exported JSON Schemas")
    p_sync.set_defaults(func=handle_sync_doc)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
