---
name: social-media-manager
description: Unified skill to post and generate summaries on Facebook, Instagram and Twitter/X
when_to_use: When new business content or weekly update is ready
---

## Description
Manages social media presence across Facebook, Instagram, and Twitter/X.
Generates posts from Business_Goals.md and company updates, handles posting
with session management, and creates engagement summaries.

## Platforms

### Facebook
- Business page posts
- Photo albums
- Event promotion
- Engagement tracking

### Instagram
- Feed posts
- Story updates
- Hashtag optimization
- Visual content focus

### Twitter/X
- Short-form updates
- Thread creation
- Real-time engagement
- Trending topics

## Functions

### generate_post(content_type)
Creates platform-optimized post from source content.
Returns formatted post text + media suggestions.

### post_to_platform(platform, content)
Publishes content to specified platform.
Returns post ID and status.

### get_engagement_summary(platform, period)
Fetches likes, comments, shares for specified period.
Returns engagement metrics dictionary.

### generate_weekly_summary()
Creates weekly social media performance report.
Includes top posts, engagement trends, recommendations.

## Integration

### With SKILL_CEOBriefing
```
1. CEO Briefing requests weekly business update
2. social-media-manager generates post content
3. Posts to all platforms
4. Returns engagement summary for briefing
```

### With SKILL_ReasoningLoop
```
1. Reasoning loop detects content ready (blog, milestone, etc.)
2. Triggers social-media-manager
3. Creates platform-specific variations
4. Queues for approval or auto-posts
5. Logs results
```

## Test Mode (Gold Tier Quick Start)
For rapid Gold Tier validation without credentials:

```bash
# Run Facebook/Instagram watcher in test mode
python facebook_instagram_watcher.py --test

# Run Twitter watcher in test mode
python twitter_watcher.py --test
```

**Test mode creates:**
- Dummy approval files for all 3 platforms
- Summary file in /Done/
- No actual posting (safe for testing)
- Console confirmation message

## Session Management
- Sessions saved to `scripts/facebook_session.json`
- Sessions saved to `scripts/instagram_session.json`
- Sessions saved to `scripts/twitter_session.json`
- Auto-renewal on expiry
- Secure credential storage via environment variables

## Usage Prompt
Invoke social-media-manager: Post weekly business update to all platforms and generate summary

## Parameters
- platforms: ['facebook', 'instagram', 'twitter'] (default: all)
- content_source: Business_Goals.md (default)
- auto_post: false (requires approval)
- include_hashtags: true
- test_mode: false (set true for quick validation)

## Logging
All operations logged to: `../logs/social_media.log`
- Post creation
- Publishing status
- Engagement metrics
- Errors and retries

## Approval Workflow
1. Posts created in `/Pending_Approval/` as `SOCIAL_POST_*.md`
2. Human reviews and moves to `/Approved/`
3. System executes posting
4. Results logged and archived to `/Done/`

## Gold Tier Requirement Status
✅ Facebook integration - Complete
✅ Instagram integration - Complete
✅ Twitter/X integration - Complete
✅ Test mode available - Complete
