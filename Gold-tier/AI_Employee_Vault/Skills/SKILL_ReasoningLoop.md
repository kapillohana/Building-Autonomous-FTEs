---
name: reasoning-loop
description: Full Gold Tier autonomous cycle - coordinates Odoo, CEO Briefing, Social Media, Error Recovery, and Audit Logging in weekly run
when_to_use: Weekly autonomous cycle (Sunday night/Monday morning) or when complex multi-system tasks needed
---

# SKILL: Reasoning Loop - Gold Tier Complete

## Description
Full autonomous weekly cycle coordinating all Gold Tier systems:
1. **Odoo Accounting** - Invoices, revenue, financial data
2. **CEO Briefing** - Monday morning executive summary
3. **Social Media** - Facebook, Instagram, Twitter posting
4. **Error Recovery** - Retry, fallback, human alert
5. **Audit Logging** - Complete trail of all actions

Uses Ralph Wiggum persistence loop across all domains until complete.

## Weekly Autonomous Cycle

### Phase 1: Data Collection (Sunday 11 PM)
```
1. Scan /Needs_Action for pending items
2. Scan Gmail for unread important emails
3. Scan WhatsApp for new messages
4. Scan LinkedIn for engagement
5. Load Odoo financial data
```

### Phase 2: Processing & Planning (Sunday 11:30 PM)
```
1. Create /Plans/Weekly_Plan_{date}.md
2. Categorize tasks by type:
   - Financial → Odoo MCP
   - Communications → Email/WhatsApp
   - Social → FB/IG/Twitter
   - Executive → CEO Briefing
3. Set checkboxes for each task
```

### Phase 3: Execution (Monday 12 AM - 6 AM)
```
1. Financial Operations
   - Create pending invoices
   - Record payments
   - Generate revenue report
   
2. Communications
   - Reply to urgent emails
   - Respond to WhatsApp messages
   - Engage on LinkedIn
   
3. Social Media Posting
   - Generate posts from Business_Goals.md
   - Post to Facebook
   - Post to Instagram
   - Post to Twitter/X
   
4. CEO Briefing Generation
   - Fetch Odoo data
   - Generate weekly summary
   - Save to /Briefings/
   - Log to audit trail
```

### Phase 4: Error Recovery (Throughout)
```
1. On any failure:
   - Retry (3 attempts, exponential backoff)
   - If still failing → dry-run fallback
   - Create approval file
   - Alert via Dashboard if critical
   
2. Log all recovery attempts
3. Track success rates
```

### Phase 5: Audit & Completion (Monday 6 AM)
```
1. Log all actions to audit_YYYY-MM-DD.json
2. Generate weekly summary
3. Update Dashboard.md
4. Archive completed tasks to /Done
5. Mark Weekly Plan as complete
```

## Integration Matrix

| Component | Trigger | Output | Audit |
|-----------|---------|--------|-------|
| Odoo MCP | Financial task | Invoices, Revenue | ✅ |
| CEO Briefing | Weekly schedule | Briefing doc | ✅ |
| Facebook | Content ready | Post + summary | ✅ |
| Instagram | Content ready | Post + summary | ✅ |
| Twitter/X | Content ready | Thread + summary | ✅ |
| Error Recovery | Any failure | Approval file | ✅ |
| Audit Logger | Every action | JSON log | N/A |

## Usage Prompt
Invoke reasoning-loop: Run full Gold Tier weekly autonomous cycle with Odoo, CEO Briefing, Social Media, Error Recovery, and Audit Logging

## Parameters
- cycle_type: weekly (default) | on_demand
- include_odoo: true
- include_social: true
- include_briefing: true
- include_audit: true
- dry_run: false

## Ralph Wiggum Persistence Loop

```python
def reasoning_loop():
    """Continue until all tasks complete across all systems"""
    
    max_iterations = 100  # Safety limit
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Check all systems
        needs_action_count = len(list(NEEDS_ACTION.glob('*.md')))
        pending_approval_count = len(list(PENDING_APPROVAL.glob('*.md')))
        plans_in_progress = get_incomplete_plans()
        
        # Check Odoo operations
        odoo_pending = check_odoo_pending()
        
        # Check social media queue
        social_pending = check_social_pending()
        
        # Check if all complete
        if (needs_action_count == 0 and 
            pending_approval_count == 0 and
            len(plans_in_progress) == 0 and
            odoo_pending == 0 and
            social_pending == 0):
            logger.info("All systems complete - exiting loop")
            break
        
        # Process pending items
        process_needs_action()
        process_pending_approvals()
        process_odoo_tasks()
        process_social_posts()
        
        # Update plan
        update_plan_checkboxes()
        
        # Log progress
        audit_logger.log_action(
            action_type='reasoning_loop_iteration',
            actor='reasoning-loop',
            status='in_progress',
            details={'iteration': iteration, 'remaining': needs_action_count}
        )
        
        time.sleep(30)  # Cooldown between iterations
    
    # Final summary
    generate_cycle_summary()
```

