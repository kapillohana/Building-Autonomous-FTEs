# Audit Log Template

This file serves as a reference for the JSON audit logs that track all AI Employee actions.

## Log File Naming Convention

```
Logs/YYYY-MM-DD.json
Logs/2026-02-22.json
```

## Log Entry Schema

Each action is logged as a JSON object with this structure:

```json
{
  "timestamp": "2026-02-22T02:37:00Z",
  "action_type": "email_send|file_move|task_complete|approval_required|error",
  "actor": "claude_code|gmail_watcher|filesystem_watcher",
  "status": "success|pending|failed|blocked",
  "priority": "critical|high|medium|low",
  "category": "communication|finance|task_management|system",
  "target": "file_path|email_address|recipient_name",
  "parameters": {
    "subject": "Email subject or action description",
    "amount": 0,
    "recipient": "user@example.com",
    "file_moved_from": "/Needs_Action/FILE.md",
    "file_moved_to": "/Done/FILE.md"
  },
  "approval_status": "auto_approved|pending_approval|approved|rejected|not_required",
  "approved_by": "human_user|system_rule|auto_rule",
  "approval_date": "2026-02-22T02:37:00Z",
  "result": "success|failure|exception",
  "error_message": null,
  "notes": "Additional context about the action"
}
```

## Action Types

### email_send
```json
{
  "action_type": "email_send",
  "target": "client@example.com",
  "parameters": {
    "subject": "Invoice #123",
    "recipient": "client@example.com",
    "body_preview": "Please find attached your invoice..."
  },
  "approval_status": "auto_approved"
}
```

### file_move
```json
{
  "action_type": "file_move",
  "target": "EMAIL_123456.md",
  "parameters": {
    "file_moved_from": "/Needs_Action/EMAIL_123456.md",
    "file_moved_to": "/Done/EMAIL_123456.md"
  },
  "status": "success"
}
```

### task_complete
```json
{
  "action_type": "task_complete",
  "target": "PLAN_process_emails.md",
  "parameters": {
    "task_name": "Process all emails",
    "items_completed": 10,
    "duration_seconds": 300
  },
  "status": "success"
}
```

### approval_required
```json
{
  "action_type": "approval_required",
  "target": "PAYMENT_Client_A_1500.md",
  "parameters": {
    "amount": 1500,
    "recipient": "Client A",
    "reason": "Invoice #123 payment"
  },
  "approval_status": "pending_approval",
  "approval_date": null
}
```

### error
```json
{
  "action_type": "error",
  "target": "gmail_watcher",
  "status": "failed",
  "error_message": "Gmail API connection timeout",
  "notes": "Retrying in 60 seconds"
}
```

## Example Daily Log

```json
[
  {
    "timestamp": "2026-02-22T08:00:00Z",
    "action_type": "task_complete",
    "actor": "claude_code",
    "status": "success",
    "priority": "high",
    "category": "task_management",
    "target": "basic-processing-loop",
    "parameters": {
      "task_name": "Process /Needs_Action",
      "items_processed": 10,
      "duration_seconds": 300
    },
    "approval_status": "not_required",
    "result": "success",
    "error_message": null,
    "notes": "10 emails processed and archived to /Done"
  },
  {
    "timestamp": "2026-02-22T10:30:00Z",
    "action_type": "approval_required",
    "actor": "claude_code",
    "status": "pending",
    "priority": "critical",
    "category": "finance",
    "target": "PAYMENT_NewVendor_500.md",
    "parameters": {
      "amount": 500,
      "recipient": "New Vendor Inc",
      "reason": "Software subscription"
    },
    "approval_status": "pending_approval",
    "approved_by": null,
    "result": "pending",
    "notes": "New vendor payment - requires human approval"
  },
  {
    "timestamp": "2026-02-22T11:00:00Z",
    "action_type": "email_send",
    "actor": "claude_code",
    "status": "success",
    "priority": "high",
    "category": "communication",
    "target": "known_client@example.com",
    "parameters": {
      "subject": "RE: Your Question",
      "recipient": "known_client@example.com"
    },
    "approval_status": "auto_approved",
    "approved_by": "auto_rule",
    "result": "success",
    "notes": "Reply to known contact auto-approved per handbook"
  }
]
```

## Retention Policy

- **Daily logs**: Retain for 90 days minimum
- **Weekly summaries**: Retain for 1 year
- **Error logs**: Retain indefinitely
- **Approved transactions**: Retain for 7 years (accounting purposes)

## Log Access & Review

### Daily Review
- Check for CRITICAL priority items
- Verify all approval_required items have been processed
- Check for errors in status="failed"

### Weekly Review
```bash
# Generate weekly summary
python3 scripts/analyze_logs.py --week 2026-02-17 --summary
```

### Monthly Audit
- Review all financial transactions
- Check approval patterns
- Analyze automation success rate
- Update policies if needed

## Security Notes

- Logs may contain sensitive information (emails, amounts, names)
- Store on encrypted disk
- Never share logs without redacting sensitive data
- Use secure backups for long-term retention
- Implement log rotation to manage file size

---

See: Dashboard.md for real-time summaries
See: Company_Handbook.md for approval thresholds