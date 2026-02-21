---
name: Gmail Watcher Processing Plan
created: 2026-02-18T02:30:00
---

# Processing Plan for TEST_EMAIL_001.md

## Email Analysis
- **From:** client@example.com
- **Subject:** Urgent Payment Request
- **Received:** 2026-02-18T02:00:00
- **Priority:** High (contains "ASAP" - matches urgent email criteria)
- **Status:** Pending

## Content Summary
Client requesting invoice for last month's services urgently.

## Rule Checks (Company_Handbook.md)
- ✓ Urgent email detected (contains "ASAP") - PRIORITIZE
- ✓ Payment-related - May need approval if amount > $500
- ✓ Maintain polite communication

## Suggested Actions
- [ ] Reply with invoice draft (polite tone per handbook)
- [ ] Check bank balance before sending
- [ ] Archive after processing

## Processing Status
- Email type: email
- Processing skill: gmail-watcher-processor
- Next: basic-processing-loop (move to /Done after action)
