---
name: reasoning-loop
description: Platinum Tier cross-zone coordination - orchestrates Cloud and Local zones using claim-by-move rule
when_to_use: For cross-zone task coordination, weekly autonomous cycles, or complex multi-zone workflows
zone: both
---

# SKILL: Reasoning Loop (Platinum Tier)

## Description
Full Platinum Tier autonomous coordination between Cloud Zone (24/7 remote processing) and Local Zone (human-in-the-loop approval). Uses the **claim-by-move** rule for distributed coordination without central orchestration.

## Zones
**Both Cloud and Local** - Cross-zone coordination

## Base Path
All operations relative to: `synced-vault/AI_Employee_Vault/`

---

## 🏗️ Cross-Zone Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD ZONE                               │
│                                                             │
│   [Inbox] → [Needs_Action] → [Drafts] ───────┐             │
│                    ↑                         │             │
│                    │                         ↓             │
│   [Done] ← [Approved] ← [Approved] ←─────────┤             │
│                                                             │
│                      ↕ SYNC ↕                               │
│                                                             │
│   [Inbox] ← [Needs_Action] ← [Pending_Approval] ←───┐      │
│                    ↓                         ↑        │      │
│                    │                         │        │      │
│   [Done] → [Approved] → [Approved] ──────────┘        │      │
│                                                             │
│                    LOCAL ZONE                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Cross-Zone Coordination Loop

### Phase 1: Detect and Claim (Cloud)

```bash
cd synced-vault/AI_Employee_Vault

# Cloud agent detects work in Inbox
ls cloud-zone/Inbox/

# Claim by moving (atomic operation)
mv cloud-zone/Inbox/TASK_XXX.md cloud-zone/Needs_Action/

# Add claim marker
echo "---
claimed_by: cloud-agent
claimed_at: $(date -Iseconds)
working_zone: cloud
---" >> cloud-zone/Needs_Action/TASK_XXX.md
```

### Phase 2: Process and Draft (Cloud)

```bash
# Cloud agent processes task
# - Uses Browser MCP for research
# - Uses Email MCP for drafts
# - Uses Social MCP for content

# Add draft to file
cat >> cloud-zone/Needs_Action/TASK_XXX.md << 'EOF'

## Draft Response
{{draft_content}}

## Execution Assignment
- **Execute in zone:** cloud
- **Execute by:** cloud-agent
EOF

# Move to Drafts for local approval
mv cloud-zone/Needs_Action/TASK_XXX.md cloud-zone/Drafts/
```

### Phase 3: Sync to Local

```python
# Sync service runs every 30 seconds
def sync_cloud_to_local():
    for file in Path("cloud-zone/Drafts").glob("*.md"):
        if not Path(f"local-zone/Pending_Approval/{file.name}").exists():
            shutil.copy2(file, f"local-zone/Pending_Approval/{file.name}")
```

### Phase 4: Human Review (Local)

```bash
# Human reviews pending files
cat local-zone/Pending_Approval/TASK_XXX.md

# Human makes decision:

# APPROVE:
mv local-zone/Pending_Approval/TASK_XXX.md local-zone/Approved/

# Add approval metadata
cat >> local-zone/Approved/TASK_XXX.md << 'EOF'

## Approval Decision
- **Decision:** APPROVED
- **Approved by:** human-reviewer
- **Approved at:** 2026-03-26T14:30:00Z
EOF

# REJECT:
mv local-zone/Pending_Approval/TASK_XXX.md local-zone/Rejected/
```

### Phase 5: Execute (Zone-Specific)

**Cloud Execution:**
```bash
# Sync copies approval to cloud
# Cloud agent detects in cloud-zone/Approved/

# Execute with cloud MCPs (Email, Social, Browser)
# python email_mcp.py --send cloud-zone/Approved/TASK_XXX.md

# Move to Done
mv cloud-zone/Approved/TASK_XXX.md cloud-zone/Done/
```

**Local Execution:**
```bash
# Local agent detects in local-zone/Approved/

# Execute with local MCPs (Odoo, File System, Database)
# python odoo_mcp.py --execute local-zone/Approved/TASK_XXX.md

# Move to Done
mv local-zone/Approved/TASK_XXX.md local-zone/Done/
```

### Phase 6: Sync Completion

