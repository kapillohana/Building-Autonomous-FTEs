---
name: scheduler
description: Manages scheduled/cron-based tasks
when_to_use: For recurring tasks (daily posts, weekly reports, reminders)
---

# SKILL: Scheduler

## Description
Manages scheduled/cron-based tasks.

## Instructions
- Read Schedule.md for recurring task definitions
- Check if current time matches any scheduled task
- Trigger appropriate skill (linkedin-sales, report-generation, etc.)
- Log execution time and result

## Usage Prompt
Invoke scheduler: Check and execute any due scheduled tasks

## Parameters
check_interval: 60 seconds

## Schedule Format (Schedule.md)
```markdown
| Task | Skill | Frequency | Time | Status |
|------|-------|-----------|------|--------|
| LinkedIn Post | linkedin-sales | Daily | 09:00 | Active |
| Weekly Report | weekly-briefing | Weekly | Monday 18:00 | Active |
```
