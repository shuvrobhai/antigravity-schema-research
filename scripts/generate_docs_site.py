"""
Script to generate an interactive single-page HTML documentation site and JSON Schema Catalog for Google Antigravity.
"""

import json
from pathlib import Path

SCHEMAS_DIR = Path("schemas")
OUTPUT_HTML = Path("docs/index.html")

SCHEMA_METADATA = {
    "settings.schema.json": {
        "title": "Settings Schema",
        "category": "CLI",
        "model": "SettingsSchema",
        "target": "~/.gemini/antigravity-cli/settings.json",
        "description": "Global and workspace user settings, editor preferences, sandbox policies, color schemes, and permission defaults for Antigravity CLI."
    },
    "plugin.schema.json": {
        "title": "Plugin Manifest Schema",
        "category": "Shared Core",
        "model": "PluginManifestSchema",
        "target": "plugins/<name>/plugin.json",
        "description": "Manifest specification for bundled Antigravity plugins containing skills, rules, MCP servers, subagents, and lifecycle hooks."
    },
    "agent.schema.json": {
        "title": "Agent Frontmatter Schema",
        "category": "Shared Core",
        "model": "AgentFrontmatterSchema",
        "target": ".agents/agents/<name>.md",
        "description": "YAML frontmatter specification for custom persona subagents defining model tiers, execution policies, tool lists, and skills."
    },
    "skill.schema.json": {
        "title": "Skill Frontmatter Schema",
        "category": "Shared Core",
        "model": "SkillFrontmatterSchema",
        "target": ".agents/skills/<name>/SKILL.md",
        "description": "YAML frontmatter specification for on-demand skill activation and intent trigger descriptions."
    },
    "mcp_config.schema.json": {
        "title": "MCP Server Config Schema",
        "category": "Shared Core",
        "model": "MCPConfigSchema",
        "target": "~/.gemini/config/mcp_config.json",
        "description": "Model Context Protocol (MCP) server bindings for Stdio executables and Remote HTTP/SSE server endpoints."
    },
    "hooks.schema.json": {
        "title": "Lifecycle Hooks Schema",
        "category": "Shared Core",
        "model": "HooksConfigSchema",
        "target": "~/.gemini/config/hooks.json",
        "description": "Lifecycle event interceptors (PreToolUse, PostToolUse, PreInvocation, PostInvocation, Stop) for automated quality gates."
    },
    "transcript_step.schema.json": {
        "title": "Transcript Step Schema",
        "category": "Runtime",
        "model": "TranscriptStepSchema",
        "target": "brain/<id>/.system_generated/logs/transcript.jsonl",
        "description": "Individual step log event schema for session trajectory transcripts recording prompt inputs, tool calls, and model outputs."
    },
    "keybindings.schema.json": {
        "title": "Keybindings Schema",
        "category": "CLI",
        "model": "KeybindingsSchema",
        "target": "~/.gemini/antigravity-cli/keybindings.json",
        "description": "TUI hotkey overrides mapping user actions (cli.escape, prompt.submit, etc.) to keyboard combinations."
    },
    "status_line.schema.json": {
        "title": "Status Line Payload Schema",
        "category": "CLI",
        "model": "StatusLinePayloadSchema",
        "target": "Status line script stdin IPC payload",
        "description": "JSON payload streamed via stdin to custom terminal status line scripts containing token usage, VCS branch, and agent state."
    },
    "master_config.schema.json": {
        "title": "Master Config Schema",
        "category": "Shared Core",
        "model": "MasterConfigSchema",
        "target": "~/.gemini/config/config.json",
        "description": "Master extensibility manifest managing plugin activation states, global permission grants (allow/deny rules), and browser policies."
    },
    "projects.schema.json": {
        "title": "Projects Index Schema",
        "category": "Shared Core",
        "model": "ProjectsIndexSchema",
        "target": "~/.gemini/projects.json",
        "description": "Global directory index mapping absolute local repository paths to project aliases."
    },
    "desktop_state.schema.json": {
        "title": "Desktop App State Schema",
        "category": "Desktop 2.0",
        "model": "DesktopStateSchema",
        "target": "~/.gemini/antigravity/antigravity_state.pbtxt",
        "description": "Antigravity 2.0 Desktop standalone application state tracking onboarding completion, acknowledged NUX popups, and database migrations."
    },
    "ide_state.schema.json": {
        "title": "IDE State Schema",
        "category": "IDE",
        "model": "IDEStateSchema",
        "target": "~/.gemini/antigravity-ide/",
        "description": "Antigravity IDE (VS Code fork) state tracking active conversation databases, HTML UI artifacts, and browser session playback recordings."
    }
}


