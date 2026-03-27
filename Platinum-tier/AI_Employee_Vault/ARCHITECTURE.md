# AI Employee Vault - Bronze Tier Architecture

**Version:** 1.0
**Date:** 2026-02-22
**Status:** Complete & Operational

---

## 📐 System Overview

The AI Employee Vault is a local-first, agent-driven automation system built on three core principles:

1. **Privacy-First**: All data stays on your machine (Obsidian vault)
2. **Human-in-the-Loop**: Critical decisions require human approval
3. **Agent-Driven**: Claude Code acts as the autonomous reasoning engine

---

## 🏗️ Architecture Layers

### Layer 1: Perception (Watchers)

**Purpose**: Monitor external sources for incoming tasks

#### Gmail Watcher
- **Language**: Python 3
- **Trigger**: Gmail API (unread, important emails)
- **Frequency**: Every 2 minutes
- **Output**: Markdown files in `/Needs_Action`
- **File**: `scripts/gmail_watcher.py`

**How it works:**
```
Gmail API
   ↓
Query: is:unread is:important
   ↓
Extract: From, Subject, Body, Date
   ↓
Format as Markdown
   ↓
Write to /Needs_Action/EMAIL_{id}.md
```

#### File System Watcher
- **Language**: Python 3 (watchdog library)
- **Trigger**: Files created in `Drop/` folder
- **Frequency**: Real-time monitoring
- **Output**: Markdown metadata files in `/Needs_Action`
- **File**: `scripts/filesystem_watcher.py`

**How it works:**
```
File dropped in Drop/ folder
   ↓
Watchdog detects creation
   ↓
Generate metadata (size, type, path)
   ↓
Create action file
   ↓
Write to /Needs_Action/FILE_{name}_{timestamp}.md
```

**Base Pattern** (`scripts/base_watcher.py`):
```python
class BaseWatcher(ABC):
    - check_for_updates() → list
    - create_action_file(item) → Path
    - run() → infinite loop
```

---

### Layer 2: Memory & Interface (Obsidian Vault)

**Purpose**: Local knowledge base + file-based communication

#### Core Files

| File | Purpose | Updated By |
|------|---------|-----------|
| **Dashboard.md** | Real-time KPIs | Claude Code |
| **Company_Handbook.md** | Rules & policies | Human |
| **Plan.md** | Current processing plan | Claude Code |

#### Action Folders

| Folder | Purpose | Flow |
|--------|---------|------|
| **/Needs_Action** | Incoming tasks | Watchers → Claude |
| **/Plans** | Execution plans | Claude → Human |
| **/Pending_Approval** | Awaiting approval | Claude → Human → Approved |
| **/Approved** | Ready to execute | Human → System |
| **/Done** | Completed tasks | System → Archive |
| **/Logs** | Audit trail | System → Log |

#### Data Structure

Each action file is Markdown with YAML frontmatter:

```markdown
---
type: email|file_drop|approval_request
from: sender@example.com
priority: high|medium|low
status: pending|complete|blocked
created: 2026-02-22T10:30:00Z
---

## Content
[Task details]

## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

---

### Layer 3: Reasoning (Claude Code)

**Purpose**: AI decision-making and task orchestration

#### Processing Loop

```
claude "Use basic-processing-loop"
   ↓
1. List files in /Needs_Action
   ↓
2. For each file:
   a. Read content
   b. Check against Company_Handbook.md
   c. Create Plan.md with steps
   ↓
3. For sensitive actions:
   a. Create /Pending_Approval file
   b. Stop and wait for approval
   ↓
4. For approved/auto-approved actions:
   a. Execute (update files, call MCP)
   b. Log to /Logs
   ↓
5. Move completed files to /Done
   ↓
