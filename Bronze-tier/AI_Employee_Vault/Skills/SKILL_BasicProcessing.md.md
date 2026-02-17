
---
name: basic-processing-loop
description: Basic loop to process /Needs_Action files, move to /Done, update dashboard. Includes Ralph Wiggum stub.
when_to_use: After any Watcher drops files, or for general task completion.
---

# SKILL: Basic Processing Loop

## Description
Autonomous processing of actionable .md files.

## Instructions
- List files in /Needs_Action.
- For each: Read, summarize/log, apply relevant skills (e.g., gmail-watcher-processor).
- Update Dashboard.md (e.g., decrement pending count).
- Move to /Done.
- If incomplete (e.g., needs approval), stop and note in Plan.md.

## Ralph Wiggum Loop Stub
While checkboxes in Plan.md are unchecked or task not moved to /Done:
Re-prompt: "Continue basic-processing-loop until complete."

## Usage Prompt
"Use basic-processing-loop: Process everything in /Needs_Action."