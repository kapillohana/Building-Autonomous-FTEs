---
name: browser-mcp
description: Automates browser actions via MCP server
when_to_use: When web interaction is needed (forms, scraping, posting)
---

# SKILL: Browser MCP

## Description
Automates browser actions via MCP server.

## Instructions
- Read action request from /Approved/
- Launch browser via MCP (Playwright/Puppeteer)
- Execute actions (navigate, fill forms, click, screenshot)
- Capture result and save to vault
- Log all actions for audit trail

## Usage Prompt
Invoke browser-mcp: Execute the approved browser automation task

## Parameters
headless: true
timeout: 30000ms

## Supported Actions
- Navigate to URL
- Fill form fields
- Click buttons/links
- Take screenshots
- Extract page content
- Download files

## Security Notes
- All browser actions require /Approved/ file
- Credentials loaded from environment variables only
- Session cookies cleared after execution