## Weekly Cycle Command

```bash
# Full weekly autonomous cycle
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\AI_Employee_Vault\scripts

# Run reasoning loop with all Gold Tier components
python reasoning_loop.py --weekly --odoo --social --briefing --audit
```

## Error Recovery Integration

```python
def execute_with_recovery(operation, actor, details):
    """Execute with full error recovery"""
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = operation()
            
            # Log success
            audit_logger.log_action(
                action_type=operation.__name__,
                actor=actor,
                status='success',
                details=details
            )
            
            return result
            
        except Exception as e:
            if attempt == max_retries - 1:
                # All retries failed - dry-run fallback
                approval_file = create_approval_file(operation.__name__, details, e)
                
                audit_logger.log_action(
                    action_type=operation.__name__,
                    actor=actor,
                    status='pending_approval',
                    target=str(approval_file),
                    error=str(e),
                    recovery_attempts=max_retries
                )
                
                # Alert via Dashboard if critical
                if is_critical_error(e):
                    update_dashboard_alert(actor, e, severity='CRITICAL')
                
                return None
            
            # Retry with backoff
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
```

## Audit Logging Integration

Every action in the reasoning loop is logged:

```python
# At start of cycle
audit_logger.log_action(
    action_type='weekly_cycle_start',
    actor='reasoning-loop',
    status='started',
    details={'cycle_type': 'weekly', 'timestamp': datetime.now().isoformat()}
)

# For each Odoo operation
audit_logger.log_action(
    action_type='odoo_create_invoice',
    actor='odoo-mcp',
    status='success',
    target=f'Invoice #{invoice_id}',
    details={'customer_id': customer_id, 'amount': amount}
)

# For each social post
audit_logger.log_action(
    action_type='social_post',
    actor='facebook-watcher',
    status='success',
    target='SOCIAL_FACEBOOK_*.md',
    details={'platform': 'facebook', 'posted': True}
)

# For CEO Briefing
audit_logger.log_action(
    action_type='ceo_briefing_generated',
    actor='odoo-mcp',
    status='success',
    target='CEO_Briefing_*.md',
    details={'period': 'weekly', 'generated_at': datetime.now().isoformat()}
)

# At end of cycle
audit_logger.log_action(
    action_type='weekly_cycle_complete',
    actor='reasoning-loop',
    status='completed',
    details={
        'duration_minutes': duration,
        'tasks_completed': total_tasks,
        'errors_recovered': error_count
    }
)
```

## Output Files

### Weekly Plan
`/Plans/Weekly_Plan_YYYY-MM-DD.md`

### CEO Briefing
`/Briefings/CEO_Briefing_YYYY-MM-DD.md`

### Social Posts
- `/Pending_Approval/SOCIAL_FACEBOOK_*.md`
- `/Pending_Approval/SOCIAL_INSTAGRAM_*.md`
- `/Pending_Approval/SOCIAL_TWITTER_*.md`

### Audit Log
`/Logs/audit_YYYY-MM-DD.json`

### Weekly Summary
`/Logs/weekly_summary_YYYY-Www.json`

### Dashboard Update
`/Dashboard.md` (KPIs refreshed)

## Gold Tier Status

✅ Odoo Accounting Integration - Complete
✅ CEO Briefing Generation - Complete
✅ Facebook Posting - Complete
✅ Instagram Posting - Complete
✅ Twitter/X Posting - Complete
✅ Error Recovery System - Complete
✅ Audit Logging - Complete
✅ Ralph Wiggum Persistence - Complete
✅ Weekly Autonomous Cycle - Complete

## Final Test Command

```bash
# Simulate full weekly autonomous cycle
cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\AI_Employee_Vault\scripts

python reasoning_loop.py --weekly --test
```

This runs the complete Gold Tier cycle in test mode:
- ✅ Odoo data fetch (CEO Briefing)
- ✅ Social media post generation (FB, IG, Twitter)
- ✅ Error recovery simulation
- ✅ Audit log creation
- ✅ Dashboard update
- ✅ Weekly summary generation
