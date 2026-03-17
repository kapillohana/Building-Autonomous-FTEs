#!/usr/bin/env python3
"""
LinkedIn Watcher - Silver Tier
Monitors LinkedIn Web for new messages, mentions, and notifications.
Uses Playwright for browser automation with session persistence.
Includes auto-sales post generation using SKILL_LinkedInSales.

TEST MODE: Creates files for ANY conversations found (not just unread).
"""

import time
import json
import logging
import sys
import signal
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from base_watcher import BaseWatcher

# ────────────────────────────────────────────────────────────────
# Graceful Shutdown Handler
# ────────────────────────────────────────────────────────────────
shutdown_requested = False
browser_instance = None

def signal_handler(sig, frame):
    global shutdown_requested
    shutdown_requested = True
    logger.info("Shutdown signal received (Ctrl+C)")
    print("\n⚠ Shutdown requested, cleaning up...")
    
    try:
        import psutil
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except:
                pass
    except:
        pass
    
    print("✓ Stopped.")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ────────────────────────────────────────────────────────────────
# Logging Setup
# ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/watcher.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('LinkedInWatcher')

# ────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────
SESSION_FILE = Path('../scripts/linkedin_session.json').resolve()
SCREENSHOT_DIR = Path('../logs/screenshots').resolve()
MAX_RETRIES = 3
CHECK_INTERVAL = 180  # 3 minutes for LinkedIn
LINKEDIN_URL = 'https://www.linkedin.com'
LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/login'

# Keywords that indicate business/sales opportunities
BUSINESS_KEYWORDS = [
    'hiring', 'job', 'opportunity', 'partnership', 'collaboration',
    'investment', 'funding', 'client', 'customer', 'lead', 'prospect',
    'service', 'product', 'solution', 'enterprise', 'b2b', 'saas',
    'interested', 'buy', 'purchase', 'contract', 'deal', 'proposal'
]


