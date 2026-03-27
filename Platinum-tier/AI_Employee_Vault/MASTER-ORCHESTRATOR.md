# MASTER-ORCHESTRATOR: Platinum Tier Cloud + Local Workflow

**Version:** 1.0
**Date:** 2026-03-26
**Tier:** Platinum (Cloud + Local Coordination)

---

## 🎯 Purpose

This document orchestrates the complete Platinum Tier workflow where:
- **Cloud Zone** processes high-volume tasks and generates drafts
- **Local Zone** provides human-in-the-loop approval and executes sensitive actions
- **Sync Service** coordinates file movement between zones

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD ZONE (24/7 Remote)                     │
│                                                                 │
│   Gmail/WhatsApp/LinkedIn Watchers                              │
│         ↓                                                       │
│   cloud-zone/Inbox/                                             │
│         ↓ (claim-by-move)                                       │
│   cloud-zone/Needs_Action/ ← SKILL_CloudDraft                   │
│         ↓ (draft ready)                                         │
│   cloud-zone/Drafts/                                            │
│         ↓ (sync)                                                │
└────────┼────────────────────────────────────────────────────────┘
         │
         │ SYNC SERVICE
         │ (copies files between zones)
         ↓
┌────────┼────────────────────────────────────────────────────────┐
│         │                    LOCAL ZONE (Your Machine)          │
│         ↓                                                       │
│   local-zone/Pending_Approval/                                  │
│         ↓ (human review)                                        │
│   Human decides: APPROVE or REJECT                              │
│         ↓ (claim-by-move)                                       │
│   local-zone/Approved/ ← SKILL_LocalApproval                    │
│         ↓ (execute with local MCP)                              │
│   local-zone/Done/                                              │
│         ↓ (sync)                                                │
│   cloud-zone/Done/ (audit copy)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

### Primary Locations

| Zone | Folder | Purpose |
|------|--------|---------|
| **Synced Vault** | `synced-vault/AI_Employee_Vault/` | Main vault with all files |
| **Cloud Zone** | `synced-vault/AI_Employee_Vault/cloud-zone/` | Cloud agent workspace |
| **Local Zone** | `synced-vault/AI_Employee_Vault/local-zone/` | Local agent workspace |

### Cloud Zone Folders

```
cloud-zone/
├── Inbox/              # Incoming tasks from watchers
├── Needs_Action/       # Currently being processed
├── Drafts/             # Ready for local approval
├── Approved/           # Approved by local, ready to execute
├── Rejected/           # Rejected by local
├── Plans/              # Execution plans
└── Done/               # Completed tasks
```

### Local Zone Folders

```
local-zone/
├── Inbox/              # Synced from cloud
├── Needs_Action/       # Currently being processed
├── Pending_Approval/   # Awaiting human decision
├── Approved/           # Human approved, ready to execute
├── Rejected/           # Human rejected
├── Plans/              # Execution plans
└── Done/               # Completed tasks
```

---

## 🔄 Complete Workflow

### Stage 1: Task Ingestion (Cloud)

**Trigger:** Gmail/WhatsApp/LinkedIn watcher detects new item

**Cloud Agent Actions:**
```bash
# 1. Create task file in cloud-zone/Inbox/
cat > cloud-zone/Inbox/TASK_001.md << 'EOF'
---
type: email_response
from: client@example.com
priority: high
zone: cloud
created: 2026-03-26T10:00:00Z
---

## Original Message
Client requesting invoice update.

## Suggested Action
- [ ] Generate updated invoice
- [ ] Send via email
EOF
```

---

### Stage 2: Cloud Processing (SKILL_CloudDraft)

**Trigger:** Task file in `cloud-zone/Inbox/`

**Cloud Agent Actions:**
```bash
# 1. Claim by moving
mv cloud-zone/Inbox/TASK_001.md cloud-zone/Needs_Action/TASK_001.md

# 2. Add claim marker
echo "---
claimed_by: cloud-agent
claimed_at: 2026-03-26T10:05:00Z
working_zone: cloud
---" >> cloud-zone/Needs_Action/TASK_001.md

# 3. Process task (research, draft)
# ... uses Browser MCP, Email MCP ...

# 4. Add draft response
cat >> cloud-zone/Needs_Action/TASK_001.md << 'EOF'

## Draft Response
**To:** client@example.com
**Subject:** Updated Invoice Attached

Dear Client,

Please find your updated invoice attached.

Best regards,
AI Employee
EOF

# 5. Move to Drafts for approval
mv cloud-zone/Needs_Action/TASK_001.md cloud-zone/Drafts/TASK_001.md
```