6. Update Dashboard.md
```

#### Decision Framework

Claude evaluates each task against:

1. **Company_Handbook.md Rules**
   - Communication standards
   - Financial thresholds
   - Priority levels
   - Approval requirements

2. **Approval Matrix** (from Handbook)
   ```
   Auto-Approve:
   - Email to known contact
   - Payment < $50 recurring
   - Scheduled social post

   Require Approval:
   - Email to new contact
   - Payment > $100
   - Direct message replies
   - File deletion
   ```

3. **Contextual Analysis**
   - Is sender known?
   - Does amount exceed threshold?
   - Is this urgent?
   - Are there security concerns?

---

### Layer 4: Action (MCP Servers - Future)

**Purpose**: Execute approved actions on external systems

*Bronze tier uses file-based actions*
*Silver tier will add MCP servers for:*
- Email sending
- Browser automation
- Social media posting
- Calendar updates

---

## 🔄 Data Flow Example: Email Processing

```
Gmail receives email from Client A asking for invoice
   ↓
Gmail Watcher detects: unread + important
   ↓
Creates: /Needs_Action/EMAIL_abc123.md
   {
     type: email
     from: client_a@example.com
     subject: "Invoice for January"
     priority: high
   }
   ↓
Claude reads /Needs_Action/EMAIL_abc123.md
   ↓
Claude checks Company_Handbook.md:
   - "Client A" = known contact ✓
   - No approval needed for reply ✓
   - Standard response acceptable ✓
   ↓
Claude creates /Plans/PLAN_invoice_client_a.md
   {
     objective: Generate and send invoice
     steps:
       - [ ] Retrieve January invoice
       - [ ] Send to client_a@example.com
       - [ ] Log transaction
       - [ ] Move to /Done
   }
   ↓
Claude reads invoice from vault
Claude drafts email response
Claude marks approval_status: auto_approved
   ↓
(In Silver tier: Claude calls Email MCP to send)
(In Bronze tier: Claude logs action)
   ↓
Claude moves email to /Done/EMAIL_abc123.md
Claude updates Dashboard.md: "Invoice sent to Client A"
Claude logs to /Logs/2026-02-22.json
   ↓
Complete ✓
```

---

## 🛡️ Safety Mechanisms

### Human-in-the-Loop (HITL)

**File-based approval system:**

```
Claude detects sensitive action
   ↓
Creates: /Pending_Approval/PAYMENT_NewVendor_500.md
   {
     action: payment
     amount: 500
     recipient: new_vendor@example.com
     requires_approval: true
   }
   ↓
Human reviews file
   ↓
If Approve: Move to /Approved
If Reject: Move to /Rejected
   ↓
Claude monitors /Approved folder
   ↓
Claude executes approved action
   ↓
Claude logs result
```

### Approval Thresholds (Company_Handbook.md)

| Category | Auto-Approve | Approval Required |
|----------|-------------|-------------------|
| Email to known contact | Yes | New contacts |
| Payment | < $50 | > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Read, create | Delete, external move |

### Error Handling

```
Action fails
   ↓
Log error to /Logs
   ↓
If transient: Retry with exponential backoff
If auth error: Alert human, pause operations
If data error: Quarantine + alert
   ↓
Human investigates logs
   ↓
Correct issue, resume
```

---

## 📊 Audit & Monitoring

### Logging

Every action logged to `/Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-02-22T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "status": "success",
  "approval_status": "auto_approved",
  "target": "client_a@example.com"
}
```

### Monitoring Points

**Real-time (Dashboard.md)**
- Pending messages count
- System status
- Last update timestamp

**Daily Review**
- Check /Pending_Approval folder
- Verify all actions logged
- Check for errors

**Weekly Review**
- Analyze /Logs files
- Review auto-approval patterns
- Audit financial transactions
- Check watcher uptime

---

## 🔧 System Components

### Files

```
scripts/
├── base_watcher.py          # Abstract watcher class
├── gmail_watcher.py         # Gmail monitor (working)
├── filesystem_watcher.py    # File monitor (implemented)
└── credentials.json         # Google OAuth (not in repo)

Skills/
├── SKILL_BasicProcessing.md
├── SKILL_GmailWatcher.md
└── SKILL_VaultReadWrite.md

Vault/
├── Dashboard.md             # KPI dashboard
├── Company_Handbook.md      # Rules & policies
├── Plan.md                  # Processing plans
├── README.md                # Setup instructions
├── ARCHITECTURE.md          # This file
└── Logs/
    ├── AUDIT_LOG_TEMPLATE.md
    └── [YYYY-MM-DD.json]    # Daily logs