class LinkedInWatcher(BaseWatcher):
    """
    LinkedIn Web watcher using Playwright.
    TEST MODE: Creates files for ANY conversations found.
    """

    def __init__(self, vault_path: str, check_interval: int = CHECK_INTERVAL):
        super().__init__(vault_path, check_interval)

        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        self.session_file = SESSION_FILE
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.processed_items = set()
        self._load_processed_items()

        # Create required directories
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        logs_dir = Path('../logs').resolve()
        logs_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Session file: {self.session_file}")
        logger.info(f"Screenshot dir: {SCREENSHOT_DIR}")
        
        if self.session_file.exists():
            print(f"✓ Session file found: {self.session_file}")
        else:
            print(f"ℹ No session file yet (will create after login)")

    def _load_processed_items(self):
        """Load previously processed item IDs."""
        processed_file = Path('../logs/processed_linkedin_ids.json').resolve()
        if processed_file.exists():
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    self.processed_items = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_items)} processed IDs")
            except:
                self.processed_items = set()
        else:
            self.processed_items = set()

    def _save_processed_items(self):
        """Save processed item IDs to file."""
        processed_file = Path('../logs/processed_linkedin_ids.json').resolve()
        try:
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_items), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save processed items: {e}")

    def _init_browser(self) -> bool:
        """Initialize Playwright browser with stealth options."""
        for attempt in range(MAX_RETRIES):
            try:
                print(f"\n[Attempt {attempt+1}/{MAX_RETRIES}] Initializing browser...")
                
                self.playwright = sync_playwright().start()

                print("")
                print("=" * 60)
                print("=== OPENING LINKEDIN WEB ===")
                print("=" * 60)

                print("Launching Chromium with stealth options...")
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    slow_mo=100,
                    ignore_default_args=['--enable-automation'],
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-infobars',
                        '--disable-dev-shm-usage',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--window-size=1280,720'
                    ]
                )
                
                global browser_instance
                browser_instance = self.browser

                print("Creating browser context...")
                self.context = self.browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720},
                    ignore_https_errors=True
                )

                print("Creating new page...")
                self.page = self.context.new_page()
                self.page.set_default_timeout(90000)

                print("Injecting stealth scripts...")
                self.page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """)

                print("Navigating to LinkedIn...")
                self.page.goto(LINKEDIN_URL, wait_until='domcontentloaded', timeout=60000)
                self.page.wait_for_timeout(5000)

                logger.info("Browser initialized with stealth mode")
                print("✓ Browser initialized successfully!")
                return True

            except Exception as e:
                logger.error(f"Init attempt {attempt+1} failed: {e}")
                print(f"✗ Error: {e}")
                print(f"   Error type: {type(e).__name__}")
                
                if attempt < MAX_RETRIES - 1:
                    print(f"   Retrying in 2 seconds...\n")
                    time.sleep(2)
                else:
                    logger.error(f"All browser init attempts failed")
                    print(f"\n✗ All {MAX_RETRIES} attempts failed")
                    print("\nTroubleshooting tips:")
                    print("  1. Make sure Playwright browsers are installed:")
                    print("     playwright install chromium")
                    print("  2. Check if another browser instance is running")
                    print("  3. Try closing any open Chrome/Chromium windows")
                    return False
        return False

    def _load_session(self) -> bool:
        """Load saved session with robust restoration."""
        if not self.session_file.exists():
            print("No session file found")
            return False

        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            version = session_data.get('version', 1)
            print(f"Session version: {version}")

            if 'timestamp' in session_data:
                session_time = datetime.fromisoformat(session_data['timestamp'])
                age_hours = (datetime.now() - session_time).total_seconds() / 3600
                age_days = age_hours / 24
                print(f"Session age: {age_days:.2f} days ({age_hours:.1f} hours)")
                if age_hours > 336:  # 14 days
                    print(f"Session expired ({age_days:.1f} days old)")
                    return False

            if 'cookies' in session_data and session_data['cookies']:
                self.context.add_cookies(session_data['cookies'])
                print(f"✓ Loaded {len(session_data['cookies'])} cookies from session")
            else:
                print("⚠ No cookies in session file")

            print("Loading LinkedIn with saved session...")
            self.page.goto(LINKEDIN_URL, wait_until='domcontentloaded', timeout=60000)
            self.page.wait_for_timeout(15000)

            if 'localStorage' in session_data and session_data['localStorage']:
                try:
                    self.page.evaluate(f"""
                        try {{
                            var data = {session_data['localStorage']};
                            if (data && typeof data === 'object') {{
                                Object.keys(data).forEach(key => {{
                                    try {{
                                        localStorage.setItem(key, data[key]);
                                    }} catch (e) {{}}
                                }});
                            }}
                        }} catch (e) {{}}
                    """)
                    print("✓ Restored localStorage")
                except Exception as e:
                    logger.debug(f"Could not restore localStorage: {e}")

            debug_screenshot = SCREENSHOT_DIR / 'linkedin_session_check.png'
            try:
                self.page.screenshot(path=str(debug_screenshot))
                print(f"Debug screenshot saved: {debug_screenshot}")
            except:
                pass

            if self._is_logged_in():
                print("✓ Session loaded successfully - you're logged in!")
                return True
            else:
                print("⚠ Session found but not logged in (QR may be showing)")
                print(f"Current URL: {self.page.url}")
                return False

        except Exception as e:
            print(f"Error loading session: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_session(self):
        """Save current session with robust storage."""
        try:
            cookies = self.context.cookies()
            
            try:
                local_storage = self.page.evaluate('() => { return JSON.stringify(localStorage) }')
            except:
                local_storage = None
            
            try:
                session_storage = self.page.evaluate('() => { return JSON.stringify(sessionStorage) }')
            except:
                session_storage = None

            session_data = {
                'cookies': cookies,
                'localStorage': local_storage,
                'sessionStorage': session_storage,
                'timestamp': datetime.now().isoformat(),
                'url': self.page.url,
                'version': 2
            }
            
            temp_file = self.session_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            temp_file.replace(self.session_file)
            
            print(f"✓ Session saved to: {self.session_file}")
            print(f"  Cookies: {len(cookies)}")
            logger.info(f"Session saved successfully: {len(cookies)} cookies")
        except Exception as e:
            logger.error(f"Save session failed: {e}")
            print(f"Warning: Could not save session: {e}")

    def _is_logged_in(self) -> bool:
        """Check if LinkedIn is logged in."""
        try:
            self.page.wait_for_timeout(2000)
            
            indicators = [
                '[data-control-name="nav_digitbar"]',
                '.mn-header__nav',
                '#mynetwork-tab-icon',
                '[aria-label="Messaging"]',
                'a[href*="/messaging/"]'
            ]
            
            for sel in indicators:
                try:
                    if self.page.query_selector(sel):
                        return True
                except:
                    pass
            
            current_url = self.page.url
            if 'linkedin.com/feed' in current_url or 'linkedin.com/mynetwork' in current_url:
                return True
            
            if 'linkedin.com/login' in current_url:
                return False
                
        except Exception as e:
            logger.debug(f"Login check error: {e}")
        
        return False

    def _wait_for_login(self) -> bool:
        """Wait for user to manually log in."""
        print("")
        print("=== LOGIN TO LINKEDIN ===")
        print("1. Enter your email and password")
        print("2. Complete any verification steps")
        print("3. Wait for your feed to load")
        print("")

        max_wait = 180
        elapsed = 0

        while elapsed < max_wait:
            if shutdown_requested:
                return False

            if self._is_logged_in():
                print("✓ Login successful!")
                self._save_session()
                return True

            time.sleep(3)
            elapsed += 3
            if elapsed % 30 == 0:
                print(f"Waiting for login... {elapsed}s")

        print("Login timeout")
        return False

    def _get_notifications(self) -> List[Dict[str, Any]]:
        """
        TEST MODE: Get ALL conversations and create files for testing.
        Even if not unread, creates files from most recent chats.
        """
        items = []

        try:
            print("Refreshing LinkedIn page...")
            self.page.reload(wait_until='domcontentloaded')
            self.page.wait_for_timeout(8000)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = SCREENSHOT_DIR / f'linkedin_{timestamp}.png'
            self.page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved: {screenshot_path}")

            # =========================================================
            # STEP 1: Check Messaging - TEST MODE (get ALL conversations)
            # =========================================================
            print("\n--- Checking Messages (TEST MODE) ---")
            
            try:
                messaging_link = self.page.query_selector('a[href*="/messaging/"], [aria-label="Messaging"]')
                if messaging_link:
                    print("Opening messaging...")
                    messaging_link.click()
                    self.page.wait_for_timeout(5000)

                    # Get ALL conversation cards (not just unread)
                    message_cards = self.page.query_selector_all('.msg-conversation-card, [class*="conversation-card"]')
                    total_conversations = len(message_cards)
                    print(f"Found {total_conversations} conversations")

                    if total_conversations > 0:
                        # TEST MODE: Always create file for first chat
                        print(f"Found {total_conversations} conversations - creating test file for first chat")
                        
                        first_card = message_cards[0]
                        
                        # Get sender name
                        sender = "Unknown"
                        sender_elem = first_card.query_selector('.msg-conversation-card__name, [class*="sender-name"]')
                        if sender_elem:
                            sender = sender_elem.inner_text().strip()

                        # Get message preview
                        preview = ""
                        preview_elem = first_card.query_selector('.msg-conversation-card__text-preview, [class*="preview"]')
                        if preview_elem:
                            preview = preview_elem.inner_text().strip()[:300]

                        # Click to read full conversation
                        try:
                            print(f"Opening conversation with: {sender}")
                            first_card.click()
                            self.page.wait_for_timeout(4000)

                            # Get full message content
                            msg_bubbles = self.page.query_selector_all('.msg-s-message-bubble, [class*="message-bubble"]')
                            if msg_bubbles:
                                last_msg = msg_bubbles[-1].query_selector('span')
                                if last_msg:
                                    full_content = last_msg.inner_text().strip()[:1000]
                                    if full_content:
                                        preview = full_content
                                        print(f"Full message content: [{full_content[:100]}...]")
                        except Exception as e:
                            logger.debug(f"Could not click message: {e}")

                        # Check for business keywords
                        is_business = any(kw in preview.lower() for kw in BUSINESS_KEYWORDS)
                        
                        # TEST MODE: Force business flag for testing sales post
                        force_business = True  # Always trigger sales post for testing
                        
                        print(f"Message from: {sender}")
                        print(f"Content: [{preview[:80]}...]")
                        print(f"Business keywords: {'Yes' if is_business else 'No'}")
                        print(f"Force business (test): {'Yes' if force_business else 'No'}")

                        # Create item for first conversation
                        msg_id = f"linkedin_test_{sender}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        
                        if msg_id not in self.processed_items:
                            items.append({
                                'id': msg_id,
                                'type': 'message',
                                'content': f"From: {sender}\n{preview}",
                                'is_business': is_business or force_business,
                                'timestamp': datetime.now().isoformat(),
                                'priority': 'high',
                                'source': 'test_mode',
                                'test_mode': True,
                                'total_conversations': total_conversations
                            })
                            print(f"✓ Created test item from first conversation")

                        # Go back to conversation list
                        try:
                            back = self.page.query_selector('[aria-label="Back"]')
                            if back:
                                back.click()
                                self.page.wait_for_timeout(2000)
                        except:
                            pass

                        # TEST MODE: Also create items for next 2 conversations if available
                        if total_conversations > 1:
                            print(f"\nProcessing additional conversations for testing...")
                            for idx, card in enumerate(message_cards[1:3], 1):
                                try:
                                    sender_elem = card.query_selector('.msg-conversation-card__name')
                                    preview_elem = card.query_selector('.msg-conversation-card__text-preview')
                                    
                                    if sender_elem and preview_elem:
                                        conv_sender = sender_elem.inner_text().strip()
                                        conv_preview = preview_elem.inner_text().strip()[:200]
                                        
                                        conv_id = f"linkedin_conv{idx}_{conv_sender}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                        
                                        if conv_id not in self.processed_items:
                                            items.append({
                                                'id': conv_id,
                                                'type': 'message',
                                                'content': f"From: {conv_sender}\n{conv_preview}",
                                                'is_business': any(kw in conv_preview.lower() for kw in BUSINESS_KEYWORDS),
                                                'timestamp': datetime.now().isoformat(),
                                                'priority': 'medium',
                                                'source': 'conversation',
                                                'test_mode': True
                                            })
                                            print(f"✓ Created item for conversation {idx}: {conv_sender}")
                                except Exception as e:
                                    logger.debug(f"Error processing conversation {idx}: {e}")

                    else:
                        print("No conversations found")

                    # Go back to main page
                    try:
                        back = self.page.query_selector('[aria-label="Back"]')
                        if back:
                            back.click()
                            self.page.wait_for_timeout(2000)
                    except:
                        pass

            except Exception as e:
                logger.debug(f"Error checking messages: {e}")
                print(f"Error: {e}")

            # =========================================================
            # STEP 2: Check Notifications (standard detection)
            # =========================================================
            print("\n--- Checking Notifications ---")
            
            try:
                notification_indicator = self.page.query_selector('[aria-label="Notifications"]')
                if notification_indicator:
                    # Check for unread badge
                    badge = notification_indicator.query_selector('span[aria-label], em, .notification-badge')
                    unread_count = 0
                    if badge:
                        badge_text = badge.inner_text().strip()
                        if badge_text.isdigit():
                            unread_count = int(badge_text)
                            print(f"Unread notifications: {unread_count}")

                    # Click and read notifications
                    notification_indicator.click()
                    self.page.wait_for_timeout(3000)

                    notification_items = self.page.query_selector_all('ul.mn-notification-feed > li, .mn-notification')
                    print(f"Found {len(notification_items)} notifications in panel")

                    for idx, notif in enumerate(notification_items[:5]):
                        try:
                            text_elem = notif.query_selector('span, div')
                            notif_text = ""
                            if text_elem:
                                notif_text = text_elem.inner_text().strip()[:500]
                            
                            if notif_text:
                                notif_type = 'notification'
                                if 'message' in notif_text.lower():
                                    notif_type = 'message'
                                elif 'mention' in notif_text.lower() or 'tagged' in notif_text.lower():
                                    notif_type = 'mention'
                                elif 'connection' in notif_text.lower():
                                    notif_type = 'connection'

                                is_business = any(kw in notif_text.lower() for kw in BUSINESS_KEYWORDS)

                                item_id = f"linkedin_{notif_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx}"

                                if item_id not in self.processed_items:
                                    items.append({
                                        'id': item_id,
                                        'type': notif_type,
                                        'content': notif_text,
                                        'is_business': is_business,
                                        'timestamp': datetime.now().isoformat(),
                                        'priority': 'medium' if not is_business else 'high',
                                        'source': 'notification'
                                    })
                                    print(f"✓ Added notification: {notif_type}")
                        except Exception as e:
                            logger.debug(f"Error processing notification {idx}: {e}")

            except Exception as e:
                logger.debug(f"Error checking notifications: {e}")

            # =========================================================
            # Summary
            # =========================================================
            print(f"\n=== DETECTION SUMMARY ===")
            print(f"Total items to process: {len(items)}")
            business_items = sum(1 for i in items if i.get('is_business', False))
            test_items = sum(1 for i in items if i.get('test_mode', False))
            print(f"Business-related: {business_items}")
            print(f"Test mode items: {test_items}")
            print(f"=========================\n")

        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            print(f"Error: {e}")

        return items

    def check_for_updates(self) -> list:
        """Check for new LinkedIn activity."""
        for attempt in range(MAX_RETRIES):
            try:
                print("\n" + "=" * 50)
                print("POLLING LINKEDIN...")
                print("=" * 50)

                if not self.page:
                    if not self._init_browser():
                        continue
                    if not self._load_session():
                        if not self._wait_for_login():
                            return []

                if not self._is_logged_in():
                    print("Not logged in, attempting login...")
                    if not self._load_session():
                        if not self._wait_for_login():
                            return []

                items = self._get_notifications()
                
                print("Saving session after successful poll...")
                self._save_session()
                
                return items

            except Exception as e:
                logger.error(f"Poll error {attempt+1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                else:
                    return []
        return []

    def _generate_sales_post(self, content: str) -> str:
        """Generate a sales post based on SKILL_LinkedInSales."""
        try:
            handbook_path = self.vault_path / 'Company_Handbook.md'
            if handbook_path.exists():
                handbook_content = handbook_path.read_text(encoding='utf-8')
                print("Read Company_Handbook.md")

            goals_path = self.vault_path / 'Business_Goals.md'
            if goals_path.exists():
                goals_content = goals_path.read_text(encoding='utf-8')
                print("Read Business_Goals.md")

            post = """## 🚀 Transform Your Business Operations with AI-Powered Efficiency

