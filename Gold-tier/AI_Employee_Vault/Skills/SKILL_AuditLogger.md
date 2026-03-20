---
name: audit-logger
description: Comprehensive audit logging for all actions in Gold Tier
when_to_use: After every action or on weekly review
---

## Description
Maintains complete audit trail of all AI Employee actions across all Gold Tier systems.
Every operation is logged with timestamp, skill name, result, and status. Supports
compliance, debugging, weekly reviews, and CEO Briefing generation.

## Instructions

### Log Structure
Each audit entry contains:
- **timestamp**: ISO 8601 format
- **skill**: Name of skill that performed action
- **action**: What was done
- **status**: success | failed | pending | skipped
- **result**: Output or error message
- **approval_status**: auto_approved | requires_approval | approved | rejected
- **metadata**: Additional context (IDs, amounts, platforms, etc.)

### Log Location
All logs saved to: `/Logs/audit_YYYY-MM-DD.json`

### Log Format
```json
[
  {
    "id": "audit_0001",
    "timestamp": "2026-03-20T10:30:00Z",
    "skill": "odoo-accounting",
    "action": "create_invoice",
    "status": "success",
    "result": "Invoice #42 created",
    "approval_status": "auto_approved",
    "metadata": {
      "invoice_id": 42,
      "customer_id": 5,
      "amount": 1500.00
    }
  },
  {
    "id": "audit_0002",
    "timestamp": "2026-03-20T11:00:00Z",
    "skill": "social-media-manager",
    "action": "create_facebook_post",
    "status": "pending_approval",
    "result": "SOCIAL_FACEBOOK_20260320_110000.md created",
    "approval_status": "requires_approval",
    "metadata": {
      "platform": "facebook",
      "file": "SOCIAL_FACEBOOK_20260320_110000.md"
    }
  }
]
```

## Implementation

### Core Logger Class
```python
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class AuditLogger:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.logs_path = vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)
    
    def _get_today_file(self) -> Path:
        today = datetime.now().strftime('%Y-%m-%d')
        return self.logs_path / f'audit_{today}.json'
    
    def log(self,
            skill: str,
            action: str,
            status: str,
            result: str = None,
            approval_status: str = 'auto_approved',
            metadata: Dict[str, Any] = None) -> str:
        """Log an action to daily audit file"""
        
        # Load existing entries
        audit_file = self._get_today_file()
        if audit_file.exists():
            entries = json.loads(audit_file.read_text())
        else:
            entries = []
        
        # Create new entry
        entry = {
            'id': f'audit_{len(entries) + 1:04d}',
            'timestamp': datetime.now().isoformat(),
            'skill': skill,
            'action': action,
            'status': status,
            'result': result,
            'approval_status': approval_status,
            'metadata': metadata or {}
        }
        
        entries.append(entry)
        
        # Save
        audit_file.write_text(json.dumps(entries, indent=2))
        
        return entry['id']
```

### Weekly Summary Generator
```python
def generate_weekly_summary(self, week_start: datetime) -> Dict[str, Any]:
    """Generate summary for the week"""
    
    entries = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        file = self.logs_path / f'audit_{date.strftime("%Y-%m-%d")}.json'
        if file.exists():
            entries.extend(json.loads(file.read_text()))
    
    # Aggregate statistics
    summary = {
        'period': f'{week_start.strftime("%Y-%m-%d")} to {(week_start + timedelta(days=6)).strftime("%Y-%m-%d")}',
        'total_actions': len(entries),
        'by_status': {},
        'by_skill': {},
        'by_action': {},
        'approval_stats': {
            'auto_approved': 0,
            'requires_approval': 0,
            'approved': 0,
            'rejected': 0
        },
        'errors': [],
        'success_rate': 0
    }
    
    # Count by category
    for entry in entries:
        status = entry.get('status', 'unknown')
        summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
        
        skill = entry.get('skill', 'unknown')
        summary['by_skill'][skill] = summary['by_skill'].get(skill, 0) + 1
        
        action = entry.get('action', 'unknown')
        summary['by_action'][action] = summary['by_action'].get(action, 0) + 1
        
        approval = entry.get('approval_status', 'unknown')
        if approval in summary['approval_stats']:
            summary['approval_stats'][approval] += 1
        
        if entry.get('status') == 'failed':
            summary['errors'].append({
                'id': entry['id'],
                'skill': entry['skill'],
                'action': entry['action'],
                'error': entry.get('result')
            })
    
    # Calculate success rate
    success_count = summary['by_status'].get('success', 0)
    summary['success_rate'] = (success_count / len(entries) * 100) if entries else 0
    
    return summary
```