```

### External Services

- **Gmail API**: Email monitoring (OAuth 2.0)
- **Claude Code**: Task reasoning and execution
- **Obsidian**: Local vault storage

---

## 🚀 Process Management

### Running Watchers

**Option 1: Manual Terminal**
```bash
python3 scripts/gmail_watcher.py credentials.json /path/to/vault
python3 scripts/filesystem_watcher.py /path/to/vault Drop
```

**Option 2: PM2 (Recommended)**
```bash
pm2 start scripts/gmail_watcher.py --interpreter python3
pm2 start scripts/filesystem_watcher.py --interpreter python3
pm2 save
```

**Option 3: Custom Watchdog** (from hackathon doc)
```bash
python3 scripts/watchdog.py
```

### Startup Flow

```
System boots
   ↓
Launch PM2 (or watchdog.py)
   ↓
Start Gmail Watcher
   ↓
Start File System Watcher
   ↓
Watchers poll every N seconds
   ↓
On update: Create action file in /Needs_Action
   ↓
Human runs: claude "use basic-processing-loop"
   ↓
Claude processes all pending tasks
```

---

## 🎯 Tier Progression

### Bronze ✓ (Current)
- [x] Single watcher (Gmail)
- [x] File system monitoring
- [x] Claude reasoning loop
- [x] Human-in-the-loop approval
- [x] Dashboard & logging
- [x] Company rules engine

### Silver (Next)
- [ ] Multiple watchers (WhatsApp, LinkedIn)
- [ ] MCP servers for external actions
- [ ] Scheduled tasks (cron)
- [ ] Social media posting
- [ ] Advanced scheduling

### Gold (Advanced)
- [ ] Cross-domain integration
- [ ] Odoo accounting system
- [ ] Multiple social platforms
- [ ] Weekly business briefings
- [ ] Advanced automation (Ralph Wiggum loop)

### Platinum (Production)
- [ ] Cloud deployment (24/7)
- [ ] Multi-agent coordination
- [ ] Vault synchronization
- [ ] A2A messaging
- [ ] Full business autonomy

---

## 🔐 Security Architecture

### Credential Management
- **NEVER** store in plaintext
- **USE**: Environment variables
- **USE**: System keychains
- **ROTATE**: Monthly

### Local-First Design
- All data stays on machine
- No cloud processing of personal data
- Logs stored locally
- No third-party access to vault

### Approval-Based Safety
- Critical actions require human sign-off
- Two-phase execution (plan + approve)
- Full audit trail
- Easy rollback via file deletion

---

## 📈 Scalability Notes

**Current (Bronze):**
- Single machine execution
- Sequential processing
- ~100 emails/day capacity
- Real-time file monitoring

**Silver+ (Future):**
- Parallel processing (multiple agents)
- Multi-machine coordination (cloud + local)
- 1000+ emails/day capacity
- Advanced task scheduling
- Load balancing

---

## 📚 Key Concepts

**Watcher**: Daemon process monitoring external source
**Action File**: Markdown file triggering AI processing
**Plan**: Claude-generated execution steps with checkboxes
**Approval**: File move mechanism for human sign-off
**Skill**: Documented, reusable automation pattern
**Handbook**: Company policy rules for AI decision-making
**Ralph Wiggum Loop**: Self-iterating task completion pattern (Silver+)

---

## 🎓 Design Decisions

### Why File-Based?
- Simple, auditable, version-controllable
- Works with Obsidian without special plugins
- Easy to backup and restore
- Human-readable (Markdown format)

### Why Local-First?
- Privacy: No data sent to cloud
- Speed: No network latency
- Control: You own your data
- Cost: No recurring fees

### Why Markdown?
- Human-readable
- Git-friendly
- No database required
- Works with any editor

### Why Claude Code?
- State-of-the-art reasoning
- Can write/modify its own prompts
- Accesses vault via filesystem tools
- Supports agent skills framework

---

## 🔗 Related Documents

- **README.md** - Setup and usage guide
- **Company_Handbook.md** - Rules and policies
- **Dashboard.md** - Real-time KPIs
- **Logs/AUDIT_LOG_TEMPLATE.md** - Log format reference

---

**Architecture v1.0 - Bronze Tier Complete**
*Last Updated: 2026-02-22*