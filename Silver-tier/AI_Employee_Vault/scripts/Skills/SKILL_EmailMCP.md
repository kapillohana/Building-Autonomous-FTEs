---
name: email-mcp
description: Sends email via MCP server
when_to_use: When draft is approved in /Approved/
---

## Description
Sends approved email drafts through the Email MCP server.

## Instructions
- Check /Approved/ folder for EMAIL_*.md files with status: approved
- Call POST /send_email endpoint with to, subject, body
- Verify email sent successfully
- Move sent email to /Done/ folder
- Log action with timestamp

## Usage Prompt
Invoke email-mcp: Send the approved email draft

## Parameters
to: recipient email address
subject: email subject
body: email content
