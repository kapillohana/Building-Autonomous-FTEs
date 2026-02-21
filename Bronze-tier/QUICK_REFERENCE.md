# Quick Reference Guide

**Bronze Tier AI Employee Vault**
Quick commands and workflows

---

## ⚡ Essential Commands

### Start Email Monitoring
```bash
cd scripts
python3 gmail_watcher.py credentials.json /path/to/vault
```

### Process All Pending Emails
```bash
cd /path/to/vault
claude "Use basic-processing-loop: Process everything in /Needs_Action"
```

### Start File Watcher
```bash
cd scripts
python3 filesystem_watcher.py /path/to/vault Drop
```

### View Dashboard
```bash
# Open in Obsidian or any editor
cat Dashboard.md
```

### Check Logs
```bash
# View today's log
tail -f Logs/2026-02-22.json

# View all logs
ls -la Logs/
```

---

## 📂 Folder Quick Map

| Folder | Purpose | Action |
|--------|---------|--------|
| `/Needs_Action` | New tasks arrive here | Claude processes |
| `/Plans` | Execution plans | Review, then approve |
| `/Pending_Approval` | Awaiting your approval | Move to `/Approved` or `/Rejected` |
| `/Approved` | Ready to execute | System processes |
| `/Done` | Completed & archived | Can be deleted |
| `/Logs` | Action history | For auditing |

---

## 🔄 Common Workflows

### Workflow 1: Email Processing
```
1. Email arrives in Gmail
   ↓
2. Gmail Watcher detects it
   ↓
3. Creates file in /Needs_Action
   ↓
4. Run: claude "Use basic-processing-loop"
   ↓
5. Claude processes and moves to /Done
   ↓
6. Done!
```

### Workflow 2: File Processing
```
1. Drop file in Drop/ folder
   ↓
2. File Watcher detects it
   ↓
3. Creates metadata in /Needs_Action
   ↓
4. Claude processes as email
   ↓
5. Move to /Done
```

### Workflow 3: Approval Workflow
```
1. Claude detects sensitive action
   ↓
2. Creates file in /Pending_Approval
   ↓
3. You review the file
   ↓
4. Move to /Approved (if yes) or /Rejected (if no)
   ↓
5. System executes or logs rejection
```

---

## 🎯 Key Files to Know

### Dashboard.md
- **What**: Real-time system status
- **Update Frequency**: After each processing loop
- **Check**: Daily for KPIs
- **Action**: Read-only (Claude updates it)

### Company_Handbook.md
- **What**: Rules and policies for AI decisions
- **Update Frequency**: As your rules change
- **Check**: When onboarding new employees
- **Action**: Edit to change AI behavior

### Plan.md
- **What**: Current processing task
- **Update Frequency**: During processing
- **Check**: When you want to see what's being processed
- **Action**: Can add notes/checkmarks

---

## 🚨 Approval Thresholds Quick Reference

From Company_Handbook.md:

### ✅ Auto-Approve
- Email to known contact
- Payment < $50 to known vendor
- Scheduled social media post
- Calendar event < 2 hours
- File read/create

### ⚠️ Requires Your Approval
- Email to NEW contact
- Payment > $100 (any payee)
- Direct message reply
- File deletion
- Anything unusual

---

## 🔍 Monitoring Commands

### Check System Status
```bash
# View real-time dashboard
cat Dashboard.md | head -30
```

### Count Pending Items
```bash
# Count items awaiting approval
ls /Pending_Approval | wc -l

# Count items to be processed
ls /Needs_Action | wc -l
```

### View Recent Actions
```bash
# Last 10 actions
tail -10 Logs/2026-02-22.json | jq '.[].action_type'

# All emails processed today
grep "action_type.*email" Logs/2026-02-22.json | wc -l
```

### Check Watcher Status
```bash
# Is Gmail watcher running?
ps aux | grep gmail_watcher

# Is file watcher running?
ps aux | grep filesystem_watcher
```

---

## 🛠️ Maintenance Checklist