```python
# Sync copies Done files between zones
def sync_done():
    # Cloud → Local
    for file in Path("cloud-zone/Done").glob("*.md"):
        if not Path(f"local-zone/Done/{file.name}").exists():
            shutil.copy2(file, f"local-zone/Done/{file.name}")
    
    # Local → Cloud
    for file in Path("local-zone/Done").glob("*.md"):
        if not Path(f"cloud-zone/Done/{file.name}").exists():
            shutil.copy2(file, f"cloud-zone/Done/{file.name}")
```

---

## 🎯 Ralph Wiggum Persistence Loop

```python
def cross_zone_reasoning_loop():
    """Continue until all tasks complete across both zones."""
    
    base_path = Path("synced-vault/AI_Employee_Vault")
    max_iterations = 100
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Check Cloud Zone
        cloud_inbox = len(list((base_path / "cloud-zone" / "Inbox").glob("*.md")))
        cloud_needs_action = len(list((base_path / "cloud-zone" / "Needs_Action").glob("*.md")))
        cloud_drafts = len(list((base_path / "cloud-zone" / "Drafts").glob("*.md")))
        cloud_approved = len(list((base_path / "cloud-zone" / "Approved").glob("*.md")))
        
        # Check Local Zone
        local_inbox = len(list((base_path / "local-zone" / "Inbox").glob("*.md")))
        local_needs_action = len(list((base_path / "local-zone" / "Needs_Action").glob("*.md")))
        local_pending = len(list((base_path / "local-zone" / "Pending_Approval").glob("*.md")))
        local_approved = len(list((base_path / "local-zone" / "Approved").glob("*.md")))
        
        # Check if all complete
        total_pending = (cloud_inbox + cloud_needs_action + cloud_drafts + 
                        cloud_approved + local_pending + local_approved)
        
        if total_pending == 0:
            print("All zones complete - exiting loop")
            break
        
        # Process Cloud Zone
        if cloud_inbox > 0:
            print(f"Cloud: {cloud_inbox} tasks to claim")
            # Invoke cloud-draft skill
        
        if cloud_approved > 0:
            print(f"Cloud: {cloud_approved} tasks to execute")
            # Execute cloud approved tasks
        
        # Process Local Zone
        if local_pending > 0:
            print(f"Local: {local_pending} tasks awaiting human approval")
            # Alert human for review
        
        if local_approved > 0:
            print(f"Local: {local_approved} tasks to execute")
            # Invoke local-approval skill
        
        # Run sync
        run_sync_cycle()
        
        # Update ZONE-STATUS.md
        update_zone_status()
        
        # Cooldown
        time.sleep(30)
    
    # Generate summary
    generate_cycle_summary()
```

---

## 📊 Zone Status Tracking

### Update ZONE-STATUS.md

```python
def update_zone_status():
    """Update zone status dashboard."""
    
    base_path = Path("synced-vault/AI_Employee_Vault")
    
    # Count files in each zone
    cloud_counts = {
        "Inbox": len(list((base_path / "cloud-zone" / "Inbox").glob("*.md"))),
        "Needs_Action": len(list((base_path / "cloud-zone" / "Needs_Action").glob("*.md"))),
        "Drafts": len(list((base_path / "cloud-zone" / "Drafts").glob("*.md"))),
        "Approved": len(list((base_path / "cloud-zone" / "Approved").glob("*.md"))),
        "Done": len(list((base_path / "cloud-zone" / "Done").glob("*.md"))),
    }
    
    local_counts = {
        "Inbox": len(list((base_path / "local-zone" / "Inbox").glob("*.md"))),
        "Needs_Action": len(list((base_path / "local-zone" / "Needs_Action").glob("*.md"))),
        "Pending_Approval": len(list((base_path / "local-zone" / "Pending_Approval").glob("*.md"))),
        "Approved": len(list((base_path / "local-zone" / "Approved").glob("*.md"))),
        "Done": len(list((base_path / "local-zone" / "Done").glob("*.md"))),
    }
    
    # Update ZONE-STATUS.md with counts
    # ... (see ZONE-STATUS.md for format)
```

---

## 🔐 Claim-By-Move Rules

### Rule 1: Atomic Claim
```bash
# Only one agent can move a file at a time
mv Inbox/TASK.md Needs_Action/TASK.md  # Atomic - only one succeeds
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
def release_orphans():
    """Release files stuck > 30 minutes."""
    for folder in ["cloud-zone/Needs_Action", "local-zone/Needs_Action"]:
        for file in Path(folder).glob("*.md"):
            if age(file) > 30 * 60:  # 30 minutes
                mv(file, folder.replace("Needs_Action", "Inbox"))
```

