---
name: local-approval
description: Local zone skill for human-in-the-loop approval and execution of sensitive actions
when_to_use: When cloud zone drafts require human approval, or local tasks need execution
zone: local
---

# SKILL: Local Approval (Platinum Tier)

## Description
Local zone skill for reviewing cloud-generated drafts, making approval decisions, and executing sensitive actions that require local permissions (Odoo, file system, financial transactions).

## Zone
**Local Zone Only** - Your machine with human oversight

## Base Path
All operations relative to: `synced-vault/AI_Employee_Vault/`

---

## 📁 Zone Folder Structure

```
synced-vault/AI_Employee_Vault/
└── local-zone/
    ├── Inbox/           # ← Synced from cloud, claim from here
    ├── Needs_Action/    # ← Work here (claimed tasks)
    ├── Pending_Approval/# ← Human reviews here
    ├── Approved/        # ← Human approved, execute from here
    ├── Rejected/        # → Human rejected
    └── Done/            # → Move here (completed)
```

---

## Instructions

### Phase 1: Monitor Pending Approvals

**Step 1: Check Pending_Approval Folder**
```bash
cd synced-vault/AI_Employee_Vault

# List files awaiting human approval
ls local-zone/Pending_Approval/
```

**Step 2: Review Synced Drafts**
- Cloud drafts sync to `local-zone/Pending_Approval/`
- Each file contains draft content + context
- Review against `Company_Handbook.md` rules

**Step 3: Prioritize by Category**

| Priority | Category | SLA |
|----------|----------|-----|
| High | Financial transactions | 1 hour |
| High | Client communications | 2 hours |
| Medium | Social media posts | 4 hours |
| Low | Internal documents | 24 hours |

---

### Phase 2: Human Review and Decision

**For Each Pending File:**

**Step 1: Read Full Context**
```bash
# View file content
cat local-zone/Pending_Approval/TASK_XXX.md
```

**Step 2: Evaluate Against Handbook**
- Does this follow company policies?
- Is the tone appropriate?
- Are amounts within thresholds?
- Is execution zone correct?

**Step 3: Make Decision**

**APPROVE:**
```bash
# Move to Approved folder
mv local-zone/Pending_Approval/TASK_XXX.md local-zone/Approved/TASK_XXX.md
```

**REJECT:**
```bash
# Create Rejected folder if needed
mkdir -p local-zone/Rejected

# Move to Rejected folder
mv local-zone/Pending_Approval/TASK_XXX.md local-zone/Rejected/TASK_XXX.md
```

**REQUEST CHANGES:**
```bash
# Edit file with feedback, then move back to Inbox
mv local-zone/Pending_Approval/TASK_XXX.md local-zone/Inbox/TASK_XXX.md
```

---

### Phase 3: Add Approval Metadata

**When Approving, Add to File:**
```markdown
## Approval Decision

- **Decision:** APPROVED
- **Approved by:** human-reviewer
- **Approved at:** 2026-03-26T14:30:00Z
- **Conditions:** [any special instructions]
```

**When Rejecting, Add to File:**
```markdown
## Rejection Decision

- **Decision:** REJECTED
- **Rejected by:** human-reviewer
- **Rejected at:** 2026-03-26T14:30:00Z
- **Reason:** [detailed explanation]

## Required Changes
[What needs to be fixed]
```

---

### Phase 4: Execute Approved Actions (Local)

**Step 1: Monitor Approved Folder**
```bash
# Ralph Wiggum loop - check every 30 seconds
ls local-zone/Approved/
```

