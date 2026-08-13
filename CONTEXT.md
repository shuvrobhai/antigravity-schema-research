# Domain Glossary: Antigravity Schemas

This document defines the canonical domain vocabulary for the `antigravity-schemas` project.

## Core Concepts

### SchemaDescriptor
A metadata descriptor for a single Antigravity JSON schema specification, encapsulating its Pydantic model class, CLI alias key, canonical exported JSON file name, and ecosystem category.

### SchemaRegistry
The central single-source-of-truth registry for all 13 Antigravity schema models across Desktop 2.0, IDE, CLI, SDK, and shared core configurations.

### AuditReport
A strongly-typed domain model representing the aggregated results of validating a local Antigravity installation (`~/.gemini`) against schema specifications.

### CategoryAuditResult
A typed result for a specific audit category (Settings, MCP Configs, Skills, Agents, Transcripts), containing validation status (`VALID`, `INVALID`, `SKIPPED`, `ERROR`), file path, passing item count, error details, and table formatting adapters.
