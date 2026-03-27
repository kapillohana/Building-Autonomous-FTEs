# CLAIM-BY-MOVE: Platinum Tier Coordination Protocol

**Version:** 1.0
**Date:** 2026-03-26
**Tier:** Platinum (Cloud + Local Coordination)

---

## 🎯 Overview

**CLAIM-BY-MOVE** is the core coordination mechanism for Platinum Tier AI Employee systems operating across Cloud and Local zones. It enables distributed agents to coordinate work without central orchestration, using file system moves as the signaling mechanism.

---

## 🏗️ Architecture Context

### Zone Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD ZONE (Remote)                      │
│  - 24/7 Always-On Processing                                │
│  - High-volume watchers (Gmail, WhatsApp, LinkedIn)         │
│  - Draft generation                                         │
│  - Syncs to Local via cloud-sync/                           │
└─────────────────────────────────────────────────────────────┘
                              ↕ (sync)
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL ZONE (Your Machine)                │
│  - Human-in-the-Loop approval                               │
│  - Sensitive action execution                               │
│  - Odoo ERP integration                                     │
│  - Final audit logging                                      │
└─────────────────────────────────────────────────────────────┘
```

### Folder Mapping

| Cloud Zone | → | Local Zone | Purpose |
|------------|---|------------|---------|
| `cloud-zone/Inbox/` | → | `local-zone/Inbox/` | Incoming tasks |
| `cloud-zone/Needs_Action/` | → | `local-zone/Needs_Action/` | Pending work |
| `cloud-zone/Drafts/` | → | `local-zone/Pending_Approval/` | Awaiting approval |
| `cloud-zone/Approved/` | → | `local-zone/Approved/` | Ready to execute |
| `cloud-zone/Done/` | → | `local-zone/Done/` | Completed tasks |

---

## 📜 The CLAIM-BY-MOVE Rule

### Core Principle

> **"To claim work, move the file. To release work, move it back."**

File movement = Work assignment + State transition

---

### State Machine

```
                    ┌──────────────┐
                    │    Inbox     │
                    └──────┬───────┘
                           │ (agent claims)
                           ↓
                    ┌──────────────┐
          ┌────────│ Needs_Action │────────┐
          │        └──────┬───────┘        │
          │               │                │
          │ (too complex) │ (needs approval)
          │               │                │
          ↓               ↓                ↓
   ┌────────────┐  ┌──────────────┐  ┌──────────────┐
   │   Inbox    │  │Pending_Appro.│  │   Drafts     │
   └────────────┘  └──────┬───────┘  └──────┬───────┘
                          │                 │
                   (human approves)   (human approves)
                          │                 │
                          ↓                 ↓
                    ┌──────────────┐  ┌──────────────┐
                    │   Approved   │←─┤   Approved   │
                    └──────┬───────┘  └──────┬───────┘
                           │                 │
                    (execute locally)  (execute cloud)
                           │                 │
                           ↓                 ↓
                    ┌──────────────┐  ┌──────────────┐
                    │    Done      │  │    Done      │
                    └──────────────┘  └──────────────┘
```

---

## 🔐 Claim Mechanics

### How to Claim Work

**Step 1: Detect Available Work**
```bash
# List unclaimed files
ls local-zone/Inbox/
ls local-zone/Needs_Action/
```

**Step 2: Claim by Moving**
```bash
# Move file to your working area
mv local-zone/Inbox/TASK_001.md local-zone/Needs_Action/TASK_001.md
```

**Step 3: Add Claim Marker**
Append to the file:
```markdown
---
claimed_by: local-agent
claimed_at: 2026-03-26T10:30:00Z
working_zone: local
---
```

**Step 4: Process the Task**
Execute the required skill (e.g., `basic-processing-loop`).

**Step 5: Move to Next State**
```bash
# On completion
mv local-zone/Needs_Action/TASK_001.md local-zone/Done/TASK_001.md

# Or if needs approval
mv local-zone/Needs_Action/TASK_001.md local-zone/Pending_Approval/TASK_001.md

