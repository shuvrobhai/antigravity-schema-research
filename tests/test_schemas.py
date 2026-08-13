"""
Unit tests for antigravity_schemas models and validation functionality using standard library unittest.
"""

import json
import unittest
import tempfile
from pathlib import Path
from antigravity_schemas.models import (
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
from antigravity_schemas.exporter import export_all_schemas


class TestSchemas(unittest.TestCase):
    def test_settings_schema_valid(self):
        data = {
            "toolPermission": "request-review",
            "artifactReviewPolicy": "asks-for-review",
            "enableTerminalSandbox": False,
            "trustedWorkspaces": ["/path/to/repo"],
            "model": "Gemini 3.5 Flash (Low)"
        }
        model = SettingsSchema.model_validate(data)
        self.assertEqual(model.toolPermission.value, "request-review")
        self.assertEqual(model.model, "Gemini 3.5 Flash (Low)")

    def test_agent_frontmatter_valid(self):
        data = {
            "name": "test-agent",
            "description": "A specialized testing subagent.",
            "tools": ["view_file", "run_command"],
            "model": "pro",
            "commandExecutionPolicy": "sandbox"
        }
        model = AgentFrontmatterSchema.model_validate(data)
        self.assertEqual(model.name, "test-agent")
        self.assertEqual(model.model, "pro")

    def test_skill_frontmatter_valid(self):
        data = {
            "name": "test-skill",
            "description": "Helps with running unit test suites."
        }
        model = SkillFrontmatterSchema.model_validate(data)
        self.assertEqual(model.description, "Helps with running unit test suites.")

    def test_mcp_config_valid(self):
        data = {
            "mcpServers": {
                "sqlite": {
                    "command": "node",
                    "args": ["/path/to/server.js"],
                    "env": {"DB": "/data.db"}
                }
            }
        }
        model = MCPConfigSchema.model_validate(data)
        self.assertIn("sqlite", model.mcpServers)
        self.assertEqual(model.mcpServers["sqlite"].command, "node")

    def test_transcript_step_valid(self):
        data = {
            "step_index": 0,
            "source": "USER_EXPLICIT",
            "type": "USER_INPUT",
            "status": "DONE",
            "content": "Hello agent!"
        }
        model = TranscriptStepSchema.model_validate(data)
        self.assertEqual(model.step_index, 0)
        self.assertEqual(model.type, "USER_INPUT")

    def test_export_all_schemas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            exported = export_all_schemas(tmp_path)
            self.assertEqual(len(exported), 9)
            for filename, path in exported.items():
                self.assertTrue(path.exists())
                content = json.loads(path.read_text())
                self.assertTrue("title" in content or "properties" in content or "type" in content or "$ref" in content)


if __name__ == "__main__":
    unittest.main()
