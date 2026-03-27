---
name: cloud-draft
description: Cloud zone skill for processing tasks from synced-vault and generating drafts for local approval
when_to_use: When cloud agent claims tasks requiring human approval before execution
zone: cloud
---

# SKILL: Cloud Draft (Platinum Tier)

## Description
Cloud zone skill for processing incoming tasks from `synced-vault/AI_Employee_Vault`, conducting research, and generating drafts that require local zone human approval before execution.

## Zone
**Cloud Zone Only** - Remote 24/7 processing agent

## Base Path
All operations relative to: `synced-vault/AI_Employee_Vault/`

---

## 📁 Zone Folder Structure

```
synced-vault/AI_Employee_Vault/
├── cloud-zone/
│   ├── Inbox/           # ← Claim from here
│   ├── Needs_Action/    # ← Work here (claimed tasks)
│   ├── Drafts/          # → Move here (awaiting approval)
│   ├── Approved/        # ← Monitor for approved work
│   ├── Rejected/        # ← Check for rejections
│   └── Done/            # → Move here (completed)
└── local-zone/
    └── Pending_Approval/ # → Sync destination for drafts
```

---

## Instructions

### Phase 1: Claim Task

**Step 1: Detect Available Work**
```bash
cd synced-vault/AI_Employee_Vault

# List unclaimed files in cloud zone
ls cloud-zone/Inbox/
ls cloud-zone/Needs_Action/
```

**Step 2: Verify Zone Assignment**
Before claiming, check file has correct zone marker:
```markdown
---
zone: cloud    # or zone: both
---
```
Skip files marked `zone: local`.

**Step 3: Claim by Moving**
```bash
# Move file to working area
mv cloud-zone/Inbox/TASK_XXX.md cloud-zone/Needs_Action/TASK_XXX.md
```

**Step 4: Add Claim Marker**
Append to file:
```markdown
---
claimed_by: cloud-agent
claimed_at: 2026-03-26T10:30:00Z
working_zone: cloud
---
```

---

### Phase 2: Process Task

**For Email Responses:**
1. Read original email content from file
2. Check `Company_Handbook.md` for response guidelines
3. Use Browser MCP for research if needed
4. Draft response following company tone
5. Add draft to file under `## Draft Response`

**For Social Media Posts:**
1. Read topic/content requirements
2. Research trending topics (Browser MCP)
3. Draft post for each platform
4. Add platform-specific variations
5. Include suggested hashtags and media notes

**For Document Generation:**
1. Gather required information
2. Use templates from vault
3. Generate draft document
4. Add placeholders for missing info
5. Mark sections needing human review

---

### Phase 3: Move to Approval

**Step 1: Update File Status**
```markdown
## Processing Complete
- **Processed by:** cloud-agent
- **Completed at:** 2026-03-26T10:45:00Z
- **Action required:** Human approval
- **Reason:** External communication

## Execution Assignment
- **Execute in zone:** cloud
- **Execute by:** cloud-agent
```

**Step 2: Move to Drafts Folder**
```bash
mv cloud-zone/Needs_Action/TASK_XXX.md cloud-zone/Drafts/TASK_XXX.md
```

**Step 3: Sync to Local**
File will be synced to `local-zone/Pending_Approval/` by sync service.

---

### Phase 4: Monitor for Approval Decision

**Ralph Wiggum Loop - Check Every 30 Seconds:**

```bash
# Check for approved files
ls cloud-zone/Approved/

# Check for rejected files
ls cloud-zone/Rejected/
```

**When File Appears in Approved/:**
1. Read approval decision and any conditions
2. Verify approval metadata present
3. Execute the approved action (Email MCP, Social MCP, etc.)
4. Move to Done

**When File Appears in Rejected/:**
1. Read rejection reason
2. Review feedback
3. Revise and resubmit or archive

---

### Phase 5: Execute Approved Actions

