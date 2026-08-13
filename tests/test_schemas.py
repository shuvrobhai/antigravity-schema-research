"""
Unit tests for antigravity_schemas models, registry, auditor, and validation functionality using standard library unittest.
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
from antigravity_schemas.registry import registry, SchemaRegistry
from antigravity_schemas.exporter import export_all_schemas
from antigravity_schemas.auditor import CategoryAuditResult, AuditReport, AuditStatus
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

    def test_schema_registry_descriptors(self):
        descriptors = registry.all_descriptors()
        self.assertEqual(len(descriptors), 13)

        settings_desc = registry.get("settings")
        self.assertIsNotNone(settings_desc)
        self.assertEqual(settings_desc.model_cls, SettingsSchema)
        self.assertEqual(settings_desc.filename, "settings.schema.json")

        plugin_desc = registry.get_by_filename("plugin.schema.json")
        self.assertIsNotNone(plugin_desc)
        self.assertEqual(plugin_desc.key, "plugin")

        schema_map = registry.schema_mapping()
        self.assertEqual(len(schema_map), 13)
        self.assertEqual(schema_map["settings.schema.json"], SettingsSchema)

        model_map = registry.model_mapping()
        self.assertEqual(len(model_map), 13)
        self.assertEqual(model_map["mcp"], MCPConfigSchema)

    def test_audit_report_domain_model(self):
        res1 = CategoryAuditResult(
            category="Settings",
            status=AuditStatus.VALID,
            path="/path/to/settings.json",
            details="Valid settings",
            valid_count=1,
        )
        res2 = CategoryAuditResult(
            category="Skills",
            status=AuditStatus.INVALID,
            path="/path/to/skills",
            details="1 invalid skill",
            invalid_count=1,
        )
        report = AuditReport(results=[res1, res2])

        self.assertEqual(report.total_audited, 2)
        self.assertEqual(report.total_valid, 1)
        self.assertEqual(report.total_invalid, 1)

        rows = report.to_table_rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "Settings")
        self.assertIn("VALID", rows[0][1])
        self.assertEqual(rows[1][0], "Skills")
        self.assertIn("INVALID", rows[1][1])

    def test_doc_sync_inspector(self):
        doc_path = Path("SCHEMA_REFERENCE.md")
        schemas_dir = Path("schemas")
        if doc_path.exists() and schemas_dir.exists():
            from antigravity_schemas.doc_inspector import DocSyncInspector
            inspector = DocSyncInspector(doc_path=doc_path, schemas_dir=schemas_dir)
            results = inspector.inspect()
            self.assertEqual(len(results), 13)
            synced_count = sum(1 for r in results if r.is_synced)
            self.assertGreaterEqual(synced_count, 10)

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

