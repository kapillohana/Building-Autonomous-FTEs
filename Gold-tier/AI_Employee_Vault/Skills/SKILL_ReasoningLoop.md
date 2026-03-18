---
name: reasoning-loop
description: Creates Plan.md and keeps looping until done
when_to_use: After any Watcher creates action files
---

# SKILL: Reasoning Loop

## Description
Multi-step reasoning with Ralph Wiggum persistence.

## Instructions
- Scan /Needs_Action
- Create /Plans/Plan_{id}.md with checkboxes
- Use Ralph Wiggum loop: continue until all checkboxes checked

## Usage Prompt
Invoke reasoning-loop: Process all files in Needs_Action and create Plan.md
