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
    MasterConfigSchema,
    ProjectsIndexSchema,
    DesktopStateSchema,
    IDEStateSchema,
)
from antigravity_schemas.exporter import export_all_schemas
from antigravity_schemas.models.desktop_state import parse_pbtxt_state


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

    def test_master_config_valid(self):
        data = {
            "plugins": {"engineering": {"enabled": True}},
            "userSettings": {"themeMode": "THEME_MODE_LIGHT"}
        }
        model = MasterConfigSchema.model_validate(data)
        self.assertTrue(model.plugins["engineering"].enabled)

    def test_projects_index_valid(self):
        data = {
            "projects": {"/Users/user/dev": "dev"}
        }
        model = ProjectsIndexSchema.model_validate(data)
        self.assertEqual(model.projects["/Users/user/dev"], "dev")

    def test_desktop_state_valid(self):
        pbtxt_sample = """
post_onboarding: {
  completed_steps: POST_ONBOARDING_STEP_TYPE_MANAGER_WELCOME
}
installation_uuid: "666c50bb-b65b-484a-81b4-a911c45ade2a"
"""
        parsed = parse_pbtxt_state(pbtxt_sample)
        model = DesktopStateSchema.model_validate(parsed)
        self.assertEqual(model.installation_uuid, "666c50bb-b65b-484a-81b4-a911c45ade2a")

    def test_ide_state_valid(self):
        data = {
            "installation_id": "ide-uuid-123",
            "active_conversations_count": 161,
            "browser_recordings": [
                {"recording_id": "rec-1", "frame_count": 300, "path": "/path/to/rec"}
            ]
        }
        model = IDEStateSchema.model_validate(data)
        self.assertEqual(model.active_conversations_count, 161)

    def test_export_all_schemas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            exported = export_all_schemas(tmp_path)
            self.assertEqual(len(exported), 13)
            for filename, path in exported.items():
                self.assertTrue(path.exists())
                content = json.loads(path.read_text())
                self.assertTrue("title" in content or "properties" in content or "type" in content or "$ref" in content)


if __name__ == "__main__":
    unittest.main()
