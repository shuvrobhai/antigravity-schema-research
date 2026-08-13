"""
Sample Python script demonstrating how external tools and plugins can import
`antigravity_schemas` as a library to validate configurations, custom agents,
status line IPC payloads, and session trajectory transcripts.
"""

import json
from pathlib import Path
from antigravity_schemas.models import (
    SettingsSchema,
    MasterConfigSchema,
    AgentFrontmatterSchema,
    SkillFrontmatterSchema,
    MCPConfigSchema,
    StatusLinePayloadSchema,
    TranscriptStepSchema,
)
from antigravity_schemas.auditor import SystemAuditor, parse_frontmatter
from antigravity_schemas.exporter import export_all_schemas


def example_1_validate_settings():
    """Example 1: Validating CLI settings dictionary programmatically."""
    print("--- Example 1: Settings Validation ---")
    raw_settings = {
        "toolPermission": "request-review",
        "artifactReviewPolicy": "asks-for-review",
        "enableTerminalSandbox": False,
        "trustedWorkspaces": ["/Users/developer/project"],
        "colorScheme": "terminal",
        "model": "Gemini 3.5 Flash (Low)"
    }

    # Validate dictionary against SettingsSchema model
    settings_model = SettingsSchema.model_validate(raw_settings)
    print(f"✓ Valid Settings Object: model={settings_model.model}, sandbox={settings_model.enableTerminalSandbox}\n")


def example_2_parse_and_validate_agent():
    """Example 2: Extracting and validating YAML frontmatter from a Custom Agent markdown file."""
    print("--- Example 2: Agent Frontmatter Parsing & Validation ---")
    agent_markdown = """---
name: code-auditor
description: Specialized subagent for security audits and code quality reviews.
tools:
  - view_file
  - grep_search
  - run_command
model: pro
commandExecutionPolicy: sandbox
---

# System Prompt
You are an expert security auditor.
"""

    # Extract frontmatter dictionary
    frontmatter_dict = parse_frontmatter(agent_markdown)

    # Validate against AgentFrontmatterSchema
    agent_model = AgentFrontmatterSchema.model_validate(frontmatter_dict)
    print(f"✓ Parsed Agent: name={agent_model.name}, model={agent_model.model}, tools={agent_model.tools}\n")


def example_3_validate_status_line_payload():
    """Example 3: Validating stdin payload in a custom status line hook script."""
    print("--- Example 3: Status Line Payload Validation ---")
    incoming_payload = {
        "cwd": "/Users/developer/project",
        "session_id": "c4cd42bc-7808-44de-af5d-2d77b6acae50",
        "version": "1.1.11",
        "context_window": {
            "used_percentage": 24.5,
            "total_input_tokens": 49000
        },
        "agent_state": "working",
        "terminal_width": 120
    }

    payload_model = StatusLinePayloadSchema.model_validate(incoming_payload)
    print(f"✓ Status Line Payload: state={payload_model.agent_state}, cwd={payload_model.cwd}\n")


def example_4_programmatic_system_audit():
    """Example 4: Running a full programmatic audit against ~/.gemini installation."""
    print("--- Example 4: Programmatic System Audit ---")
    auditor = SystemAuditor()
    report = auditor.run_full_audit()

    print(f"✓ Audit Settings Status: {report['settings']['status']}")
    print(f"✓ Skills Audited: {len(report['skills'])} valid SKILL.md files")
    print(f"✓ Transcripts Audited: {len(report['transcripts'])} sessions scanned\n")


def example_5_export_custom_schema():
    """Example 5: Generating JSON Schema dictionary from Pydantic model."""
    print("--- Example 5: Generating JSON Schema Dictionary ---")
    mcp_schema_dict = MCPConfigSchema.model_json_schema()
    print(f"✓ MCP Config JSON Schema Title: {mcp_schema_dict.get('title')}")
    print(f"✓ Properties count: {len(mcp_schema_dict.get('properties', {}))}\n")


def main():
    print("=================================================================")
    print("      Antigravity Schemas Python Library Usage Demonstration     ")
    print("=================================================================\n")

    example_1_validate_settings()
    example_2_parse_and_validate_agent()
    example_3_validate_status_line_payload()
    example_4_programmatic_system_audit()
    example_5_export_custom_schema()

    print("All library usage examples executed cleanly!")


if __name__ == "__main__":
    main()
