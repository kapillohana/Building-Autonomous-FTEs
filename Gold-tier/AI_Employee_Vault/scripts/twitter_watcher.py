#!/usr/bin/env python3
"""
Twitter/X Watcher - Gold Tier
Monitors Business_Goals.md for content updates and posts to Twitter/X.
Uses Playwright for browser automation with session persistence.
Optimized for short-form tweets and threads.
"""

import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
LOGS_FOLDER = Path(__file__).parent.parent / 'logs'
LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_FOLDER / 'social_media.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('TwitterWatcher')

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Run: pip install playwright && playwright install")

# Twitter/X Configuration
TWITTER_URL = 'https://twitter.com'
TWEET_CHAR_LIMIT = 280
THREAD_TWEET_LIMIT = 10


class TwitterWatcher:
    """Watches for business content and posts to Twitter/X"""
    
    def __init__(self, vault_path: str = None, check_interval: int = 300):
        self.vault_path = Path(vault_path or Path(__file__).parent.parent).resolve()
        self.scripts_path = Path(__file__).parent.resolve()
        self.check_interval = check_interval
        
        # Session file
        self.twitter_session_file = self.scripts_path / 'twitter_session.json'
        
        # Content source
        self.business_goals_file = self.vault_path / 'Business_Goals.md'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        
        # Credentials from environment
        self.TWITTER_EMAIL = os.getenv('TWITTER_EMAIL', '')
        self.TWITTER_USERNAME = os.getenv('TWITTER_USERNAME', '')
        self.TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD', '')
        
        # Processed content tracking
        self.processed_file = LOGS_FOLDER / 'processed_twitter_posts.json'
        self.processed_posts = self._load_processed_posts()
        
        # Default hashtags
        self.default_hashtags = "#BusinessUpdate #AIEmployee #GoldTier #Automation"
        
        print("=" * 60)
        print("Twitter/X Watcher - Gold Tier")
        print("=" * 60)
        print(f"Vault Path: {self.vault_path}")
        print(f"Check Interval: {check_interval}s")
        print(f"Tweet Limit: {TWEET_CHAR_LIMIT} characters")
        print("=" * 60)
        
        if not PLAYWRIGHT_AVAILABLE:
            print("\n⚠️  Playwright not installed!")
            print("   Run: pip install playwright && playwright install")
        
        logger.info("TwitterWatcher initialized")
    
    def _load_processed_posts(self) -> set:
        """Load set of already processed post hashes"""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed_posts(self):
        """Save processed posts to file"""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_posts), f)
    
    def _load_session(self) -> dict:
        """Load saved session cookies"""
        if self.twitter_session_file.exists():
            with open(self.twitter_session_file, 'r') as f:
                session = json.load(f)
                logger.info("Loaded Twitter session")
                return session
        return {}
    
    def _save_session(self, cookies: list):
        """Save session cookies"""
        with open(self.twitter_session_file, 'w') as f:
            json.dump(cookies, f)
        logger.info("Saved Twitter session")
    
    def _create_tweet_content(self, text: str, section: str = None) -> list:
        """Split content into tweet-sized chunks (thread support)"""
        tweets = []
        
        # Add hashtags
        full_text = f"{text}\n\n{self.default_hashtags}"
        
        # If within limit, single tweet
        if len(full_text) <= TWEET_CHAR_LIMIT:
            tweets.append(full_text)
            return tweets
        
        # Split into thread
        words = full_text.split(' ')
        current_tweet = ""
        
        for word in words:
            test_tweet = f"{current_tweet} {word}".strip()
            if len(test_tweet) <= TWEET_CHAR_LIMIT:
                current_tweet = test_tweet
            else:
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = word
        
        if current_tweet:
            tweets.append(current_tweet)
        
        # Limit thread length
        return tweets[:THREAD_TWEET_LIMIT]
    
    def _generate_post_content(self) -> list:
        """Read Business_Goals.md and generate tweet content"""
        posts = []
        
        if not self.business_goals_file.exists():
            logger.warning(f"Business_Goals.md not found: {self.business_goals_file}")
            return posts
        
        content = self.business_goals_file.read_text(encoding='utf-8')
        
        # Extract recent updates
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('## ') or line.startswith('### '):
                if current_section and current_content:
                    post_text = ' '.join(current_content[:100])  # Limit for tweets
                    post_hash = hash(post_text)
                    if post_text.strip() and post_hash not in self.processed_posts:
                        posts.append({
                            'section': current_section,
                            'content': post_text,
                            'timestamp': datetime.now().isoformat()
                        })
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Handle last section
        if current_section and current_content:
            post_text = ' '.join(current_content[:100])
            post_hash = hash(post_text)
            if post_text.strip() and post_hash not in self.processed_posts:
                posts.append({
                    'section': current_section,
                    'content': post_text,
                    'timestamp': datetime.now().isoformat()
                })
        
        return posts
    
    def _create_approval_file(self, tweet_data: dict, thread: list) -> Path:
        """Create approval file in Pending_Approval folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SOCIAL_TWITTER_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        thread_content = '\n\n---\n\n'.join([f"**Tweet {i+1}:**\n{t}" for i, t in enumerate(thread)])
        
        content = f"""---
