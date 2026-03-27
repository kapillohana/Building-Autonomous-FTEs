# SYNC-RULES: Platinum Tier Zone Coordination

**Version:** 1.0
**Date:** 2026-03-26
**Tier:** Platinum (Cloud + Local Coordination)

---

## 🎯 Purpose

This document defines the exact rules for synchronizing work between Cloud Zone (remote 24/7 agent) and Local Zone (your machine with human oversight) in the Platinum Tier AI Employee system.

---

## 📁 Zone Folder Structure

### Cloud Zone (`cloud-zone/`)

```
cloud-zone/
├── Inbox/           # Unclaimed incoming tasks
├── Needs_Action/    # Currently being processed by cloud agent
├── Drafts/          # Completed drafts awaiting local approval
├── Approved/        # Approved by local, ready for cloud execution
├── Rejected/        # Rejected by local, needs revision
├── Plans/           # Execution plans (cloud agent)
└── Done/            # Completed tasks
```

### Local Zone (`local-zone/`)

```
local-zone/
├── Inbox/           # Synced from cloud, unclaimed
├── Needs_Action/    # Currently being processed locally
├── Pending_Approval/# Awaiting human decision
├── Approved/        # Human approved, ready for local execution
├── Rejected/        # Human rejected
├── Plans/           # Execution plans (local agent)
└── Done/            # Completed tasks
```

---

## 🔐 Rule 1: CLAIM-BY-MOVE

### The Golden Rule

> **"To claim work, move the file. To release work, move it back."**

File movement IS the coordination mechanism. No locks, no databases, no central coordinator.

---

### Claim Protocol

**Step 1: Detect Available Work**
```bash
# Cloud agent checks cloud-zone folders
ls cloud-zone/Inbox/
ls cloud-zone/Needs_Action/

# Local agent checks local-zone folders  
ls local-zone/Inbox/
ls local-zone/Needs_Action/
```

**Step 2: Claim by Moving**
```bash
# Cloud agent claims from cloud-zone
mv cloud-zone/Inbox/TASK_001.md cloud-zone/Needs_Action/TASK_001.md

# Local agent claims from local-zone
mv local-zone/Inbox/TASK_002.md local-zone/Needs_Action/TASK_002.md
```

**Step 3: Add Claim Marker (Optional but Recommended)**
```markdown
---
claimed_by: cloud-agent    # or local-agent
claimed_at: 2026-03-26T10:30:00Z
working_zone: cloud        # or local
---
```

---

### Release Protocol

**When to Release:**
- Task requires different zone's permissions
- Task exceeds agent capabilities
- Blocking error encountered
- Task idle too long (starvation prevention)

**How to Release:**
```bash
# Move back to Inbox (unclaimed state)
mv cloud-zone/Needs_Action/TASK_001.md cloud-zone/Inbox/TASK_001.md
mv local-zone/Needs_Action/TASK_001.md local-zone/Inbox/TASK_001.md
```

**Add Release Note:**
```markdown
## Release Note
- **Released by:** cloud-agent
- **Released at:** 2026-03-26T10:45:00Z
- **Reason:** Requires local-zone Odoo access
- **Next action:** Local agent should claim
```

---

## 🌐 Rule 2: ZONE RESPONSIBILITIES

### Cloud Zone Responsibilities

| Capability | Cloud Zone | Local Zone |
|------------|:----------:|:----------:|
| 24/7 Always-On | ✓ | ✗ |
| High-Volume Processing | ✓ | ✗ |
| Gmail Watcher | ✓ | ✗ |
| WhatsApp Watcher | ✓ | ✗ |
| LinkedIn Watcher | ✓ | ✗ |
| Browser MCP (Research) | ✓ | ✗ |
| Email MCP (Send) | ✓ | ✗ |
| Social Media MCP | ✓ | ✗ |
| Draft Generation | ✓ | ✗ |
| Odoo ERP Access | ✗ | ✓ |
| Local File System | ✗ | ✓ |
| Human Approval | ✗ | ✓ |
| Financial Execution | ✗ | ✓ |
| Final Audit Log | ✗ | ✓ |

---

### Cloud Zone Workflow