### Daily
- [ ] Read Dashboard.md (2 min)
- [ ] Check /Pending_Approval folder (1 min)
- [ ] Process /Needs_Action (5 min)

### Weekly
- [ ] Review Logs/ (15 min)
- [ ] Check watcher uptime (5 min)
- [ ] Archive old /Done items (5 min)

### Monthly
- [ ] Review Company_Handbook.md rules (10 min)
- [ ] Check log file sizes (5 min)
- [ ] Rotate credentials (10 min)

---

## 🔐 Security Quick Check

### ✓ Do This
- Store API keys in environment variables
- Keep credentials.json out of git
- Review logs regularly
- Rotate credentials monthly
- Approve sensitive actions

### ✗ Don't Do This
- Commit .env files to git
- Store passwords in markdown
- Skip approval workflows
- Delete logs without backup
- Share vault with sensitive data

---

## 🚀 Fast Troubleshooting

### Gmail Watcher Not Detecting Emails
```bash
# Check if API credentials valid
python3 -c "from googleapiclient.discovery import build; print('OK')"

# Check if folder exists
ls -la credentials.json

# Test connection manually
python3 scripts/gmail_watcher.py credentials.json . &
sleep 5; kill %1
```

### Claude Can't Read Vault
```bash
# Run from vault directory
cd /path/to/vault

# Verify path works
ls /Needs_Action

# Test Claude
claude "ls /Needs_Action"
```

### File Watcher Not Working
```bash
# Create Drop folder if missing
mkdir Drop

# Check watchdog installed
pip show watchdog

# Verify folder permissions
ls -la Drop/
```

---

## 📚 Important File Locations

```
Vault Root:
  ├── README.md ......................... Start here
  ├── ARCHITECTURE.md ................... Technical details
  ├── Company_Handbook.md ............... Rules & policies
  ├── Dashboard.md ...................... System status

Scripts:
  └── scripts/
      ├── base_watcher.py .............. Template
      ├── gmail_watcher.py ............. Email monitor
      └── filesystem_watcher.py ........ File monitor

Configuration:
  └── scripts/
      └── credentials.json ............. Google OAuth (SECRET!)
```

---

## 🎯 What to Do Next

### Immediate (Today)
1. Read README.md
2. Set up Gmail API credentials
3. Start Gmail Watcher
4. Send yourself a test email

### This Week
1. Run basic-processing-loop
2. Process 10+ emails
3. Review Dashboard.md
4. Check Logs/

### This Month
1. Fine-tune Company_Handbook.md
2. Create custom skills
3. Add file watcher
4. Plan Silver tier features

---

## 📞 Getting Help

### Issues?
1. Check ARCHITECTURE.md for technical details
2. Check README.md troubleshooting section
3. Review Logs/ for error messages
4. Check Company_Handbook.md for policy questions

### Questions?
1. Post in research meeting (Wed 10 PM UTC)
2. Review related documentation
3. Test with simple examples

### Errors?
1. Check Logs/ folder
2. Read error message carefully
3. Search ARCHITECTURE.md
4. Review similar past logs

---

## 📊 One-Page Reference

```
STARTING UP:
python3 scripts/gmail_watcher.py credentials.json ./
cd vault && claude "Use basic-processing-loop"

FOLDER FLOW:
Gmail → /Needs_Action → Claude → /Done
Drop → /Needs_Action → Claude → /Done
Sensitive → /Pending_Approval → You → /Approved → /Done

CRITICAL FILES:
Company_Handbook.md    = Rules
Dashboard.md           = Status
Logs/                  = History
/Pending_Approval      = Your decisions

DAILY TASKS:
1. Check Dashboard.md
2. Approve items in /Pending_Approval
3. Run basic-processing-loop
4. Archive /Done items

MONTHLY:
1. Review Company_Handbook.md
2. Rotate credentials
3. Audit logs
4. Plan improvements
```

---

**Bronze Tier Quick Reference**
*Save this for fast lookups!*