**For Email (Email MCP):**
```bash
# Read approved draft
cat cloud-zone/Approved/EMAIL_XXX.md

# Execute via Email MCP
# Send to recipient

# Move to Done
mv cloud-zone/Approved/EMAIL_XXX.md cloud-zone/Done/EMAIL_XXX.md
```

**For Social Media (Social MCP):**
```bash
# Read approved posts
cat cloud-zone/Approved/SOCIAL_XXX.md

# Execute via Social MCP
# Post to platforms

# Move to Done
mv cloud-zone/Approved/SOCIAL_XXX.md cloud-zone/Done/SOCIAL_XXX.md
```

---

### Phase 6: Log Completion

**Add to File:**
```markdown
## Execution Complete
- **Executed by:** cloud-agent
- **Executed at:** 2026-03-26T11:00:00Z
- **Result:** Success
- **Synced to local:** Yes
```

---

## Usage Prompt

```
Use cloud-draft: Process claimed task in synced-vault/AI_Employee_Vault/cloud-zone/Needs_Action/, generate draft, move to cloud-zone/Drafts/. Sync will copy to local-zone/Pending_Approval/. Monitor cloud-zone/Approved/ for approved files and execute. Move completed to cloud-zone/Done/.
```

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `zone` | cloud | This skill runs in cloud zone only |
| `base_path` | synced-vault/AI_Employee_Vault/ | Root path for all operations |
| `check_interval` | 30 seconds | Ralph Wiggum loop for Approved folder |
| `sync_enabled` | true | Auto-sync drafts to local zone |
| `inbox_path` | cloud-zone/Inbox/ | Claim from here |
| `work_path` | cloud-zone/Needs_Action/ | Process here |
| `draft_path` | cloud-zone/Drafts/ | Submit for approval here |
| `approved_path` | cloud-zone/Approved/ | Execute from here |
| `done_path` | cloud-zone/Done/ | Complete to here |

---

## Draft Template

```markdown
## Draft Response

**To:** {{recipient}}
**Subject:** {{subject}}
**Tone:** Professional

{{draft_body}}

---
**Requires Review:** Yes

## Execution Assignment
- **Execute in zone:** cloud
- **Execute by:** cloud-agent
- **MCP Required:** Email MCP
```

---

## Error Handling

### Draft Generation Fails
1. Log error to file under `## Errors`
2. Move to Drafts with gaps marked
3. Human can fill gaps or reject

### Sync Fails
1. Retry 3 times with exponential backoff
2. Alert via Dashboard
3. Hold in Drafts until resolved

### Approval Timeout (> 4 hours)
1. Add reminder note
2. Move to `cloud-zone/Inbox/` with "URGENT" marker

---

## Zone Coordination

### When to Sync to Local

| Event | Destination |
|-------|-------------|
| Draft ready | local-zone/Pending_Approval/ |
| Task completed | local-zone/Done/ |

### When to Check Cloud Folders

| Folder | Frequency | Action |
|--------|-----------|--------|
| Inbox/ | 30 seconds | Claim available work |
| Approved/ | 30 seconds | Execute approved actions |
| Rejected/ | 60 seconds | Review and revise |

---

## Related Skills

- **SKILL_LocalApproval.md** - Local zone approval counterpart
- **SKILL_BrowserMCP.md** - Web research
- **SKILL_EmailMCP.md** - Email operations
- **SYNC-RULES.md** - Zone synchronization rules
- **MASTER-ORCHESTRATOR.md** - Complete workflow guide

---

## Example Workflow

```
1. Gmail Watcher creates cloud-zone/Inbox/EMAIL_001.md
2. cloud-draft claims: moves to cloud-zone/Needs_Action/
3. Reads email, researches, drafts response
4. Moves to cloud-zone/Drafts/
5. Sync copies to local-zone/Pending_Approval/
6. Human approves: moves to local-zone/Approved/
7. Sync copies to cloud-zone/Approved/
8. cloud-draft sends email via Email MCP
9. Moves to cloud-zone/Done/
10. Sync updates local-zone/Done/
```

---

**SKILL_CloudDraft.md v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