```
1. Watchers detect incoming work
   → Creates: cloud-zone/Inbox/TASK_XXX.md

2. Cloud agent claims
   → Moves to: cloud-zone/Needs_Action/

3. Process: research, draft, prepare
   → Uses: Browser MCP, Email MCP, Social MCP

4. If needs human approval:
   → Moves to: cloud-zone/Drafts/
   → Sync copies to: local-zone/Pending_Approval/

5. Wait for local approval decision

6. If approved (appears in cloud-zone/Approved/):
   → Execute (send email, post, etc.)
   → Moves to: cloud-zone/Done/

7. If rejected (appears in cloud-zone/Rejected/):
   → Log rejection
   → Revise or archive
```

---

### Local Zone Workflow

```
1. Sync receives drafts from cloud
   → Appears: local-zone/Pending_Approval/

2. Human reviews pending files
   → Reads draft, context, research

3. Human makes decision:
   - Approve: move to local-zone/Approved/
   - Reject: move to local-zone/Rejected/
   - Changes: edit and return to local-zone/Inbox/

4. Sync copies decision to cloud
   → local-zone/Approved/ → cloud-zone/Approved/

5. Local agent executes (if local action needed)
   → Uses: Odoo MCP, File System
   → Moves to: local-zone/Done/

6. Sync updates cloud Done folder
   → local-zone/Done/ → cloud-zone/Done/
```

---

## 🔄 Rule 3: SYNC DIRECTION

### Sync Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOUD ZONE                             │
│                                                             │
│   Inbox → Needs_Action → Drafts → Approved → Done          │
│                              ↓         ↑         ↑          │
│                              │         │         │          │
│                              │ SYNC    │ SYNC    │ SYNC     │
│                              │         │         │          │
│                              ↓         ↑         ↑          │
│  Inbox → Needs_Action → Pending_Approval → Approved → Done │
│                                                             │
│                      LOCAL ZONE                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Sync Triggers

| Event | Source | Destination | Files |
|-------|--------|-------------|-------|
| Draft Created | Cloud | Local | `cloud-zone/Drafts/*.md` → `local-zone/Pending_Approval/` |
| Approval Decision | Local | Cloud | `local-zone/Approved/*.md` → `cloud-zone/Approved/` |
| Rejection Decision | Local | Cloud | `local-zone/Rejected/*.md` → `cloud-zone/Rejected/` |
| Cloud Task Done | Cloud | Local | `cloud-zone/Done/*.md` → `local-zone/Done/` |
| Local Task Done | Local | Cloud | `local-zone/Done/*.md` → `cloud-zone/Done/` |

---

### Sync Script (Python Example)

```python
#!/usr/bin/env python3
"""
Sync service for Cloud ↔ Local zone coordination.
Run continuously or on schedule (every 30 seconds).
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

class ZoneSync:
    def __init__(self, cloud_root: Path, local_root: Path):
        self.cloud = cloud_root
        self.local = local_root
        self.sync_log = []
    
    def sync_cloud_to_local(self):
        """Copy drafts and completed tasks from cloud to local."""
        
        # Sync Drafts → Pending_Approval
        draft_src = self.cloud / "Drafts"
        approval_dst = self.local / "Pending_Approval"
        self._sync_folder(draft_src, approval_dst, "draft")
        
        # Sync Done (both directions, merge)
        cloud_done = self.cloud / "Done"
        local_done = self.local / "Done"
        self._sync_folder(cloud_done, local_done, "done")
    
    def sync_local_to_cloud(self):
        """Copy approval decisions and completed tasks to cloud."""
        
        # Sync Approved → Approved
        local_approved = self.local / "Approved"
        cloud_approved = self.cloud / "Approved"
        self._sync_folder(local_approved, cloud_approved, "approval")
        
        # Sync Rejected → Rejected
        local_rejected = self.local / "Rejected"
        cloud_rejected = self.cloud / "Rejected"
        self._sync_folder(local_rejected, cloud_rejected, "rejection")
        
        # Sync Done (both directions, merge)
        local_done = self.local / "Done"
        cloud_done = self.cloud / "Done"
        self._sync_folder(local_done, cloud_done, "done")
    
    def _sync_folder(self, src: Path, dst: Path, sync_type: str):
        """Copy new/updated files from src to dst."""
        if not src.exists():
            return
        
        dst.mkdir(parents=True, exist_ok=True)
        
        for file in src.glob("*.md"):
            dst_file = dst / file.name
            
            # Copy if destination doesn't exist or source is newer
            if not dst_file.exists() or file.stat().st_mtime > dst_file.stat().st_mtime:
                shutil.copy2(file, dst_file)
                self._log_sync(sync_type, file.name, str(src), str(dst))
    
    def _log_sync(self, sync_type: str, filename: str, src: str, dst: str):
        """Log sync operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": sync_type,
            "file": filename,
            "from": src,
            "to": dst
        }
        self.sync_log.append(entry)
        print(f"[SYNC {sync_type.upper()}] {filename}: {src} → {dst}")
    
    def run(self):
        """Run one sync cycle."""
        self.sync_cloud_to_local()
        self.sync_local_to_cloud()
        return self.sync_log


if __name__ == "__main__":
    cloud_root = Path("/path/to/cloud-zone")
    local_root = Path("/path/to/local-zone")
    
    sync = ZoneSync(cloud_root, local_root)
    log = sync.run()
    print(f"Synced {len(log)} files")
```

