---
name: whatsapp-watcher
description: Processes new WhatsApp messages from /Needs_Action
when_to_use: When a new WHATSAPP_*.md file appears in Needs_Action
---

## Description
Handles WhatsApp messages (urgent, invoice, payment, help).

## Instructions
- Read the WhatsApp file
- Apply Company_Handbook rules (polite communication, flag payments >$500, prioritize urgent)
- Create reply plan or move to Done
- Use Ralph Wiggum loop if task is not complete

## Usage Prompt
Invoke whatsapp-watcher: Process all new WHATSAPP files in Needs_Action

## Parameters
priority: high
