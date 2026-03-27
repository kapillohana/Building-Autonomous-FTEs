---
name: approval-workflow
description: Manages Pending_Approval to Approved workflow
when_to_use: Continuously monitors for approval decisions
---

# SKILL: Approval Workflow

## Description
Manages Pending_Approval to Approved workflow.

## Instructions
- Monitor /Pending_Approval/ folder for new files
- Check every 30 seconds (Ralph Wiggum loop)
- When file moved to /Approved/: execute the approved action
- When file moved to /Rejected/: log rejection, notify if needed
- Maintain approval audit log

## Usage Prompt
Invoke approval-workflow: Monitor and execute approved actions

## Parameters
check_interval: 30 seconds
notify_on_reject: true

## Approval Categories
| Category | Auto-Approve Threshold | Requires Human |
|----------|----------------------|----------------|
| Email | Known contacts | New contacts |
| Payment | < $50 recurring | > $100 or new payee |
| Social Media | Scheduled posts | DMs, replies |
| File Ops | Read/Create | Delete, external |

## File Movement Triggers
- **Pending → Approved**: Execute action immediately
- **Pending → Rejected**: Log and archive
- **Approved → Done**: Action completed successfully
