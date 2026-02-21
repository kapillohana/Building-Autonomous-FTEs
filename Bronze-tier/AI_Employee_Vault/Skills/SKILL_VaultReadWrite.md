
---
name: vault-read-write
description: Basic read from and write to Obsidian vault files. Use for dashboard updates, logging, summarizing Needs_Action files.
when_to_use: When task involves reading Company_Handbook.md, updating Dashboard.md, or processing .md files in vault folders.
---

# SKILL: Vault Read/Write

## Description
Provides safe, file-system-based read/write access to Obsidian vault. Always use relative paths from vault root.

## Instructions for Claude
- Use built-in file tools to read/write .md files.
- Never overwrite without confirmation in plan.
- For updates: Append under specific sections (e.g., ## Recent Updates in Dashboard.md).
- Error handling: If file missing, create it or log to /Logs/error.md.
- Format outputs cleanly in Markdown.

## Usage Prompt (Invoke like this)
"Use vault-read-write: Read Company_Handbook.md and extract rules. Then update Dashboard.md with summary under ## Recent Updates."

## Parameters / Examples
- target_file: Company_Handbook.md
- output_file: Dashboard.md
- action: read / append / overwrite

## Ralph Wiggum Stub (for future)
If task has multiple steps and incomplete, re-prompt self: "Continue vault-read-write until done."