---

### Stage 3: Sync to Local

**Sync Service Actions:**
```python
# Sync script runs every 30 seconds
def sync_cloud_to_local():
    # Copy drafts to local Pending_Approval
    for file in cloud-zone/Drafts/*.md:
        if not exists(local-zone/Pending_Approval/{file.name}):
            copy(file, local-zone/Pending_Approval/)
```

**Result:** `local-zone/Pending_Approval/TASK_001.md` appears

---

### Stage 4: Human Review (Local)

**Trigger:** File appears in `local-zone/Pending_Approval/`

**Human Actions:**
```bash
# 1. Review the draft
cat local-zone/Pending_Approval/TASK_001.md

# 2. Decide: Approve or Reject

# If APPROVE:
mv local-zone/Pending_Approval/TASK_001.md local-zone/Approved/TASK_001.md

# Add approval metadata
cat >> local-zone/Approved/TASK_001.md << 'EOF'

## Approval Decision
- **Decision:** APPROVED
- **Approved by:** human-reviewer
- **Approved at:** 2026-03-26T10:30:00Z
EOF

# If REJECT:
mv local-zone/Pending_Approval/TASK_001.md local-zone/Rejected/TASK_001.md

# Add rejection reason
cat >> local-zone/Rejected/TASK_001.md << 'EOF'

## Rejection Decision
- **Decision:** REJECTED
- **Reason:** Incorrect client name
- **Required Changes:** Fix name to "John Smith"
EOF
```

---

### Stage 5: Local Execution (SKILL_LocalApproval)

**Trigger:** File in `local-zone/Approved/`

**Local Agent Actions:**
```bash
# 1. Monitor Approved folder (Ralph Wiggum loop)
while true; do
    for file in local-zone/Approved/*.md; do
        # 2. Check execution zone
        if grep -q "Execute in zone: local" "$file"; then
            # 3. Execute with local MCP (e.g., Odoo)
            # python odoo_mcp.py --execute "$file"
            
            # 4. Move to Done
            mv "$file" local-zone/Done/
        fi
    done
    sleep 30
done
```

---

### Stage 6: Cloud Execution (for cloud-zone tasks)

**Sync Service:** Copies `local-zone/Approved/` → `cloud-zone/Approved/`

**Cloud Agent Actions:**
```bash
# 1. Detect approved file
ls cloud-zone/Approved/

# 2. Execute (e.g., send email via Email MCP)
# python email_mcp.py --send cloud-zone/Approved/TASK_001.md

# 3. Move to Done
mv cloud-zone/Approved/TASK_001.md cloud-zone/Done/
```

---

### Stage 7: Sync Completion

**Sync Service:** Copies `cloud-zone/Done/` → `local-zone/Done/`

**Result:** Both zones have completion record for audit.

---

## 🎭 Agent Roles

### Cloud Agent

| Responsibility | Description |
|---------------|-------------|
| **Watchers** | Gmail, WhatsApp, LinkedIn monitoring |
| **Claim** | Move from `Inbox/` → `Needs_Action/` |
| **Process** | Research, draft, prepare |
| **Submit** | Move to `Drafts/` for approval |
| **Execute (Cloud)** | Email, Social, Browser MCP |
| **Complete** | Move to `Done/` |

### Local Agent

| Responsibility | Description |
|---------------|-------------|
| **Monitor** | Watch `Pending_Approval/` for human decisions |
| **Execute (Local)** | Odoo, File System, Database MCP |
| **Complete** | Move to `Done/`, sync to cloud |

### Human Reviewer

| Responsibility | Description |
|---------------|-------------|
| **Review** | Read files in `Pending_Approval/` |
| **Decide** | Approve → `Approved/`, Reject → `Rejected/` |
| **Feedback** | Add notes for rejected items |

---

## 🔐 Claim-By-Move Rules

### Rule 1: Atomic Claim

```bash
# Only one agent can move a file at a time
mv Inbox/TASK.md Needs_Action/TASK.md  # Atomic operation
```

### Rule 2: Zone Markers

Every task file MUST have:
```markdown
---
zone: cloud    # or local, or both
---
```

### Rule 3: Release on Failure

```bash
# If can't process, release back to Inbox
mv Needs_Action/TASK.md Inbox/TASK.md

# Add release note
cat >> Inbox/TASK.md << 'EOF'

## Release Note
- **Released by:** cloud-agent
- **Reason:** Requires local Odoo access
EOF
```

### Rule 4: Orphan Detection