# Or if can't process
mv local-zone/Needs_Action/TASK_001.md local-zone/Inbox/TASK_001.md
```

---

### How to Release Work

**Reasons to Release:**
- Task too complex for current agent
- Requires different permissions
- Agent encountered error
- Task belongs to another zone

**Release Process:**
```bash
# Move back to Inbox (unclaimed state)
mv local-zone/Needs_Action/TASK_001.md local-zone/Inbox/TASK_001.md
```

**Add Release Note:**
```markdown
## Release Note
- **Released by:** local-agent
- **Released at:** 2026-03-26T10:45:00Z
- **Reason:** Requires cloud-based browser MCP for research
- **Next action:** Cloud agent should claim and execute
```

---

## 🌐 Cloud vs Local Zone Responsibilities

### Cloud Zone (Remote Agent)

**Capabilities:**
- ✓ High-volume email processing
- ✓ Social media monitoring
- ✓ Draft generation (emails, posts, responses)
- ✓ Research using browser MCP
- ✓ Data aggregation and summarization
- ✓ Sync coordination

**Limitations:**
- ✗ Cannot access local Odoo ERP
- ✗ Cannot execute financial transactions
- ✗ Cannot access local file system directly
- ✗ Requires human approval for sensitive actions

**Typical Workflow:**
```
1. Claim file from cloud-zone/Inbox/
2. Process: read, research, draft response
3. Move to cloud-zone/Drafts/ (needs approval)
4. Sync to local-zone/Pending_Approval/
5. Human reviews and approves (moves to Approved/)
6. Sync back to cloud-zone/Approved/
7. Cloud executes (sends email, posts)
8. Move to cloud-zone/Done/
```

---

### Local Zone (Your Machine)

**Capabilities:**
- ✓ Human-in-the-Loop approval
- ✓ Odoo ERP integration (payments, invoices)
- ✓ Local file system access
- ✓ Sensitive action execution
- ✓ Final audit logging
- ✓ Vault synchronization

**Limitations:**
- ✗ Not always-on (machine sleep/offline)
- ✗ Limited browser automation
- ✗ No high-volume processing
- ✗ Dependent on human availability

**Typical Workflow:**
```
1. Sync receives files from cloud-zone/
2. Human reviews Pending_Approval/ files
3. Approve: move to local-zone/Approved/
4. Local agent executes (Odoo, files)
5. Move to local-zone/Done/
6. Sync updates cloud-zone/Done/
```

---

## 🔄 Sync Protocol

### Sync Direction

```
Cloud → Local (Drafts, Completed)
Local → Cloud (Approvals, Commands)
```

### Sync Triggers

| Event | Sync Direction | Files |
|-------|---------------|-------|
| Cloud creates draft | Cloud → Local | `Drafts/*.md` → `Pending_Approval/*.md` |
| Human approves | Local → Cloud | `Approved/*.md` → `Approved/*.md` |
| Task completed (local) | Local → Cloud | `Done/*.md` → `Done/*.md` |
| Task completed (cloud) | Cloud → Local | `Done/*.md` → `Done/*.md` |

### Sync Script (Pseudocode)

```python
def sync_cloud_to_local():
    for file in cloud_zone/Drafts/:
        if not exists(local_zone/Pending_Approval/):
            copy(file, local_zone/Pending_Approval/)
    
    for file in cloud_zone/Done/:
        if not exists(local_zone/Done/):
            copy(file, local_zone/Done/)

def sync_local_to_cloud():
    for file in local_zone/Approved/:
        if not exists(cloud_zone/Approved/):
            copy(file, cloud_zone/Approved/)
    
    for file in local_zone/Done/:
        if not exists(cloud_zone/Done/):
            copy(file, cloud_zone/Done/)
```

---

## 📋 File Format

### Standard Task File

```markdown
---
type: email_response
from: client@example.com
priority: high
status: pending
created: 2026-03-26T10:00:00Z
zone: cloud
---

## Original Message
Client requesting invoice update.

## Suggested Action
- [ ] Generate updated invoice from Odoo
- [ ] Send via email
- [ ] Log transaction

## Processing Notes
[Agent adds notes here]

## Claim History
| Claimed By | Claimed At | Released At | Reason |
|------------|------------|-------------|--------|
| cloud-agent | 2026-03-26T10:05:00Z | - | - |
```

---

## 🎯 Decision Matrix

### When to Claim

| Condition | Action |
|-----------|--------|
| File in Inbox/Needs_Action | Claim if you have capacity |
| File matches your capabilities | Claim immediately |
| File requires your zone's permissions | Claim (e.g., local for Odoo) |
| File idle > 5 minutes | Claim (prevent starvation) |

### When NOT to Claim

| Condition | Action |
|-----------|--------|
| Already claimed by another agent | Wait or coordinate |
| Requires permissions you lack | Skip (wrong zone) |
| Currently at capacity | Skip |
| File marked "do not claim" | Respect marker |

### When to Release

| Condition | Action |
|-----------|--------|
| Task requires different zone | Release to Inbox |
| Task exceeds your capabilities | Release with note |
| Encountered blocking error | Release with error details |
| Human intervention needed | Move to Pending_Approval |

---

## 🚨 Error Handling

### Claim Conflicts

**Scenario:** Two agents claim same file simultaneously.

**Resolution:**
1. First file move wins (filesystem atomic)
2. Second agent detects file missing → claim next available
3. No coordination overhead needed

### Orphaned Claims

**Scenario:** Agent claims but never completes.

**Detection:**
- File in Needs_Action/ > 30 minutes
- No recent modifications

**Resolution:**
```bash
# Release orphaned task
mv local-zone/Needs_Action/OLD_TASK.md local-zone/Inbox/OLD_TASK.md
# Add release note with "orphaned" marker
```

### Sync Conflicts

**Scenario:** Same file modified in both zones.

**Resolution:**
1. Local zone always wins for approval decisions
2. Cloud zone wins for draft content
3. Use timestamps to determine latest
4. Manual review if both modified same section

---

## 📊 Monitoring

### Dashboard Integration

Add to `Dashboard.md`:

```markdown
## Zone Status

| Zone | Status | Active Claims | Pending | Last Sync |
|------|--------|---------------|---------|-----------|
| Cloud | ✓ Online | 3 | 12 | 2026-03-26T10:30:00Z |
| Local | ✓ Online | 1 | 5 | 2026-03-26T10:30:00Z |

## Cross-Zone Tasks

| Task ID | Current Zone | Claimed By | Status |
|---------|-------------|------------|--------|
| TASK_001 | Cloud | cloud-agent | Processing |
| TASK_002 | Local | local-agent | Pending Approval |
```

### Audit Log Entry

```json
{
  "timestamp": "2026-03-26T10:30:00Z",
  "event": "claim_by_move",
  "task_id": "TASK_001",
  "from_zone": "Inbox",
  "to_zone": "Needs_Action",
  "claimed_by": "local-agent",
  "action": "email_response",
  "status": "success"
}
```

---

## 🧪 Example Scenarios

### Scenario 1: Email Response (Cloud → Local → Cloud)

```
1. Gmail Watcher (Cloud) detects new email
   → Creates: cloud-zone/Inbox/EMAIL_001.md

2. Cloud Agent claims
   → Moves to: cloud-zone/Needs_Action/EMAIL_001.md
   → Drafts response
   → Moves to: cloud-zone/Drafts/EMAIL_001.md

3. Sync copies to Local
   → Appears: local-zone/Pending_Approval/EMAIL_001.md

4. Human reviews and approves
   → Moves to: local-zone/Approved/EMAIL_001.md

5. Sync copies back to Cloud
   → Appears: cloud-zone/Approved/EMAIL_001.md

6. Cloud Agent executes (sends email)
   → Moves to: cloud-zone/Done/EMAIL_001.md

7. Sync updates Local
   → Appears: local-zone/Done/EMAIL_001.md
```

---

### Scenario 2: Payment Processing (Local Only)

```
1. Invoice request arrives (synced from Cloud)
   → local-zone/Inbox/INVOICE_001.md

2. Local Agent claims
   → Moves to: local-zone/Needs_Action/INVOICE_001.md

3. Local Agent generates invoice via Odoo MCP
   → Requires human approval (financial transaction)
   → Moves to: local-zone/Pending_Approval/INVOICE_001.md

4. Human approves
   → Moves to: local-zone/Approved/INVOICE_001.md

5. Local Agent executes payment
   → Moves to: local-zone/Done/INVOICE_001.md

6. Sync updates Cloud for audit
   → cloud-zone/Done/INVOICE_001.md
```

---

### Scenario 3: Complex Research (Release & Reclaim)

```
1. Task requires deep research
   → cloud-zone/Inbox/RESEARCH_001.md

2. Cloud Agent claims, discovers needs browser MCP
   → Already has browser MCP, proceeds

3. Task requires local Odoo data (can't access from cloud)
   → Releases with note
   → Moves to: cloud-zone/Inbox/RESEARCH_001.md
   → Note: "Requires local-zone Odoo access"

4. Sync copies to Local
   → local-zone/Inbox/RESEARCH_001.md

5. Local Agent claims
   → Moves to: local-zone/Needs_Action/RESEARCH_001.md

6. Local Agent queries Odoo, completes research
   → Moves to: local-zone/Done/RESEARCH_001.md
```

---

## 📝 Best Practices

### For Cloud Agents

1. **Always draft, never execute sensitive actions**
2. **Sync frequently** (every 30 seconds)
3. **Release tasks requiring local permissions quickly**
4. **Add detailed processing notes for human reviewers**

### For Local Agents

1. **Review Pending_Approval first** (human waiting)
2. **Execute approved actions promptly**
3. **Sync completion status back to cloud**
4. **Log all financial transactions**

### For Humans

1. **Check Pending_Approval regularly** (bottleneck)
2. **Approve/reject within SLA** (e.g., 4 hours)
3. **Add feedback notes for rejected items**
4. **Monitor Dashboard for sync issues**

---

## 🔗 Related Documents

- **ARCHITECTURE.md** - System architecture overview
- **Dashboard.md** - Real-time zone status
- **SKILL_CloudDraft.md** - Cloud draft generation skill
- **SKILL_LocalApproval.md** - Local approval execution skill
- **Company_Handbook.md** - Approval thresholds and rules

---

**CLAIM-BY-MOVE Protocol v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