**Step 2: When File Appears in Approved/**
- Read the approved action details
- Verify approval metadata present
- Verify execution zone is `local`

**Step 3: Execute Based on Type**

**Financial (Odoo MCP):**
```bash
# Read approved transaction
cat local-zone/Approved/PAY_XXX.md

# Use Odoo MCP to create invoice/payment
# python odoo_mcp.py --execute local-zone/Approved/PAY_XXX.md

# Move to Done
mv local-zone/Approved/PAY_XXX.md local-zone/Done/PAY_XXX.md
```

**File Operations:**
```bash
# Read file operation request
cat local-zone/Approved/FILE_XXX.md

# Execute file operation (read/create/move)
# Never delete without explicit approval

# Move to Done
mv local-zone/Approved/FILE_XXX.md local-zone/Done/FILE_XXX.md
```

**Database Operations:**
```bash
# Read database query/update
cat local-zone/Approved/DB_XXX.md

# Execute via Database MCP
# Move to Done
mv local-zone/Approved/DB_XXX.md local-zone/Done/DB_XXX.md
```

---

### Phase 5: Log Completion

**Add to File:**
```markdown
## Execution Complete
- **Executed by:** local-agent
- **Executed at:** 2026-03-26T15:00:00Z
- **Result:** Success
- **Transaction ID:** [if applicable]
- **Synced to cloud:** Yes
```

**Sync will copy to `cloud-zone/Done/` for audit.**

---

## Usage Prompt

```
Use local-approval: Review files in synced-vault/AI_Employee_Vault/local-zone/Pending_Approval/, make approve/reject decisions with metadata. For approved items in local-zone/Approved/, execute using local MCPs (Odoo, File System). Move completed to local-zone/Done/.
```

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `zone` | local | This skill runs in local zone only |
| `base_path` | synced-vault/AI_Employee_Vault/ | Root path for all operations |
| `check_interval` | 30 seconds | Ralph Wiggum loop for Approved folder |
| `pending_path` | local-zone/Pending_Approval/ | Human reviews here |
| `approved_path` | local-zone/Approved/ | Execute from here |
| `rejected_path` | local-zone/Rejected/ | Rejections go here |
| `done_path` | local-zone/Done/ | Complete to here |

---

## Approval Decision Matrix

### Auto-Approve Guidelines

| Condition | Decision |
|-----------|----------|
| Email to known contact, standard reply | Approve |
| Scheduled social post, on-brand | Approve |
| Payment < $50, recurring vendor | Approve |

### Require Careful Review

| Condition | Action |
|-----------|--------|
| Email to new contact | Review |
| Payment > $100 | Review |
| Public social media | Review |

### Auto-Reject Indicators

| Condition | Decision |
|-----------|----------|
| Violates company policy | Reject |
| Incorrect recipient | Reject |
| Wrong amount/payee | Reject |

---

## Execution Permissions

### Local Zone Can Execute

| Action Type | MCP Required |
|-------------|--------------|
| Odoo transactions | Odoo MCP |
| File system ops | File System |
| Database queries | Database MCP |

### Cloud Zone Executes (After Local Approval)

| Action Type | MCP Required |
|-------------|--------------|
| Email send | Email MCP |
| Social posting | Social MCP |
| Browser automation | Browser MCP |

---

## Sync Protocol

### After Approval Decision

```
1. Human moves file to Approved/ or Rejected/
2. Local agent adds decision metadata
3. Sync service copies to cloud-zone/
4. Cloud agent detects and acts accordingly
```

### Sync Direction

```
Local → Cloud (Decisions)
- local-zone/Approved/*.md → cloud-zone/Approved/
- local-zone/Rejected/*.md → cloud-zone/Rejected/
- local-zone/Done/*.md → cloud-zone/Done/

Cloud → Local (Drafts)
- cloud-zone/Drafts/*.md → local-zone/Pending_Approval/
```

---

## Error Handling

### Execution Fails
1. Log error details to file
2. Move back to `local-zone/Needs_Action/`
3. Notify human via Dashboard

### Sync Fails
1. Retry 3 times
2. Alert via Dashboard
3. Hold until resolved

---

## Zone Coordination

### When to Sync to Cloud

| Event | Destination |
|-------|-------------|
| Approval decision | cloud-zone/Approved/ |
| Rejection decision | cloud-zone/Rejected/ |
| Task completed | cloud-zone/Done/ |

### When to Check Local Folders

| Folder | Frequency | Action |
|--------|-----------|--------|
| Pending_Approval/ | 2 minutes | Human review |
| Approved/ | 30 seconds | Execute local actions |
| Inbox/ | 30 seconds | Claim available work |

---

## Best Practices

1. **Review promptly** - Don't bottleneck the pipeline
2. **Add clear feedback** - Help cloud agent improve
3. **Check zone markers** - Only execute local-assigned tasks
4. **Verify before executing** - Double-check approval metadata
5. **Log decisions** - Audit trail required

---

## Related Skills

- **SKILL_CloudDraft.md** - Cloud zone draft generation counterpart
- **SKILL_OdooAccounting.md** - Financial transactions
- **SKILL_VaultReadWrite.md** - File operations
- **SYNC-RULES.md** - Zone synchronization rules
- **MASTER-ORCHESTRATOR.md** - Complete workflow guide

---

## Example Workflow

### Email Approval (Cloud Execution)

```
1. Cloud draft synced to local-zone/Pending_Approval/
2. Human reviews and approves → local-zone/Approved/
3. Sync copies to cloud-zone/Approved/
4. Cloud agent sends via Email MCP
5. Both zones update Done/
```

### Payment Approval (Local Execution)

```
1. Invoice request in local-zone/Pending_Approval/
2. Human approves → local-zone/Approved/
3. Local agent executes via Odoo MCP
4. Move to local-zone/Done/
5. Sync updates cloud-zone/Done/
```

---

## Quick Reference Commands

```bash
# Check pending approvals
ls -la local-zone/Pending_Approval/

# Approve
mv local-zone/Pending_Approval/TASK.md local-zone/Approved/

# Reject
mv local-zone/Pending_Approval/TASK.md local-zone/Rejected/

# Check approved awaiting execution
ls -la local-zone/Approved/

# Complete
mv local-zone/Approved/TASK.md local-zone/Done/
```

---

## Human Review Checklist

- [ ] Draft follows company tone
- [ ] Recipient/contact verified
- [ ] Amounts within thresholds
- [ ] Execution zone correct
- [ ] No sensitive data exposed

---

**SKILL_LocalApproval.md v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