def build_docs():
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    schemas_data = {}

    for file_name, meta in SCHEMA_METADATA.items():
        file_path = SCHEMAS_DIR / file_name
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                schema_json = json.load(f)
            schemas_data[file_name] = {
                **meta,
                "file_name": file_name,
                "json_schema": schema_json
            }

    data_json_str = json.dumps(schemas_data, indent=2)

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Antigravity Schema Catalog & Developer Specs</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0b0f19;
            --bg-surface: #131b2e;
            --bg-card: #182238;
            --bg-hover: #1e2c4a;
            --border-color: #243456;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-primary);
            color: var(--text-main);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 10;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-logo {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.1rem;
            color: #fff;
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .badge-version {
            background: rgba(59, 130, 246, 0.15);
            color: var(--accent-blue);
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .search-box {
            position: relative;
            width: 320px;
        }

        .search-input {
            width: 100%;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.6rem 1rem 0.6rem 2.5rem;
            color: var(--text-main);
            font-family: var(--font-sans);
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }

        .search-icon {
            position: absolute;
            left: 0.85rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            pointer-events: none;
        }

        .app-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        sidebar {
            width: 320px;
            background: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        .category-filter {
            padding: 1rem;
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            border-bottom: 1px solid var(--border-color);
        }

        .filter-btn {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .filter-btn:hover, .filter-btn.active {
            background: var(--accent-blue);
            color: #fff;
            border-color: var(--accent-blue);
        }

        .schema-list {
            list-style: none;
            padding: 0.5rem;
        }

        .schema-item {
            padding: 0.85rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 0.25rem;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }

        .schema-item:hover {
            background: var(--bg-hover);
        }

        .schema-item.active {
            background: var(--bg-card);
            border-color: var(--accent-blue);
        }

        .schema-item-title {
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .schema-item-cat {
            font-size: 0.7rem;
            color: var(--text-dim);
            font-family: var(--font-mono);
        }

        main {
            flex: 1;
            background: var(--bg-primary);
            overflow-y: auto;
            padding: 2rem 3rem;
        }

        .doc-header {
            margin-bottom: 2rem;
        }

        .doc-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.5rem;
        }

        .doc-description {
            font-size: 1.05rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 2.5rem;
        }

        .meta-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            margin-bottom: 0.3rem;
            font-weight: 700;
        }

        .meta-value {
            font-family: var(--font-mono);
            font-size: 0.875rem;
            color: var(--accent-cyan);
            word-break: break-all;
        }

        .section-heading {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .fields-table {
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-surface);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            margin-bottom: 2.5rem;
        }

        .fields-table th, .fields-table td {
            padding: 1rem 1.25rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .fields-table th {
            background: var(--bg-card);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            font-weight: 700;
        }

        .field-name {
            font-family: var(--font-mono);
            font-weight: 600;
            color: var(--accent-blue);
            font-size: 0.9rem;
        }

        .field-type {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--accent-amber);
            background: rgba(245, 158, 11, 0.1);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
        }

        .field-desc {
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.5;
        }

        .code-container {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }

        .code-header {
            background: var(--bg-card);
            padding: 0.75rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.85rem;
            font-family: var(--font-mono);
            color: var(--text-muted);
        }

        .copy-btn {
            background: var(--bg-hover);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .copy-btn:hover {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
        }

        pre {
            padding: 1.25rem;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            color: #e2e8f0;
            overflow-x: auto;
            max-height: 450px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="brand-logo">G</div>
            <div class="brand-title">Google Antigravity Schema Catalog</div>
            <span class="badge-version">v0.2.0 Full Ecosystem</span>
        </div>
        <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input type="text" id="searchInput" class="search-input" placeholder="Search schemas or fields...">
        </div>
    </header>

    <div class="app-container">
        <sidebar>
            <div class="category-filter">
                <button class="filter-btn active" data-cat="ALL">All (13)</button>
                <button class="filter-btn" data-cat="Shared Core">Shared Core</button>
                <button class="filter-btn" data-cat="CLI">CLI</button>
                <button class="filter-btn" data-cat="Desktop 2.0">Desktop 2.0</button>
                <button class="filter-btn" data-cat="IDE">IDE</button>
                <button class="filter-btn" data-cat="Runtime">Runtime</button>
            </div>
            <ul class="schema-list" id="schemaList"></ul>
        </sidebar>

        <main id="mainContent">
            <!-- Dynamic Schema Rendered Here -->
        </main>
    </div>

    <script>
        const SCHEMAS_DATA = """ + data_json_str + """;
        let activeSchemaKey = Object.keys(SCHEMAS_DATA)[0];

        function renderSidebar(filterCat = 'ALL', search = '') {
            const listEl = document.getElementById('schemaList');
            listEl.innerHTML = '';

            Object.entries(SCHEMAS_DATA).forEach(([key, item]) => {
                if (filterCat !== 'ALL' && item.category !== filterCat) return;
                if (search && !item.title.toLowerCase().includes(search.toLowerCase()) && !item.description.toLowerCase().includes(search.toLowerCase())) return;

                const li = document.createElement('li');
                li.className = 'schema-item ' + (key === activeSchemaKey ? 'active' : '');
                li.onclick = () => selectSchema(key);
                li.innerHTML = `
                    <div class="schema-item-title">
                        ${item.title}
                        <span class="schema-item-cat">${item.category}</span>
                    </div>
                `;
                listEl.appendChild(li);
            });
        }

        function selectSchema(key) {
            activeSchemaKey = key;
            renderSidebar(document.querySelector('.filter-btn.active').dataset.cat, document.getElementById('searchInput').value);
            renderMainContent();
        }

        function renderMainContent() {
            const item = SCHEMAS_DATA[activeSchemaKey];
            if (!item) return;

            const schemaObj = item.json_schema;
            const properties = schemaObj.properties || {};

            let fieldsRows = '';
            Object.entries(properties).forEach(([fieldName, prop]) => {
                fieldsRows += `
                    <tr>
                        <td class="field-name">${fieldName}</td>
                        <td><span class="field-type">${prop.type || (prop.$ref ? '$ref' : 'any')}</span></td>
                        <td class="field-desc">${prop.description || '—'}</td>
                    </tr>
                `;
            });

            const mainEl = document.getElementById('mainContent');
            mainEl.innerHTML = `
                <div class="doc-header">
                    <h1 class="doc-title">${item.title}</h1>
                    <p class="doc-description">${item.description}</p>
                </div>

                <div class="meta-grid">
                    <div>
                        <div class="meta-label">Category</div>
                        <div class="meta-value" style="color: var(--accent-amber);">${item.category}</div>
                    </div>
                    <div>
                        <div class="meta-label">Pydantic v2 Model</div>
                        <div class="meta-value">${item.model}</div>
                    </div>
                    <div>
                        <div class="meta-label">Target Location / Payload</div>
                        <div class="meta-value">${item.target}</div>
                    </div>
                    <div>
                        <div class="meta-label">Schema File</div>
                        <div class="meta-value">${item.file_name}</div>
                    </div>
                </div>

                <h2 class="section-heading">Properties Breakdown</h2>
                <table class="fields-table">
                    <thead>
                        <tr>
                            <th>Field Name</th>
                            <th>Data Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${fieldsRows || '<tr><td colspan="3" style="text-align:center; color: var(--text-dim);">Root Model (No nested top-level properties)</td></tr>'}
                    </tbody>
                </table>

                <h2 class="section-heading">Standalone JSON Schema (.json)</h2>
                <div class="code-container">
                    <div class="code-header">
                        <span>${item.file_name}</span>
                        <button class="copy-btn" onclick="copySchemaJson()">Copy JSON</button>
                    </div>
                    <pre><code id="jsonCode">${JSON.stringify(schemaObj, null, 2)}</code></pre>
                </div>
            `;
        }

        function copySchemaJson() {
            const codeText = document.getElementById('jsonCode').innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                alert('JSON Schema copied to clipboard!');
            });
        }

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.onclick = (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                renderSidebar(e.target.dataset.cat, document.getElementById('searchInput').value);
            };
        });

        document.getElementById('searchInput').oninput = (e) => {
            const activeCat = document.querySelector('.filter-btn.active').dataset.cat;
            renderSidebar(activeCat, e.target.value);
        };

        renderSidebar();
        renderMainContent();
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Docs catalog generated successfully at: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    build_docs()
