# Antigravity Schemas (`antigravity-schemas`)

An automated schema extraction, validation, and auditing toolkit for the **Google Antigravity CLI and IDE** ecosystem, built from empirical trajectory audits and source documentation in [`antigravity-cli-reference.md`](file:///Users/rayhanislamshuvro/Developer/antigravity-schema-research/antigravity-cli-reference.md).

## Features

- **Pydantic v2 Models**: Formal schema definitions for all 9 core configuration & runtime schemas.
- **JSON Schema Exporter**: Export standard `.json` schemas to `schemas/` directory.
- **Live System Auditor**: Inspect local `~/.gemini/` configuration files, skills, custom agents, MCP servers, and brain transcripts in real time.
- **CLI Validator**: Validate local `.json` or `.md` files directly against target models.

## Installation & Setup

```bash
# Clone and setup with Python 3.10+
pip install -e .
```

## CLI Usage (`agy-schema`)

### 1. Export JSON Schemas
Export standard JSON schemas for all 9 models into the `schemas/` directory:

```bash
agy-schema export -o schemas
```

### 2. Run Live System Audit
Audit your local `~/.gemini/` installation and brain transcripts against formal schemas:

```bash
agy-schema audit
```

### 3. Validate Specific File
Validate a settings file or custom agent frontmatter:

```bash
agy-schema validate ~/.gemini/antigravity-cli/settings.json -t settings
agy-schema validate ~/.gemini/config/agents/code-auditor.md -t agent
```

## Python Library Usage

External Python tools, plugins, and custom hooks can import `antigravity_schemas` directly:

```python
from antigravity_schemas.models import SettingsSchema, AgentFrontmatterSchema, StatusLinePayloadSchema
from antigravity_schemas.auditor import parse_frontmatter

# Validate settings dictionary
settings = SettingsSchema.model_validate(raw_json_dict)

# Extract and validate Custom Agent frontmatter
agent_data = parse_frontmatter(agent_markdown_content)
agent = AgentFrontmatterSchema.model_validate(agent_data)
```

See [`examples/library_usage.py`](file:///Users/rayhanislamshuvro/Developer/antigravity-schema-research/examples/library_usage.py) for complete runnable examples.

## Supported Schemas (13 Core Ecosystem Schemas)

1. `settings` (`settings.json`) - Global and workspace CLI settings
2. `plugin` (`plugin.json`) - Plugin package manifest
3. `agent` (`agent.md` frontmatter) - Custom subagent YAML frontmatter
4. `skill` (`SKILL.md` frontmatter) - Skill YAML frontmatter
5. `mcp` (`mcp_config.json`) - Model Context Protocol servers
6. `hooks` (`hooks.json`) - Execution lifecycle hooks
7. `transcript` (`transcript.jsonl`) - Session trajectory log steps
8. `keybindings` (`keybindings.json`) - TUI hotkey mappings
9. `status_line` (`status_line.json`) - Custom status line IPC stdin payload
10. `master_config` (`config.json`) - Master extensibility configuration
11. `projects` (`projects.json`) - Global workspace directory index
12. `desktop_state` (`antigravity_state.pbtxt`) - Antigravity 2.0 Desktop app state
13. `ide_state` (`~/.gemini/antigravity-ide/`) - Antigravity IDE state

## Testing

Run unit tests using Python's standard library test runner:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