```python
# Release files stuck > 30 minutes
def release_orphans():
    for file in Needs_Action/*.md:
        if age(file) > 30 minutes:
            mv file Inbox/
```

---

## 📊 Status Tracking

### Update ZONE-STATUS.md

```markdown
## Current Status

| Zone | Status | Active Claims | Pending | Last Sync |
|------|--------|---------------|---------|-----------|
| Cloud | 🟢 Online | 3 | 12 | 2026-03-26T10:30:00Z |
| Local | 🟡 Standby | 1 | 5 | 2026-03-26T10:30:00Z |
```

### Update Dashboard.md

```markdown
## Zone Status

| Folder | Cloud Count | Local Count |
|--------|-------------|-------------|
| Inbox | 0 | 0 |
| Needs_Action | 3 | 1 |
| Pending_Approval | - | 5 |
| Approved | 2 | 3 |
| Done | 150 | 148 |
```

---

## 🧪 Test Scenarios

### Test 1: Email Response (Cloud Execution)

```bash
# Setup
echo "---
type: email_response
from: test@example.com
zone: cloud
---
Test email" > cloud-zone/Inbox/TEST_001.md

# Run Cloud Draft
# Claude: "Use cloud-draft skill"

# Human approves
mv local-zone/Pending_Approval/TEST_001.md local-zone/Approved/

# Cloud executes
# Claude: "Execute approved email in cloud-zone/Approved/"
```

### Test 2: Invoice (Local Execution)

```bash
# Setup
echo "---
type: invoice
zone: local
---
Create invoice" > local-zone/Inbox/INV_001.md

# Run Local Approval
# Claude: "Use local-approval skill"

# Human approves
mv local-zone/Pending_Approval/INV_001.md local-zone/Approved/

# Local executes with Odoo MCP
# Claude: "Execute invoice with Odoo MCP"
```

---

## 🛠️ Commands Reference

### Cloud Agent Commands

```bash
# Claim work
mv cloud-zone/Inbox/*.md cloud-zone/Needs_Action/

# Submit for approval
mv cloud-zone/Needs_Action/*.md cloud-zone/Drafts/

# Check for approved work
ls cloud-zone/Approved/

# Complete
mv cloud-zone/Approved/*.md cloud-zone/Done/
```

### Local Agent Commands

```bash
# Check pending
ls local-zone/Pending_Approval/

# Approve
mv local-zone/Pending_Approval/*.md local-zone/Approved/

# Reject
mv local-zone/Pending_Approval/*.md local-zone/Rejected/

# Complete
mv local-zone/Approved/*.md local-zone/Done/
```

### Human Commands

```bash
# Review
cat local-zone/Pending_Approval/TASK.md

# Approve
mv local-zone/Pending_Approval/TASK.md local-zone/Approved/

# Reject
mv local-zone/Pending_Approval/TASK.md local-zone/Rejected/
```

### Sync Commands

```bash
# Manual sync (if needed)
python scripts/sync_zones.py

# Check sync status
ls cloud-zone/Done/
ls local-zone/Done/
```

---

## 🔗 Related Documents

| Document | Purpose |
|----------|---------|
| `SYNC-RULES.md` | Detailed sync protocol |
| `ZONE-STATUS.md` | Real-time zone status |
| `CLAIM-BY-MOVE.md` | Coordination protocol |
| `SKILL_CloudDraft.md` | Cloud agent skill |
| `SKILL_LocalApproval.md` | Local agent skill |
| `SKILL_ReasoningLoop.md` | Cross-zone coordination |

---

## 🚀 Quick Start

### Step 1: Initialize Zones

```bash
# Ensure zone folders exist
mkdir -p synced-vault/AI_Employee_Vault/cloud-zone/{Inbox,Needs_Action,Drafts,Approved,Rejected,Done}
mkdir -p synced-vault/AI_Employee_Vault/local-zone/{Inbox,Needs_Action,Pending_Approval,Approved,Rejected,Done}
```

### Step 2: Start Sync Service

```bash
# Run sync in background
python scripts/sync_zones.py &
```

### Step 3: Create Test Task

```bash
# Create test task in cloud Inbox
cat > synced-vault/AI_Employee_Vault/cloud-zone/Inbox/TEST_001.md << 'EOF'
---
type: test
zone: cloud
priority: high
---

## Test Task
This is a test task for Platinum Tier workflow.

## Suggested Action
- [ ] Process and draft response
- [ ] Submit for local approval
- [ ] Execute after approval
EOF
```

### Step 4: Run Full Workflow

```bash
# See test command below
```

---

**MASTER-ORCHESTRATOR v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