---

## 🚫 Rule 4: AVOID DOUBLE-WORK

### Problem: Two Agents Claim Same File

**Scenario:** Cloud and Local agents both try to claim TASK_001 simultaneously.

**Solution: Filesystem Atomicity**

```
Time 0: TASK_001.md exists in cloud-zone/Inbox/
Time 1: Cloud agent executes: mv Inbox TASK_001.md Needs_Action/
Time 2: Local agent checks Inbox/ - file is GONE
Time 3: Local agent knows: already claimed, skip
```

**Key Insight:** File move is atomic. Only one agent succeeds. The other sees the file is missing and moves on.

---

### Problem: Sync Creates Duplicate

**Scenario:** Sync copies file to both zones, both agents think it's theirs.

**Solution: Zone Marker in File**

Every task file MUST include zone designation:

```markdown
---
type: email_response
zone: cloud          # or local, or both
source: gmail-watcher
---
```

**Agent Checks Zone Before Claiming:**
```python
def should_claim(file_path: Path, my_zone: str) -> bool:
    content = file_path.read_text()
    if f"zone: {my_zone}" not in content and "zone: both" not in content:
        return False  # Wrong zone, skip
    return True  # Correct zone, can claim
```

---

### Problem: Agent Crashes After Claim

**Scenario:** Cloud agent claims TASK_001, crashes before completing. File stuck in Needs_Action/.

**Solution: Orphan Detection + Auto-Release**

```python
def detect_orphans(folder: Path, max_age_minutes: int = 30) -> list:
    """Find files stuck in Needs_Action too long."""
    orphans = []
    now = datetime.now()
    
    for file in folder.glob("*.md"):
        age = now - datetime.fromtimestamp(file.stat().st_mtime)
        if age.total_seconds() > max_age_minutes * 60:
            orphans.append(file)
    
    return orphans

def release_orphan(file: Path, inbox: Path):
    """Release orphaned file back to Inbox."""
    with open(file, "a") as f:
        f.write(f"\n## Orphan Release\n")
        f.write(f"- **Released at:** {datetime.now().isoformat()}\n")
        f.write(f"- **Reason:** Orphaned (no activity > 30 min)\n")
    
    shutil.move(str(file), str(inbox / file.name))
```

---

### Problem: Human Approves, Cloud Executes, But Local Also Executes

**Scenario:** Both zones try to execute same approved task.

**Solution: Execution Zone Marker**

```markdown
## Execution Assignment
- **Execute in zone:** cloud    # or local
- **Execute by:** cloud-agent   # or local-agent
- **Executed at:** [timestamp added after execution]
```

**Agent Checks Before Executing:**
```python
def should_execute(file_path: Path, my_zone: str) -> bool:
    content = file_path.read_text()
    
    # Already executed?
    if "Executed at:" in content:
        return False
    
    # Assigned to my zone?
    if f"Execute in zone: {my_zone}" not in content:
        return False
    
    return True
```

---

## 📊 Rule 5: STATUS TRACKING

### Dashboard Integration

Update `Dashboard.md` with zone status:

```markdown
## Zone Status

| Zone | Status | Active Claims | Pending | Last Sync |
|------|--------|---------------|---------|-----------|
| Cloud | ✓ Online | 3 | 12 | 2026-03-26T10:30:00Z |
| Local | ✓ Online | 1 | 5 | 2026-03-26T10:30:00Z |

## Cross-Zone Tasks

| Task ID | Current Zone | Claimed By | Status | Waiting On |
|---------|-------------|------------|--------|------------|
| TASK_001 | Cloud | cloud-agent | Draft Ready | Local Approval |
| TASK_002 | Local | local-agent | Executing | Odoo MCP |
| TASK_003 | Cloud | - | Unclaimed | - |
```

---