Are you tired of letting repetitive tasks slow down your team? In today's fast-paced business environment, staying competitive means working smarter, not harder.

At our company, we specialize in implementing intelligent automation solutions that:

✅ **Reduce response times** - Handle client inquiries within 24 hours, every time
✅ **Streamline financial workflows** - Process invoices and payments automatically
✅ **Eliminate missed deadlines** - Track critical tasks and never drop the ball
✅ **Free your team** - Focus on high-value work while AI handles the rest

💡 **Real Results:** Our AI Employee Vault system helps businesses maintain professional communication, automate financial tracking, and keep teams organized—all while maintaining human oversight where it matters most.

**Ready to explore how automation can transform your operations?**

📩 **Let's connect!** Send me a message or comment below to schedule a free consultation. No pressure—just a friendly conversation about your goals.

---
*Committed to responding to all inquiries within 24 hours.*

#BusinessAutomation #AI #Productivity #DigitalTransformation #Innovation #SmallBusiness #Entrepreneurship #TechSolutions
"""
            return post

        except Exception as e:
            logger.error(f"Error generating sales post: {e}")
            return ""

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file for LinkedIn item."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            item_type = item.get('type', 'unknown')
            filename = f"LINKEDIN_{item_type.upper()}_{timestamp}.md"
            filepath = self.needs_action / filename

            priority = item.get('priority', 'medium').upper()
            content = item.get('content', 'No content')
            source = item.get('source', 'unknown')
            test_mode = item.get('test_mode', False)

            markdown_content = f"""---
