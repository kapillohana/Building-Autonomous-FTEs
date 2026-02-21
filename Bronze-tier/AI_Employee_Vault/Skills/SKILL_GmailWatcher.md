
---
name: gmail-watcher-processor
description: Processes Gmail action files created by gmail_watcher.py in /Needs_Action. Summarizes emails, suggests actions.
when_to_use: When new EMAIL_*.md files appear in /Needs_Action from Gmail Watcher.
---

# SKILL: Gmail Watcher Processor

## Description
Handles Gmail urgent/unread emails dropped as .md files.

## Instructions
1. Scan /Needs_Action for EMAIL_*.md.
2. Read YAML frontmatter + content.
3. Summarize sender/subject/snippet.
4. Suggest actions based on Company_Handbook.md rules.
5. Write summary to Dashboard.md or create Plan.md.
6. Move processed file to /Done.
7. Log any issues to /Logs/.

## Usage Prompt
"Invoke gmail-watcher-processor: Process all new EMAIL files in /Needs_Action and update dashboard."

## Parameters
- priority: high (default)
- auto_move: true