### Audit Log Entry Format

Every zone transition logged:

```json
{
  "timestamp": "2026-03-26T10:30:00Z",
  "event": "claim",
  "task_id": "TASK_001",
  "from_folder": "Inbox",
  "to_folder": "Needs_Action",
  "zone": "cloud",
  "agent": "cloud-agent",
  "action_type": "email_response",
  "status": "success"
}
```

---

## 🧪 Example Scenarios

### Scenario 1: Email Response (Standard Flow)

```
1. Gmail Watcher (Cloud) creates cloud-zone/Inbox/EMAIL_001.md
2. Cloud agent claims: moves to cloud-zone/Needs_Action/
3. Cloud agent drafts response, moves to cloud-zone/Drafts/
4. Sync copies to local-zone/Pending_Approval/EMAIL_001.md
5. Human reviews, approves: moves to local-zone/Approved/
6. Sync copies to cloud-zone/Approved/EMAIL_001.md
7. Cloud agent detects, sends email via Email MCP
8. Cloud agent moves to cloud-zone/Done/
9. Sync copies to local-zone/Done/
```

**Zone Transitions:** Inbox → Needs_Action → Drafts → [Sync] → Pending_Approval → Approved → [Sync] → Approved → Done

---

### Scenario 2: Payment (Local Execution)

```
1. Invoice request synced to local-zone/Inbox/INVOICE_001.md
2. Local agent claims: moves to local-zone/Needs_Action/
3. Local agent creates invoice via Odoo MCP
4. Moves to local-zone/Pending_Approval/ (financial = approval)
5. Human approves: moves to local-zone/Approved/
6. Local agent executes payment via Odoo MCP
7. Moves to local-zone/Done/
8. Sync copies to cloud-zone/Done/ (audit only)
```

**Zone Transitions:** Inbox → Needs_Action → Pending_Approval → Approved → Done → [Sync] → Done

---

### Scenario 3: Release and Reclaim

```
1. Task in cloud-zone/Inbox/RESEARCH_001.md
2. Cloud agent claims, discovers needs Odoo data
3. Cloud agent releases: moves back to cloud-zone/Inbox/
   Adds note: "Requires local-zone Odoo access"
4. Sync copies to local-zone/Inbox/
5. Local agent claims: moves to local-zone/Needs_Action/
6. Local agent queries Odoo, completes task
7. Moves to local-zone/Done/
8. Sync copies to cloud-zone/Done/
```

**Zone Transitions:** Cloud Inbox → Cloud Needs_Action → Cloud Inbox → [Sync] → Local Inbox → Local Needs_Action → Local Done → [Sync] → Cloud Done

---

## 📋 Quick Reference

### Cloud Agent Commands

```bash
# Claim work
mv cloud-zone/Inbox/*.md cloud-zone/Needs_Action/

# Submit for approval
mv cloud-zone/Needs_Action/*.md cloud-zone/Drafts/

# Check for approved work
ls cloud-zone/Approved/

# Execute and complete
mv cloud-zone/Approved/*.md cloud-zone/Done/

# Release if can't process
mv cloud-zone/Needs_Action/*.md cloud-zone/Inbox/
```

---

### Local Agent Commands

```bash
# Check pending approvals
ls local-zone/Pending_Approval/

# Approve
mv local-zone/Pending_Approval/TASK.md local-zone/Approved/

# Reject
mv local-zone/Pending_Approval/TASK.md local-zone/Rejected/

# Check for local execution
ls local-zone/Approved/

# Complete local work
mv local-zone/Approved/TASK.md local-zone/Done/

# Release if can't process
mv local-zone/Needs_Action/TASK.md local-zone/Inbox/
```

---

### Human Commands

```bash
# Review pending
cat local-zone/Pending_Approval/TASK.md

# Approve (move file)
mv local-zone/Pending_Approval/TASK.md local-zone/Approved/

# Reject (move file)
mv local-zone/Pending_Approval/TASK.md local-zone/Rejected/

# Request changes (edit then move)
mv local-zone/Pending_Approval/TASK.md local-zone/Inbox/
```

---

## 🔗 Related Documents

- **CLAIM-BY-MOVE.md** - Full coordination protocol
- **ZONE-STATUS.md** - Real-time zone status tracking
- **SKILL_CloudDraft.md** - Cloud agent skill
- **SKILL_LocalApproval.md** - Local agent skill
- **Dashboard.md** - System status overview

---

**SYNC-RULES v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