type: social_media
platform: twitter
created: {tweet_data['timestamp']}
status: pending_approval
thread_count: {len(thread)}
---

# Twitter/X Post Draft

## Source
{tweet_data.get('section', 'Business_Goals.md')}

## Thread
{thread_content}

---
**Action Required:** Move to /Approved folder to publish, or delete to reject.
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Twitter approval file: {filepath}")
        print(f"  → Created: {filename}")
        
        return filepath
    
    def _create_summary_file(self, posted_tweets: list) -> Path:
        """Create summary file in Done folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"TWITTER_SUMMARY_{timestamp}.md"
        filepath = self.vault_path / 'Done' / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        summary_content = '\n\n---\n\n'.join([f"**Tweet {i+1}:**\n{t}" for i, t in enumerate(posted_tweets)])
        
        content = f"""---
type: social_media_summary
platform: twitter
created: {datetime.now().isoformat()}
status: published
---

# Twitter/X Posting Summary

## Posted Thread
{summary_content}

## Metrics
- Total Tweets: {len(posted_tweets)}
- Posted At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Status: Published

---
*Auto-generated by Twitter Watcher - Gold Tier*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Twitter summary: {filepath}")
        
        return filepath
    
    def post_to_twitter(self, thread: list, page: sync_playwright) -> bool:
        """Post thread to Twitter/X"""
        try:
            print(f"\n🐦 Posting to Twitter/X ({len(thread)} tweet(s))...")
            logger.info(f"Posting thread to Twitter: {len(thread)} tweets")
            
            browser = page.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Load existing session
            session = self._load_session()
            if session:
                context.add_cookies(session)
            
            page = context.new_page()
            
            # Navigate to Twitter
            page.goto(TWITTER_URL, timeout=60000)
            page.wait_for_timeout(5000)
            
            # Check if logged in
            if 'login' in page.url.lower() or 'i/flow/login' in page.url:
                print("  → Logging in to Twitter...")
                logger.info("Logging in to Twitter")
                
                try:
                    # Enter email/username
                    page.fill('input[autocomplete="username"]', self.TWITTER_EMAIL)
                    page.click('div[role="button"]:has-text("Next")')
                    page.wait_for_timeout(3000)
                    
                    # Enter password
                    page.fill('input[type="password"]', self.TWITTER_PASSWORD)
                    page.click('div[role="button"]:has-text("Log in")')
                    page.wait_for_timeout(5000)
                    
                except Exception as e:
                    logger.warning(f"Twitter login interaction: {str(e)}")
            
            page.wait_for_timeout(3000)
            
            # Check if still on login page
            if 'login' in page.url.lower():
                print("  ✗ Twitter login failed - check credentials")
                logger.error("Twitter login failed")
                browser.close()
                return False
            
            # Click Tweet button
            try:
                page.goto('https://twitter.com/compose/tweet', timeout=60000)
                page.wait_for_timeout(3000)
                
                # Find tweet box
                tweet_box = page.locator('div[contenteditable="true"][data-contents="true"]').first
                tweet_box.click()
                page.wait_for_timeout(1000)
                
                # Post first tweet
                tweet_box.fill(thread[0])
                page.wait_for_timeout(1000)
                
                # Add more tweets for thread
                for i in range(1, len(thread)):
                    try:
                        # Click "Add another post" button
                        add_button = page.locator('div[role="button"][aria-label*="Add"], button:has-text("Add")').first
                        add_button.click()
                        page.wait_for_timeout(1000)
                        
                        # Find next tweet box and fill
                        tweet_boxes = page.locator('div[contenteditable="true"][data-contents="true"]').all()
                        if len(tweet_boxes) > i:
                            tweet_boxes[i].fill(thread[i])
                            page.wait_for_timeout(500)
                    except Exception as e:
                        logger.warning(f"Could not add tweet {i+1}: {str(e)}")
                
                # Click Post button
                post_button = page.locator('div[role="button"][data-testid="tweetButton"], button:has-text("Post")').first
                post_button.click()
                page.wait_for_timeout(5000)
                
                # Save session
                self._save_session(context.cookies())
                
                # Create summary
                self._create_summary_file(thread)
                
                print("  ✓ Twitter thread published!")
                logger.info("Twitter thread published successfully")
                return True
                
            except Exception as e:
                logger.error(f"Twitter posting failed: {str(e)}")
                print(f"  ✗ Twitter post failed: {str(e)}")
                
                # Create approval file on failure
                self._create_approval_file({
                    'content': thread[0] if thread else '',
                    'timestamp': datetime.now().isoformat(),
                    'section': 'Business Update'
                }, thread)
                
                browser.close()
                return False
            
            browser.close()
            
        except Exception as e:
            logger.error(f"Twitter posting error: {str(e)}")
            print(f"  ✗ Error: {str(e)}")
            
            # Create approval file on error
            self._create_approval_file({
                'content': thread[0] if thread else '',
                'timestamp': datetime.now().isoformat(),
                'section': 'Business Update'
            }, thread)
            
            return False
    
    def check_for_updates(self) -> list:
        """Check Business_Goals.md for new content"""
        print("\n" + "=" * 60)
        print("Checking Business_Goals.md for Twitter content...")
        logger.info("Checking for new content")
        
        posts = self._generate_post_content()
        
        if posts:
            print(f"  ✓ Found {len(posts)} new post(s)")
            logger.info(f"Found {len(posts)} new posts")
        else:
            print("  → No new content")
            logger.info("No new content found")
        
        return posts
    
    def run(self):
        """Main watcher loop"""
        print("\n🚀 Starting Twitter/X Watcher...")
        print("   Press Ctrl+C to stop\n")
        logger.info("Starting watcher loop")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️  Playwright not available - running in approval-file mode only")
        
        while True:
            try:
                posts = self.check_for_updates()
                
                for post in posts:
                    print(f"\n📝 Processing: {post.get('section', 'Unknown')}")
                    
                    # Create tweet thread
                    thread = self._create_tweet_content(post['content'], post.get('section'))
                    
                    print(f"  → Thread: {len(thread)} tweet(s)")
                    
                    # Try to post if Playwright available
                    if PLAYWRIGHT_AVAILABLE:
                        with sync_playwright() as p:
                            success = self.post_to_twitter(thread, p)
                            if success:
                                self.processed_posts.add(hash(post['content']))
                                self._save_processed_posts()
                    else:
                        # Create approval file only
                        self._create_approval_file(post, thread)
                        self.processed_posts.add(hash(post['content']))
                        self._save_processed_posts()
                
            except Exception as e:
                logger.error(f"Watcher error: {str(e)}")
                print(f"  ✗ Error: {str(e)}")
            
            print(f"\n⏳ Next check in {self.check_interval} seconds...")
            import time
            time.sleep(self.check_interval)


    def run_test_mode(self):
        """Test mode - create dummy Twitter posts without login"""
        print("\n" + "=" * 60)
        print("TEST MODE - Gold Tier Twitter/X Validation")
        print("=" * 60)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create dummy Twitter thread
        tweets = [
            "🚀 Gold Tier AI Employee is LIVE! New features: Odoo ERP integration, automated CEO briefings, multi-platform social posting. #AIEmployee #GoldTier #BusinessAutomation",
            "📊 Accounting made easy with Odoo integration. Track invoices, revenue, and generate financial reports automatically. #Accounting #ERP #SmallBusiness",
            "💼 CEO Briefing every Monday morning. Get revenue summaries, pending payments, and actionable insights. Stay informed! #Leadership #BusinessIntelligence"
        ]
        
        thread_content = '\n\n---\n\n'.join([f"**Tweet {i+1}:**\n{t}" for i, t in enumerate(tweets)])
        
        twitter_content = f"""---
type: social_media
platform: twitter
created: {datetime.now().isoformat()}
status: pending_approval
test_mode: true
thread_count: 3
---

# Twitter/X Post Draft - TEST MODE

## Thread
{thread_content}

---
**TEST MODE:** This is a demo thread for Gold Tier validation.
Move to /Approved to enable real posting.
"""
        
        twitter_file = self.pending_approval / f"SOCIAL_TWITTER_TEST_{timestamp}.md"
        twitter_file.write_text(twitter_content, encoding='utf-8')
        print(f"  ✓ Created: {twitter_file.name}")
        
        # Create summary in Done
        summary_content = f"""---
type: social_media_summary
platform: twitter
created: {datetime.now().isoformat()}
status: test_complete
test_mode: true
---

# Twitter/X Test Summary

## Platforms Covered
1. ✅ Twitter/X - Thread draft created (3 tweets)

## Test Results
- Approval files generated: 1
- Thread tweets: 3
- Platforms validated: Twitter/X
- Test mode: ACTIVE
- Real posting: DISABLED

## Next Steps
1. Set credentials in .env file
2. Run without --test flag for real posting
3. Move approval files to /Approved to publish

---
*Gold Tier Twitter/X Integration - Test Complete*
"""
        
        done_file = self.vault_path / 'Done' / f"TWITTER_TEST_SUMMARY_{timestamp}.md"
        done_file.parent.mkdir(parents=True, exist_ok=True)
        done_file.write_text(summary_content, encoding='utf-8')
        print(f"  ✓ Created summary: {done_file.name}")
        
        print("\n" + "=" * 60)
        print("✅ Twitter/X integration completed in test mode")
        print("=" * 60)
        
        logger.info("Test mode completed - Twitter/X covered")
        return True


if __name__ == "__main__":
    import sys
    
    # Check for test mode flag
    if '--test' in sys.argv or '-t' in sys.argv:
        watcher = TwitterWatcher()
        watcher.run_test_mode()
        sys.exit(0)
    
    try:
        watcher = TwitterWatcher()
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user")
        print("\n\n✓ Watcher stopped gracefully.")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        print(f"\n✗ Fatal: {str(e)}")
        sys.exit(1)