---

## 🧪 Weekly Autonomous Cycle

### Sunday 11 PM - Data Collection

```bash
# Collect from all sources
# - Gmail watcher → cloud-zone/Inbox/
# - WhatsApp watcher → cloud-zone/Inbox/
# - LinkedIn watcher → cloud-zone/Inbox/
# - Local files → local-zone/Inbox/
```

### Sunday 11:30 PM - Planning

```bash
# Create weekly plan
cat > cloud-zone/Plans/Weekly_Plan_2026-W13.md << 'EOF'
# Weekly Plan - 2026-W13

## Cloud Zone Tasks
- [ ] Process email backlog
- [ ] Draft social media posts
- [ ] Research trending topics

## Local Zone Tasks
- [ ] Review pending approvals
- [ ] Execute Odoo transactions
- [ ] Audit completed tasks
EOF
```

### Monday 12 AM - 6 AM - Execution

```bash
# Run cross-zone reasoning loop
# Cloud: Process, draft, submit for approval
# Local: Human reviews, approves, executes
# Sync: Coordinate between zones
```

### Monday 6 AM - Audit & Complete

```bash
# Generate weekly summary
# Update Dashboard.md
# Archive to Done/
# Log to audit_YYYY-MM-DD.json
```

---

## Usage Prompt

```
Use reasoning-loop: Run Platinum Tier cross-zone coordination loop. Monitor cloud-zone/ and local-zone/ folders. Apply claim-by-move rule. Process cloud drafts, coordinate local approvals, execute zone-specific actions. Sync between zones. Continue until all tasks complete.
```

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `zones` | cloud,local | Both zones active |
| `base_path` | synced-vault/AI_Employee_Vault/ | Root path |
| `check_interval` | 30 seconds | Loop frequency |
| `sync_enabled` | true | Auto-sync between zones |
| `claim_by_move` | true | Use file movement for coordination |
| `max_iterations` | 100 | Safety limit |

---

## Integration Matrix

| Component | Zone | Trigger | Output |
|-----------|------|---------|--------|
| Cloud Draft | Cloud | Inbox task | Draft in Drafts/ |
| Local Approval | Local | Pending file | Decision in Approved/ |
| Sync Service | Both | Folder change | File copied |
| Odoo MCP | Local | Approved financial | Transaction complete |
| Email MCP | Cloud | Approved email | Email sent |
| Audit Logger | Both | Any action | JSON log entry |

---

## Error Recovery

```python
def execute_with_recovery(operation, zone, details):
    """Execute with cross-zone error recovery."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = operation()
            log_success(zone, operation.__name__, details)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                # Create approval file for human review
                create_approval_file(operation.__name__, details, e)
                log_failure(zone, operation.__name__, e)
                return None
            time.sleep(2 * (2 ** attempt))  # Exponential backoff
```

---

## Related Skills

- **SKILL_CloudDraft.md** - Cloud zone processing
- **SKILL_LocalApproval.md** - Local zone approval
- **SKILL_BasicProcessing.md** - General task processing
- **SYNC-RULES.md** - Zone synchronization rules
- **ZONE-STATUS.md** - Zone status tracking
- **MASTER-ORCHESTRATOR.md** - Complete workflow guide

---

## Example Cross-Zone Workflow

```
1. Gmail Watcher → cloud-zone/Inbox/EMAIL_001.md
2. Cloud agent claims → cloud-zone/Needs_Action/
3. Cloud drafts response → cloud-zone/Drafts/
4. Sync → local-zone/Pending_Approval/
5. Human approves → local-zone/Approved/
6. Sync → cloud-zone/Approved/
7. Cloud executes (Email MCP) → cloud-zone/Done/
8. Sync → local-zone/Done/
9. Audit log updated
```

---

## Quick Reference Commands

```bash
# Check all zone status
ls cloud-zone/Inbox/ cloud-zone/Approved/
ls local-zone/Pending_Approval/ local-zone/Approved/

# Run sync manually
python scripts/sync_zones.py

# Update zone status
python scripts/update_zone_status.py

# Run reasoning loop
python scripts/reasoning_loop.py --platinum
```

---

**SKILL_ReasoningLoop.md v1.0 - Platinum Tier**
*Last Updated: 2026-03-26*
