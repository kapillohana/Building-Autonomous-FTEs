---
name: linkedin-watcher
description: Monitors LinkedIn notifications and messages
when_to_use: When LinkedIn notifications or DMs arrive
---

# SKILL: LinkedIn Watcher

## Description
Monitors LinkedIn notifications and messages.

## Instructions
- Scan for new connection requests, messages, comments
- Apply Company_Handbook rules (professional tone)
- Flag connection requests from unknown contacts for approval
- Draft responses to messages using appropriate tone

## Usage Prompt
Invoke linkedin-watcher: Process new LinkedIn notifications

## Parameters
priority: medium
auto_accept: false (require approval for new connections)

## Approval Required
- New connection requests (unknown contacts)
- Direct message replies (per Company_Handbook.md)
- Comments on sensitive topics