type: linkedin
item_type: {item_type}
received: {item['timestamp']}
priority: {priority}
status: pending
is_business: {item.get('is_business', False)}
source: {source}
test_mode: {test_mode}
---

## LinkedIn {item_type.title()} {'(TEST MODE)' if test_mode else ''}

**Type:** {item_type}
**Received:** {item['timestamp']}
**Priority:** {priority}
**Business Related:** {'Yes' if item.get('is_business', False) else 'No'}
**Source:** {source}
**Test Mode:** {'Yes' if test_mode else 'No'}

## Content

{content}

## Suggested Actions

- [ ] Review {item_type} content
- [ ] Respond if action required
- [ ] Flag for approval if needed
- [ ] Archive after processing

## Processing Notes

_Add notes about processing here_
"""

            filepath.write_text(markdown_content, encoding='utf-8')
            self.processed_items.add(item['id'])
            self._save_processed_items()

            test_flag = " (TEST)" if test_mode else ""
            print(f"✓ Created action file: {filename}{test_flag}")
            logger.info(f"Created: {filepath}")

            # Auto-generate sales post if business-related or test mode
            if item.get('is_business', False) or test_mode:
                print("Business/test item detected, triggering sales post generation...")
                self._create_sales_post_draft()

            return filepath

        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            raise

    def _create_sales_post_draft(self):
        """Create a sales post draft in Pending_Approval using SKILL_LinkedInSales."""
        try:
            pending_dir = self.vault_path / 'Pending_Approval'
            pending_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            draft_path = pending_dir / f'LinkedIn_Post_{timestamp}.md'

            post_content = self._generate_sales_post("")

            draft_markdown = f"""---
