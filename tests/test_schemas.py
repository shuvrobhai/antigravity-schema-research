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
    RuleFileSchema,
    CLIStateSchema,
    CLIHistoryEntrySchema,
    TrustedHooksSchema,
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

    def test_rule_file_schema_valid(self):
        data = {
            "name": "Global Rules",
            "scope": "global",
            "rules": [
                {
                    "rule_id": "RULE[user_global]",
                    "description": "Always respond in English.",
                    "incorrect_example": "Hello in Spanish",
                    "correct_example": "Hello in English"
                }
            ]
        }
        model = RuleFileSchema.model_validate(data)
        self.assertEqual(model.rules[0].rule_id, "RULE[user_global]")

    def test_cli_state_schema_valid(self):
        data = {
          "runtimes": {"node": "v26.5.0", "python": "3.14.6", "docker": True},
          "providers": [{"id": "github", "status": "authenticated", "scopes": ["repo"]}],
          "installed_tools": {"mcp_servers": ["pieces"], "plugins": ["apple"]}
        }
        model = CLIStateSchema.model_validate(data)
        self.assertEqual(model.runtimes["node"], "v26.5.0")
        self.assertEqual(model.providers[0].id, "github")

    def test_cli_history_entry_schema_valid(self):
        data = {
            "timestamp": "2026-08-13T19:00:00Z",
            "prompt": "build feature",
            "session_id": "sess-123",
            "exit_code": 0
        }
        model = CLIHistoryEntrySchema.model_validate(data)
        self.assertEqual(model.prompt, "build feature")

    def test_trusted_hooks_schema_valid(self):
        data = {
            "trusted_hashes": {"/scripts/pre_commit.sh": "sha256abc123"},
            "auto_approve_sandbox": True
        }
        model = TrustedHooksSchema.model_validate(data)
        self.assertTrue(model.auto_approve_sandbox)

    def test_schema_registry_descriptors(self):
        descriptors = registry.all_descriptors()
        self.assertEqual(len(descriptors), 17)

        settings_desc = registry.get("settings")
        self.assertIsNotNone(settings_desc)
        self.assertEqual(settings_desc.model_cls, SettingsSchema)
        self.assertEqual(settings_desc.filename, "settings.schema.json")

        rule_desc = registry.get("rule")
        self.assertIsNotNone(rule_desc)
        self.assertEqual(rule_desc.model_cls, RuleFileSchema)

        schema_map = registry.schema_mapping()
        self.assertEqual(len(schema_map), 17)

        model_map = registry.model_mapping()
        self.assertEqual(len(model_map), 17)

    def test_doc_sync_inspector(self):
        doc_path = Path("SCHEMA_REFERENCE.md")
        schemas_dir = Path("schemas")
        if doc_path.exists() and schemas_dir.exists():
            from antigravity_schemas.doc_inspector import DocSyncInspector
            inspector = DocSyncInspector(doc_path=doc_path, schemas_dir=schemas_dir)
            results = inspector.inspect()
            self.assertEqual(len(results), 17)
            synced_count = sum(1 for r in results if r.is_synced)
            self.assertEqual(synced_count, 17)

    def test_export_all_schemas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            exported = export_all_schemas(tmp_path)
            self.assertEqual(len(exported), 17)
            for filename, path in exported.items():
                self.assertTrue(path.exists())
                content = json.loads(path.read_text())
                self.assertTrue("title" in content or "properties" in content or "type" in content or "$ref" in content)



if __name__ == "__main__":
    unittest.main()