## Integration with SKILL_ErrorRecovery

```python
def log_with_recovery(operation, skill, action, metadata=None):
    """Execute operation and log with error recovery"""
    audit_logger = AuditLogger(vault_path)
    
    try:
        result = operation()
        
        # Log success
        audit_logger.log(
            skill=skill,
            action=action,
            status='success',
            result=str(result),
            approval_status='auto_approved',
            metadata=metadata
        )
        
        return result
        
    except Exception as e:
        # Log failure
        audit_logger.log(
            skill=skill,
            action=action,
            status='failed',
            result=str(e),
            approval_status='requires_review',
            metadata={**metadata, 'error_type': type(e).__name__} if metadata else {'error_type': type(e).__name__}
        )
        
        # Trigger error recovery
        from skill_error_recovery import ErrorRecovery
        recovery = ErrorRecovery(vault_path)
        recovery.handle(error=e, operation=action, data=metadata)
        
        raise
```

## Integration with Gold Tier Skills

### SKILL_OdooAccounting
```python
# After creating invoice
audit_logger.log(
    skill='odoo-accounting',
    action='create_invoice',
    status='success',
    result=f'Invoice #{invoice_id} created',
    approval_status='auto_approved',
    metadata={
        'invoice_id': invoice_id,
        'customer_id': customer_id,
        'amount': amount
    }
)
```

### SKILL_SocialMediaManager
```python
# After creating social post
audit_logger.log(
    skill='social-media-manager',
    action=f'create_{platform}_post',
    status='pending_approval',
    result=f'{filename} created',
    approval_status='requires_approval',
    metadata={
        'platform': platform,
        'file': filename,
        'content_hash': content_hash
    }
)
```

### SKILL_CEOBriefing
```python
# After generating briefing
audit_logger.log(
    skill='ceo-briefing',
    action='generate_ceo_briefing',
    status='success',
    result=f'CEO_Briefing_{date}.md created',
    approval_status='auto_approved',
    metadata={
        'period': 'weekly',
        'generated_at': datetime.now().isoformat()
    }
)
```

### SKILL_ErrorRecovery
```python
# After recovery attempt
audit_logger.log(
    skill='error-recovery',
    action='retry_operation',
    status='success' if recovered else 'failed',
    result='Operation recovered' if recovered else 'Fallback to approval',
    approval_status='auto_approved',
    metadata={
        'original_skill': original_skill,
        'original_action': original_action,
        'recovery_attempts': attempts
    }
)
```

## Usage Prompt
Invoke audit-logger: Log last action and generate weekly report

## Parameters
- skill: string (required)
- action: string (required)
- status: success|failed|pending|skipped (required)
- result: string (optional)
- approval_status: auto_approved|requires_approval|approved|rejected
- metadata: dict (optional)
- generate_weekly: true|false

## Output Files

### Daily Audit Log
`/Logs/audit_YYYY-MM-DD.json`

### Weekly Summary
`/Logs/weekly_summary_YYYY-Www.json`

### Monthly Compliance Report
`/Logs/compliance_YYYY-MM.json` (on request)

## Dashboard Integration

```markdown
## 📊 Audit Summary (Today)
- Total Actions: 47
- Success Rate: 98%
- Pending Approvals: 3
- Errors: 1

## 📈 This Week
- Total Actions: 312
- Success Rate: 97.5%
- Top Skill: odoo-accounting (45%)
- Most Common: create_invoice (28%)
```

## Query Examples

### Find all actions by skill
```bash
python scripts/audit_query.py --skill odoo-accounting --date 2026-03-20
```

### Find all errors
```bash
python scripts/audit_query.py --status failed --date 2026-03-20
```

### Find pending approvals
```bash
python scripts/audit_query.py --approval requires_approval
```

### Generate weekly report
```bash
python scripts/audit_query.py --weekly-summary --week 2026-W12
```

## Log Retention
- **Daily logs**: 90 days
- **Weekly summaries**: 1 year
- **Compliance reports**: 7 years (if enabled)

## Gold Tier Status
✅ Daily JSON audit logs - Complete
✅ Weekly summary generation - Complete
✅ All skills integrated - Complete
✅ Error recovery integration - Complete
✅ Dashboard summary - Complete