type: linkedin_post
status: pending_approval
created: {datetime.now().isoformat()}
tone: professional
length: medium
skill: SKILL_LinkedInSales
---

# LinkedIn Sales Post Draft

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Pending Approval
**Source:** Auto-generated from LinkedIn activity (SKILL_LinkedInSales)

---

{post_content}

---

## Approval Checklist

- [ ] Review content for accuracy
- [ ] Verify alignment with brand voice
- [ ] Check for scheduling (business hours 9 AM - 6 PM)
- [ ] Approve for posting
"""

            draft_path.write_text(draft_markdown, encoding='utf-8')
            print(f"✓ Generated sales post draft: {draft_path.name}")
            print(f"  → Saved to: {draft_path}")
            logger.info(f"Sales post draft created: {draft_path}")

        except Exception as e:
            logger.error(f"Error creating sales post draft: {e}")
            print(f"Warning: Could not create sales post draft: {e}")

    def cleanup(self):
        """Clean up browser and playwright resources with guaranteed session save."""
        print("\nCleaning up resources...")
        
        # ALWAYS save session before closing
        if self.page and self.context:
            try:
                print("⚠ Saving session before exit (critical)...")
                cookies = self.context.cookies()
                
                try:
                    local_storage = self.page.evaluate('() => { return JSON.stringify(localStorage) }')
                except:
                    local_storage = None
                
                try:
                    session_storage = self.page.evaluate('() => { return JSON.stringify(sessionStorage) }')
                except:
                    session_storage = None

                session_data = {
                    'cookies': cookies,
                    'localStorage': local_storage,
                    'sessionStorage': session_storage,
                    'timestamp': datetime.now().isoformat(),
                    'url': self.page.url,
                    'version': 2
                }
                
                temp_file = self.session_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
                temp_file.replace(self.session_file)
                
                print(f"✓ Session SAVED successfully ({len(cookies)} cookies)")
            except Exception as e:
                print(f"✗ Failed to save session: {e}")
        
        if self.browser:
            print("Closing browser...")
            try:
                self.browser.close()
            except:
                pass
            self.browser = None
            
        if self.playwright:
            print("Stopping Playwright...")
            try:
                self.playwright.stop()
            except:
                pass
            self.playwright = None
            
        print("✓ Cleanup complete.")
        
        global browser_instance
        browser_instance = None

    def run(self):
        """Main watcher loop."""
        logger.info("Starting LinkedInWatcher")
        print("")
        print("=" * 60)
        print("=== LinkedIn Watcher STARTED ===")
        print("=" * 60)
        print(f"Monitoring for: messages, mentions, notifications")
        print(f"Business keywords: {BUSINESS_KEYWORDS[:5]}...")
        print(f"Check interval: {self.check_interval} seconds")
        print("")
        print("💼 TEST MODE: Will create files for ANY conversations")
        print("⚡ Press Ctrl+C to stop")
        print("")
        print("=== TEST MODE ENABLED ===")
        print("")

        try:
            if not self._init_browser():
                print("Failed to initialize browser")
                return

            if not self._load_session():
                print("No valid session found")
                if not self._wait_for_login():
                    print("Login timeout or cancelled")
                    return

            print("\n✓ LinkedIn loaded successfully!")
            print("Starting monitoring loop...\n")

            poll_count = 0
            while not shutdown_requested:
                poll_count += 1
                print(f"\n[Poll #{poll_count}] Checking LinkedIn...")
                
                try:
                    items = self.check_for_updates()
                    if items:
                        print(f"\n>>> Found {len(items)} new item(s)")
                        for item in items:
                            self.create_action_file(item)
                        print(f">>> Processed {len(items)} item(s)")
                    else:
                        print("No new LinkedIn activity")
                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    print(f"Error during polling: {e}")

                print(f"\nWaiting {self.check_interval} seconds before next check...")
                for i in range(self.check_interval):
                    if shutdown_requested:
                        print("\nShutdown detected, exiting loop...")
                        break
                    time.sleep(1)
                
                if shutdown_requested:
                    break

        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")
        except Exception as e:
            logger.critical(f"Fatal: {e}")
            print(f"\nFatal error: {e}")
        finally:
            self.cleanup()
            print("\n✓ LinkedIn Watcher stopped.")


if __name__ == "__main__":
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent.resolve())
    watcher = LinkedInWatcher(vault_path=vault_path)
    watcher.run()
