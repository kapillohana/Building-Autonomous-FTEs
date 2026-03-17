
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

## Ralph Wiggum Loop Stub (for multi-step autonomy)
While task incomplete (e.g., checkboxes unchecked in Plan.md or file not in /Done):
Re-prompt self: "Continue basic-processing-loop until all steps complete and file moved to /Done. Do not stop early."

### Loop Implementation
- **Trigger**: When files remain in /Needs_Action or checkboxes unchecked
- **Action**: Re-execute basic-processing-loop skill
- **Termination**: Only when all /Needs_Action files moved to /Done AND all Plan.md checkboxes marked complete

## Human-in-the-Loop (HITL)
For sensitive actions (email, LinkedIn post):
- Write draft to /Pending_Approval/
- Wait for user to move file to /Approved/
- Then execute using Ralph Wiggum loop (check every 30 seconds)