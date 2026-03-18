# AI Employee Vault - Bronze Tier Implementation

> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

**Status:** Bronze Tier ✓ Complete
**Last Updated:** 2026-02-22
**Version:** 1.0

---

## 📋 What is the AI Employee Vault?

The AI Employee Vault is an autonomous agent that:
- Monitors Gmail and file system for incoming tasks
- Uses Claude Code to analyze and prioritize work
- Creates execution plans with human-in-the-loop approval
- Moves completed tasks to archive
- Maintains an audit log of all actions

Perfect for managing personal and business affairs 24/7.

---

## ✅ Bronze Tier Requirements

All Bronze tier requirements have been implemented:

| Requirement | Status | Details |
|------------|--------|---------|
| Obsidian vault | ✓ Done | Dashboard.md, Company_Handbook.md created |
| Gmail Watcher | ✓ Done | scripts/gmail_watcher.py with OAuth integration |
| File System Watcher | ✓ Done | scripts/filesystem_watcher.py watches Drop folder |
| Claude Code integration | ✓ Done | Reads/writes vault, executes basic-processing-loop |
| Folder structure | ✓ Done | /Needs_Action, /Done, /Logs, /Plans, /Pending_Approval |
| Agent Skills | ✓ Done | SKILL_BasicProcessing.md, SKILL_GmailWatcher.md |

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install required software
- Claude Code (Pro subscription or Free with Gemini API router)
- Obsidian v1.10.6+ (free)
- Python 3.13+
- Node.js v24+ LTS
- Git

# Install Python dependencies
cd scripts
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client watchdog
```

### Initial Setup

1. **Open Obsidian**
   ```
   File → Open vault folder → Select this directory
   ```

2. **Configure Gmail API**
   ```bash
   # Follow: https://developers.google.com/gmail/api/quickstart/python
   # Save credentials.json to scripts/
   ```

3. **Start Gmail Watcher**
   ```bash
   cd scripts
   python3 gmail_watcher.py credentials.json /path/to/vault
   ```

4. **Start File System Watcher (optional)**
   ```bash
   cd scripts
   python3 filesystem_watcher.py /path/to/vault Drop
   ```

5. **Test Basic Processing Loop**
   ```bash
   cd /path/to/vault
   claude "Use basic-processing-loop: Process everything in /Needs_Action"
   ```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md                 # Real-time KPI dashboard
├── Company_Handbook.md          # Rules of engagement
├── Plan.md                      # Current processing plan
├── Needs_Action/                # Incoming tasks from watchers
├── Plans/                       # Claude-generated execution plans
├── Done/                        # Completed tasks (archive)
├── Logs/                        # Audit trail
├── Pending_Approval/            # Human review queue
│   ├── Approved/               # Approved actions (execute)
│   └── Rejected/               # Rejected actions (log)
├── Skills/                      # Agent Skills documentation
│   ├── SKILL_BasicProcessing.md
│   ├── SKILL_GmailWatcher.md
│   └── SKILL_VaultReadWrite.md
└── scripts/                     # Watcher and utility scripts
    ├── base_watcher.py         # Abstract base class
    ├── gmail_watcher.py        # Gmail monitor
    ├── filesystem_watcher.py   # Drop folder monitor
    └── credentials.json        # Google OAuth (DO NOT COMMIT)
```

---

## 🔄 How It Works

### 1️⃣ Perception (Watchers)
Lightweight Python scripts monitor your inputs:
- **Gmail Watcher**: Monitors unread, important emails
- **File System Watcher**: Monitors Drop folder for file uploads

### 2️⃣ Reasoning (Claude Code)
Claude analyzes incoming tasks:
- Reads files from /Needs_Action
- Evaluates against Company_Handbook.md rules
- Creates Plan.md with execution steps
- Identifies items needing human approval

### 3️⃣ Action (Human-in-the-Loop)
For sensitive actions, Claude creates approval files:
- `/Pending_Approval/ACTION_*.md`
- You review and move to `/Approved` folder
- System executes the approved action

### 4️⃣ Completion
- Moves executed tasks to /Done
- Updates Dashboard.md
- Logs all actions to Logs/

---

## 💡 Usage Examples

### Example 1: Process All Pending Emails
```bash
claude "Use basic-processing-loop: Process everything in /Needs_Action"
```

Expected output:
- Analyzes all email files
- Creates processing plans
- Moves completed items to Done
- Updates Dashboard.md

### Example 2: Create a Financial Plan
Create a file in Needs_Action:
```markdown
---
type: finance
action: categorize_transactions
---

Please categorize my transactions for January 2026
```

