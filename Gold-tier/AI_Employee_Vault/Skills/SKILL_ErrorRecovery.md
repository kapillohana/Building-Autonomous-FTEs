---
name: error-recovery
description: Full error recovery system with retry logic, dry-run fallback, and human alert via Dashboard
when_to_use: On any operation failure or exception
---

## Description
Comprehensive error recovery system ensuring Gold Tier operations complete successfully
even when individual components fail. Implements multiple recovery strategies with
human-in-the-loop escalation.

## Recovery Strategies

### Level 1: Automatic Retry
- **Attempts**: 3 retries with exponential backoff
- **Delay**: 2s, 4s, 8s between attempts
- **Use Case**: Temporary network issues, API rate limits
- **Logging**: All retries logged to audit trail

### Level 2: Dry-Run Fallback
- **Trigger**: After 3 failed retries
- **Action**: Create approval file instead of executing
- **Use Case**: Authentication failures, permission issues
- **Output**: File in `/Pending_Approval/` for human review

### Level 3: Human Alert via Dashboard
- **Trigger**: Dry-run also fails or critical error
- **Action**: Update Dashboard.md with alert
- **Use Case**: Systemic failures, credential expiry
- **Visibility**: Immediate visibility on next Dashboard review

## Implementation

### Retry Decorator
```python
def retry_operation(operation, max_retries=3, base_delay=2):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
```

### Dry-Run Fallback
```python
def create_approval_file(operation_type, data, error):
    """Create approval file when auto-execution fails"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = PENDING_APPROVAL / f"RECOVERY_{operation_type}_{timestamp}.md"
    
    content = f"""---
type: error_recovery
original_operation: {operation_type}
created: {datetime.now().isoformat()}
status: pending_review
error: {str(error)}
---

# Manual Action Required

## Original Operation
{operation_type}

## Data
{json.dumps(data, indent=2)}

## Error Details
{str(error)}

---
**Action:** Review and execute manually, or move to Rejected/
"""
    filepath.write_text(content)
    return filepath
```

### Dashboard Alert
```python
def update_dashboard_alert(component, error, severity='HIGH'):
    """Add alert to Dashboard.md"""
    dashboard_path = VAULT_PATH / 'Dashboard.md'
    content = dashboard_path.read_text()
    
    alert = f"""
## 🚨 ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Component:** {component}
- **Severity:** {severity}
- **Error:** {str(error)}
- **Status:** Requires attention
"""
    
    # Insert after alerts section
    if '## 🚨 Alerts & Warnings' in content:
        content = content.replace('## 🚨 Alerts & Warnings', f'## 🚨 Alerts & Warnings\n{alert}')
    
    dashboard_path.write_text(content)
```

## Error Categories

### Transient Errors (Auto-Retry)
- Network timeouts
- API rate limits (429)
- Temporary service unavailability (503)
- Database connection timeouts

### Authentication Errors (Dry-Run)
- Expired sessions
- Invalid credentials
- Token refresh failures
- Permission denied

### Critical Errors (Human Alert)
- Data corruption detected
- Security violation
- Repeated failures (>5 attempts)
- System resource exhaustion

## Integration Points

### With Odoo MCP
```python
try:
    odoo.create_invoice(customer_id, amount, description)
except Exception as e:
    error_recovery.handle(e, operation='create_invoice', data={...})
```

### With Social Media Watchers
```python
try:
    post_to_twitter(thread)
except Exception as e:
    error_recovery.handle(e, operation='twitter_post', data={'thread': thread})
```

### With CEO Briefing
```python
try:
    briefing = odoo.generate_ceo_briefing()
except Exception as e:
    # Generate static briefing with error notice
    briefing = generate_fallback_briefing(e)
```

## Usage Prompt
Invoke error-recovery: Handle failed operation with retry, fallback to dry-run, alert via Dashboard

## Parameters
- max_retries: 3 (default)
- base_delay: 2 seconds
- fallback_to_dry_run: true
- alert_on_critical: true
- severity_threshold: HIGH

## Logging
All recovery actions logged to:
- `../logs/error_recovery.log` - Detailed recovery attempts
- `../logs/audit_YYYY-MM-DD.json` - Structured audit trail
- `Dashboard.md` - Human-visible alerts

## Metrics Tracked
- Total errors encountered
- Successful recoveries (retry)
- Successful recoveries (dry-run)
- Escalated to human
- Mean time to recovery
- Component failure rates

## Example Workflow

```
1. Operation: Post to Twitter
2. Error: Session expired
3. Retry 1: Failed (session still invalid)
4. Retry 2: Failed
5. Retry 3: Failed
6. Fallback: Create approval file SOCIAL_TWITTER_*.md
7. Log: Entry in audit_2026-03-20.json
8. Alert: Dashboard updated with Twitter posting failure
9. Human: Reviews approval file, moves to Approved/
10. Execute: Manual posting completes
```

## Configuration

### Environment Variables
```bash
# Error recovery settings
ERROR_RECOVERY_MAX_RETRIES=3
ERROR_RECOVERY_BASE_DELAY=2
ERROR_RECOVERY_LOG_LEVEL=INFO
ERROR_RECOVERY_ALERT_SEVERITY=HIGH
```

### Settings File
```json
{
  "error_recovery": {
    "enabled": true,
    "max_retries": 3,
    "base_delay_seconds": 2,
    "exponential_backoff": true,
    "dry_run_fallback": true,
    "dashboard_alerts": true,
    "alert_severity_threshold": "HIGH"
  }
}
```

## Testing

### Test Retry Logic
```bash
python scripts/error_recovery_test.py --test-retry
```

### Test Dry-Run Fallback
```bash
python scripts/error_recovery_test.py --test-fallback
```

### Test Dashboard Alert
```bash
python scripts/error_recovery_test.py --test-alert
```

## Gold Tier Status
✅ Automatic retry (3 attempts) - Complete
✅ Dry-run fallback - Complete
✅ Dashboard alerts - Complete
✅ Audit logging - Complete
✅ All integrations - Complete
