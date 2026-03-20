# Gold Tier - Autonomous Employee

**Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

---

## Overview

Gold Tier is the complete autonomous AI employee system. It builds on Silver Tier with full Odoo ERP integration, multi-platform social media automation, weekly CEO Briefings, comprehensive error recovery, and complete audit logging.

**Status:** ✅ **COMPLETE**

---

## ✨ Completed Features

### Core Systems
- [x] **Odoo ERP Integration** - Full accounting via JSON-RPC MCP
- [x] **Gmail Watcher** - Auto-process unread important emails
- [x] **WhatsApp Watcher** - Message monitoring and responses
- [x] **LinkedIn Watcher** - Sales post automation
- [x] **Facebook/Instagram Watcher** - Multi-platform posting
- [x] **Twitter/X Watcher** - Thread creation and posting

### Automation
- [x] **Weekly CEO Briefing** - Auto-generated Monday morning reports
- [x] **Social Media Manager** - Unified posting across 3 platforms
- [x] **Error Recovery System** - 3-retry + fallback + Dashboard alerts
- [x] **Audit Logger** - Complete trail of all actions

### Intelligence
- [x] **Reasoning Loop** - Multi-system coordination with persistence
- [x] **Approval Workflow** - Human-in-the-loop enforcement
- [x] **Dashboard** - Real-time KPI monitoring

---

## 🚀 How to Run the Full System

### Prerequisites
```bash
# Software required
- Python 3.13+
- Odoo 19 (Docker)
- Node.js v24+ LTS
- Claude Code

# Python dependencies
pip install google-auth-oauthlib google-api-python-client watchdog playwright
playwright install chromium
```

### 1. Start Odoo ERP
```bash
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\odoo
docker-compose up -d
```

### 2. Run Individual Components

**Odoo MCP (Accounting):**
```bash
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\AI_Employee_Vault\scripts
python odoo_mcp.py
```

**Gmail Watcher:**
```bash
python gmail_watcher.py
```

**Social Media (Test Mode):**
```bash
python facebook_instagram_watcher.py --test
python twitter_watcher.py --test
```

### 3. Full Weekly Autonomous Cycle

**Using Claude Code:**
```bash
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\AI_Employee_Vault
claude "Use reasoning-loop: Run full Gold Tier weekly autonomous cycle with Odoo, CEO Briefing, Social Media, Error Recovery, and Audit Logging"
```

**Manual Full Test:**
```bash
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\AI_Employee_Vault\scripts
python odoo_mcp.py && python facebook_instagram_watcher.py --test && python twitter_watcher.py --test
```

---

## 📁 Folder Structure

```
Gold-tier/
├── AI_Employee_Vault/
│   ├── Dashboard.md              # Real-time KPIs
│   ├── Company_Handbook.md       # Rules of engagement (Gold Tier v2.0)
│   ├── Skills/                   # All skill documentation
│   │   ├── SKILL_OdooAccounting.md
│   │   ├── SKILL_SocialMediaManager.md
│   │   ├── SKILL_ErrorRecovery.md
│   │   ├── SKILL_AuditLogger.md
│   │   └── SKILL_ReasoningLoop.md
│   ├── Needs_Action/             # Incoming tasks
│   ├── Pending_Approval/         # Human review queue
│   ├── Done/                     # Completed tasks archive
│   ├── Logs/                     # Audit trails
│   └── scripts/                  # All watchers
│       ├── odoo_mcp.py
│       ├── gmail_watcher.py
│       ├── facebook_instagram_watcher.py
│       ├── twitter_watcher.py
│       └── ...
├── odoo/                         # Odoo Docker setup
└── mcp/                          # MCP servers
```

---

## 📊 Gold Tier Capabilities

| Capability | Status | Details |
|------------|--------|---------|
| Odoo Accounting | ✅ | Invoices, customers, revenue, CEO Briefing |
| Email Processing | ✅ | Gmail watcher with OAuth |
| WhatsApp | ✅ | Message monitoring |
| LinkedIn | ✅ | Sales post automation |
| Facebook | ✅ | Business page posting |
| Instagram | ✅ | Feed posting |
| Twitter/X | ✅ | Thread creation |
| CEO Briefing | ✅ | Weekly auto-generation |
| Error Recovery | ✅ | 3-retry + fallback + alerts |
| Audit Logging | ✅ | Daily JSON + weekly summary |

---

## 🔐 Security

- All credentials via environment variables (.env file)
- Session persistence with secure storage
- Human-in-the-loop for all sensitive actions
- Complete audit trail (90+ day retention)
- No credentials logged or transmitted

---

## 📈 Weekly Autonomous Cycle

**Schedule:** Sunday 11:00 PM - Monday 6:00 AM

1. **Data Collection** - Scan all inputs (email, WhatsApp, LinkedIn, social)
2. **Processing** - Create weekly plan with task categorization
3. **Execution** - Odoo operations, communications, social posting
4. **CEO Briefing** - Generate Monday morning executive summary
5. **Audit** - Log all actions, update Dashboard, archive to Done

---

## 🛠️ Configuration

### Environment Variables (.env)
```bash
# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_company
ODOO_USERNAME=admin@aiemployee.com
ODOO_PASSWORD=your_password

# Gmail
GMAIL_CREDENTIALS_PATH=scripts/credentials.json

# Social Media
FACEBOOK_EMAIL=your@email.com
FACEBOOK_PASSWORD=yourpassword
INSTAGRAM_EMAIL=your@email.com
INSTAGRAM_PASSWORD=yourpassword
TWITTER_EMAIL=your@email.com
TWITTER_PASSWORD=yourpassword
```

---

## 📝 Documentation

- **Dashboard.md** - Real-time system status and KPIs
- **Company_Handbook.md** - Rules of engagement (Gold Tier v2.0)
- **Skills/** - Individual skill documentation (18 skills)
- **Logs/** - Audit trails and summaries

---

## 🎯 Next Steps

Gold Tier is **complete** and operational.

**To activate:**
1. Set up .env with your credentials
2. Start Odoo Docker containers
3. Run weekly autonomous cycle via Claude Code
4. Review Dashboard.md daily
5. Process /Pending_Approval folder regularly

---

**Made with ❤️ for the Personal AI Employee Hackathon 2026**

*Gold Tier - Autonomous Employee - COMPLETE ✅*