Claude will:
- Analyze your transaction history
- Create category breakdown
- Generate financial report
- Flag unusual patterns

---

## 🔐 Security Best Practices

### Credentials
- **NEVER commit** credentials.json or .env files
- Add to .gitignore immediately
- Rotate credentials monthly
- Use environment variables for API keys

Example .env:
```bash
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
```

### Data Protection
- Keep vault on encrypted disk
- All logs stored locally (90 day retention)
- No credentials logged or transmitted
- Regular security audits recommended

### Approval Requirements
Per Company_Handbook.md:
- All new payees require approval
- Payments > $100 require approval
- New email contacts require approval
- Irreversible actions always require approval

---

## 📊 Monitoring & Maintenance

### Daily Checklist
- [ ] Check Dashboard.md for alerts
- [ ] Review /Pending_Approval folder
- [ ] Process /Needs_Action items
- [ ] Monitor Logs/ for errors

### Weekly Tasks
- [ ] Review audit log (Logs/YYYY-MM-DD.json)
- [ ] Check watcher processes are running
- [ ] Verify no stuck items in /Plans
- [ ] Archive old Done/ items

### Monthly Tasks
- [ ] Rotate credentials
- [ ] Review security settings
- [ ] Update Company_Handbook.md as needed
- [ ] Generate business summary

---

## 🛠️ Extending Bronze Tier

### Add More Watchers
1. Extend `BaseWatcher` class
2. Implement `check_for_updates()`
3. Implement `create_action_file()`
4. Document in new SKILL file
5. Add to orchestrator

Example:
```python
class LinkedInWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your LinkedIn API calls here
        pass

    def create_action_file(self, item) -> Path:
        # Create markdown file
        pass
```

### Create Custom Skills
Skills are documented in Markdown:
```markdown
---
name: your-skill-name
description: What this skill does
when_to_use: When to invoke it
---

# Implementation details
...
```

---

## 📚 Learning Resources

From the hackathon document:
- Claude Code Features: https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows
- Obsidian Setup: https://help.obsidian.md/Getting+started
- Gmail API: https://developers.google.com/gmail/api/quickstart/python
- MCP Introduction: https://modelcontextprotocol.io/introduction

---

## 🚨 Troubleshooting

### Gmail Watcher Won't Start
```bash
# Check credentials
ls -la scripts/credentials.json

# Verify OAuth consent screen is verified
# Go to: https://console.cloud.google.com/apis/credentials

# Test connection
python3 -c "from googleapiclient.discovery import build; print('Gmail API OK')"
```

### Claude Code Can't Read Vault
```bash
# Run from vault directory
cd /path/to/AI_Employee_Vault
claude "ls /Needs_Action"

# Or specify path explicitly
claude --cwd=/path/to/AI_Employee_Vault "ls /Needs_Action"
```

### File System Watcher Not Detecting Files
```bash
# Create Drop folder
mkdir Drop

# Check watchdog installation
pip install watchdog --upgrade

# Run with verbose logging
python3 scripts/filesystem_watcher.py . Drop
```

---

## 📈 Next Steps: Silver Tier

Once Bronze tier is stable, upgrade to Silver tier:
- Add WhatsApp watcher (Playwright-based)
- Implement MCP servers (email, browser actions)
- Create LinkedIn posting automation
- Add cron-based scheduled tasks
- Implement approval workflow UI

See: https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI

---

## 📝 Documentation Files

- **Company_Handbook.md**: Rules and policies for AI decision-making
- **Dashboard.md**: Real-time KPIs and status
- **Plan.md**: Current processing plans and checkpoints
- **Skills/**: Individual skill documentation
- **Logs/**: Audit trail of all actions

---

## 🤝 Contributing

To improve this implementation:
1. Test new features thoroughly
2. Document in appropriate SKILL file
3. Update Company_Handbook.md if adding new rules
4. Log all changes to Logs/
5. Keep vault structure clean

---

## ⚠️ Important Notes

- **You are responsible** for your AI Employee's actions
- All actions should be logged and reviewable
- High-risk actions (payments, communications) require approval
- Regular audits (daily/weekly) are essential
- This is experimental technology - use with caution

---

## 📞 Support

Questions or issues?
1. Check troubleshooting section above
2. Review log files in Logs/
3. Check Claude Code documentation
4. Join the weekly research meeting (Wednesdays 10 PM UTC)

---

**Made with ❤️ for the Personal AI Employee Hackathon 2026**

*Version 1.0 - Bronze Tier Complete*