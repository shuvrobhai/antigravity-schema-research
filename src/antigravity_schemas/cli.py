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

from .registry import registry
from .exporter import export_all_schemas
from .auditor import SystemAuditor, parse_frontmatter
from .doc_inspector import DocSyncInspector

console = Console()

# Unified model mapping from SchemaRegistry
MODEL_MAPPING = registry.model_mapping()


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

    # Delegate table row formatting directly to AuditReport domain model
    for row in report.to_table_rows():
        table.add_row(*row)

    console.print(table)


def handle_validate(args):
    file_path = Path(args.file)
    model_name = args.type.lower()

    descriptor = registry.get(model_name)
    if not descriptor:
        console.print(f"[bold red]Error:[/bold red] Unknown target schema type '{model_name}'. Options: {list(MODEL_MAPPING.keys())}")
        sys.exit(1)

    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        sys.exit(1)

    model_cls = descriptor.model_cls
    content = file_path.read_text(encoding="utf-8")

    try:
        if file_path.suffix in [".yaml", ".yml"] or model_name in ["agent", "skill"]:
            data = parse_frontmatter(content) if model_name in ["agent", "skill"] else yaml.safe_load(content)
        else:
            data = json.loads(content)

        model_cls.model_validate(data)
        console.print(Panel(f"[bold green]Validation Successful![/bold green]\nFile: {file_path}\nSchema: {model_cls.__name__} ({descriptor.category})", title="Success", border_style="green"))
    except Exception as e:
        console.print(Panel(f"[bold red]Validation Failed![/bold red]\nFile: {file_path}\nError: {e}", title="Error", border_style="red"))
        sys.exit(1)


def handle_sync_doc(args):
    doc_path = Path(args.doc)
    schemas_dir = Path(args.schemas_dir)

    if not doc_path.exists() and Path("SCHEMA_REFERENCE.md").exists():
        doc_path = Path("SCHEMA_REFERENCE.md")

    console.print(f"[bold blue]Checking Contextual Sync Status against Doc:[/bold blue] {doc_path.name}\n")

    if not doc_path.exists():
        console.print(f"[bold red]Error:[/bold red] Reference document not found at {doc_path}")
        sys.exit(1)

    inspector = DocSyncInspector(doc_path=doc_path, schemas_dir=schemas_dir)
    results = inspector.inspect()

    table = Table(title="Spec & Code Contextual Sync Status", show_lines=True)
    table.add_column("Schema Model", style="cyan", no_wrap=True)
    table.add_column("JSON Schema File", style="magenta")
    table.add_column("Doc References", style="white")
    table.add_column("Sync Status", style="bold")

    out_of_sync_items = []

    for r in results:
        desc = r.descriptor
        status_text = "SYNCED" if r.is_synced else "OUT OF SYNC"
        status_style = "green" if r.is_synced else "yellow"

        table.add_row(
            desc.model_cls.__name__,
            f"✓ {desc.filename}" if r.schema_file_exists else "✗ Missing",
            f"{len(r.documented_fields)}/{r.total_fields} fields ({r.coverage_pct:.0f}%)",
            f"[{status_style}]{status_text}[/{status_style}]"
        )

        if not r.is_synced and r.missing_fields:
            out_of_sync_items.append(f"[bold]{desc.model_cls.__name__}[/bold]: missing fields -> {r.missing_fields}")

    console.print(table)

    if out_of_sync_items:
        console.print("\n", Panel("\n".join(out_of_sync_items), title="[bold yellow]Contextual Missing Fields Details[/bold yellow]", border_style="yellow"))


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
    p_sync.add_argument("-d", "--doc", default="SCHEMA_REFERENCE.md", help="Path to reference markdown document (default: SCHEMA_REFERENCE.md)")
    p_sync.add_argument("-s", "--schemas-dir", default="schemas", help="Directory containing exported JSON Schemas")
    p_sync.set_defaults(func=handle_sync_doc)

    args = parser.parse_args()
    args.func(args)



if __name__ == "__main__":
    main()
