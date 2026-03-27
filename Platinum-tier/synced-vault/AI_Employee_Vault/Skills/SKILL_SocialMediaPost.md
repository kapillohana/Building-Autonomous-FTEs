---
name: social-media-post
description: Posts content to multiple social platforms
when_to_use: When approved social media content is ready
---

# SKILL: Social Media Post

## Description
Posts content to multiple social platforms.

## Instructions
- Read approved post from /Approved/Social_Post.md
- Check target platforms (LinkedIn, Twitter, Facebook)
- Format content per platform requirements
- Post via MCP or API
- Log post URL and engagement metrics

## Usage Prompt
Invoke social-media-post: Publish the approved content to specified platforms

## Parameters
platforms: [linkedin, twitter, facebook]
schedule: immediate (or specific datetime)

## Platform Formats
- **LinkedIn**: Professional, 3000 char max, hashtags
- **Twitter**: Concise, 280 char, threads for longer
- **Facebook**: Casual, links encouraged

## Approval Required
- All posts require /Approved/ status
- Controversial topics flagged for human review
- Scheduled posts auto-approved if within business hours (9 AM - 6 PM)
