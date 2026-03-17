#!/usr/bin/env python3
"""
WhatsApp Watcher - Silver Tier
Monitors WhatsApp Web for new messages with urgent keywords.
Uses Playwright for browser automation with session persistence.
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
browser_instance = None  # Global reference for cleanup

def signal_handler(sig, frame):
    global shutdown_requested
    shutdown_requested = True
    logger.info("Shutdown signal received (Ctrl+C)")
    print("\n⚠ Shutdown requested, cleaning up...")
    # Force immediate cleanup
    if browser_instance:
        try:
            browser_instance.close()
        except:
            pass
    sys.exit(0)

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
logger = logging.getLogger('WhatsAppWatcher')

# ────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help']
SESSION_FILE = Path('../scripts/whatsapp_session.json').resolve()
SCREENSHOT_DIR = Path('../logs/screenshots').resolve()
MAX_RETRIES = 3
CHECK_INTERVAL = 120  # seconds
WHATSAPP_URL = 'https://web.whatsapp.com'


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Web watcher using Playwright.
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

        self.processed_messages = set()
        self._load_processed_messages()

        # Create required directories
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Ensure logs directory exists
        logs_dir = Path('../logs').resolve()
        logs_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Session file: {self.session_file}")
        logger.info(f"Screenshot dir: {SCREENSHOT_DIR}")
        
        # Print session file status
        if self.session_file.exists():
            print(f"✓ Session file found: {self.session_file}")
        else:
            print(f"ℹ No session file yet (will create after QR scan)")

    def _load_processed_messages(self):
        processed_file = Path('../logs/processed_whatsapp_ids.json').resolve()
        if processed_file.exists():
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    self.processed_messages = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_messages)} processed IDs")
            except:
                self.processed_messages = set()
        else:
            self.processed_messages = set()

    def _save_processed_messages(self):
        processed_file = Path('../logs/processed_whatsapp_ids.json').resolve()
        try:
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_messages), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save processed: {e}")

    def _init_browser(self) -> bool:
        for attempt in range(MAX_RETRIES):
            try:
                self.playwright = sync_playwright().start()

                print("")
                print("=" * 60)
                print("=== OPENING WHATSAPP WEB ===")
                print("=" * 60)

                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    slow_mo=50,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--window-size=1280,720',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu'
                    ]
                )
                
                # Store global reference for cleanup
                global browser_instance
                browser_instance = self.browser

                self.context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1280, 'height': 720}
                )

                self.page = self.context.new_page()
                self.page.set_default_timeout(90000)

                print("Navigating to WhatsApp Web...")
                self.page.goto(WHATSAPP_URL, wait_until='domcontentloaded', timeout=60000)
                
                # Wait for page to fully load
                self.page.wait_for_timeout(5000)

                logger.info("Browser initialized")
                return True

            except Exception as e:
                logger.warning(f"Init attempt {attempt+1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                else:
                    logger.error(f"All browser init attempts failed")
                    return False
        return False

    def _load_session(self) -> bool:
        if not self.session_file.exists():
            print("No session file found")
            return False

        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            # Check if session is recent (within 7 days)
            if 'timestamp' in session_data:
                session_time = datetime.fromisoformat(session_data['timestamp'])
                age_hours = (datetime.now() - session_time).total_seconds() / 3600
                print(f"Session age: {age_hours:.2f} hours")
                if age_hours > 168:  # 7 days
                    print(f"Session expired ({age_hours:.1f} hours old)")
                    return False

            # Add cookies
            if 'cookies' in session_data and session_data['cookies']:
                self.context.add_cookies(session_data['cookies'])
                print(f"✓ Loaded {len(session_data['cookies'])} cookies from session")

            # Navigate to WhatsApp
            print("Loading WhatsApp Web with saved session...")
            self.page.goto(WHATSAPP_URL, wait_until='domcontentloaded', timeout=60000)
            self.page.wait_for_timeout(10000)  # Wait longer for page to load

            # Take a screenshot to debug
            debug_screenshot = SCREENSHOT_DIR / 'session_check.png'
            self.page.screenshot(path=str(debug_screenshot))
            print(f"Debug screenshot saved: {debug_screenshot}")

            # Check if logged in
            if self._is_logged_in():
                print("✓ Session loaded successfully - you're logged in!")
                return True
            else:
                print("⚠ Session found but not logged in (QR may be showing)")
                return False

        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def _save_session(self):
        try:
            # Get cookies
            cookies = self.context.cookies()
            
            # Get localStorage data via JavaScript
            try:
                local_storage = self.page.evaluate('() => { return JSON.stringify(localStorage) }')
            except:
                local_storage = None

            session_data = {
                'cookies': cookies,
                'localStorage': local_storage,
                'timestamp': datetime.now().isoformat(),
                'url': self.page.url
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"✓ Session saved to: {self.session_file}")
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Save session failed: {e}")
            print(f"Warning: Could not save session: {e}")

    def _is_logged_in(self) -> bool:
        """Check if WhatsApp Web is logged in by looking for chat list."""
        try:
            # Wait a bit for page to settle
            self.page.wait_for_timeout(1000)
            
            # Multiple indicators of being logged in
            indicators = [
                '[data-testid="chat-list"]',
                '#pane-side',
                'div[role="main"]',
                '[data-testid="default-user"]'
            ]
            
            for sel in indicators:
                try:
                    if self.page.query_selector(sel):
                        return True
                except:
                    pass
            
            # Also check URL - if we're still at web.whatsapp.com without QR, we're likely logged in
            current_url = self.page.url
            if 'web.whatsapp.com' in current_url and not self.page.query_selector('[data-testid="qr-icon"]'):
                return True
                
        except Exception as e:
            logger.debug(f"Login check error: {e}")
        
        return False

    def _wait_for_qr_scan(self) -> bool:
        print("")
        print("=== SCAN QR CODE NOW ===")
        print("1. Open WhatsApp on phone")
        print("2. Settings/Menu → Linked Devices")
        print("3. Link a Device")
        print("4. Scan the QR code")
        print("")
        
        max_wait = 120
        elapsed = 0
        
        while elapsed < max_wait:
            if shutdown_requested:
                return False
            
            if self._is_logged_in():
                print("✓ QR scanned!")
                self._save_session()
                return True
            
            time.sleep(3)
            elapsed += 3
            if elapsed % 15 == 0:
                print(f"Waiting... {elapsed}s")
        
        return False

    def _get_unread_messages(self) -> List[Dict[str, Any]]:
        """Find unread messages by looking for unread indicators and reading messages."""
        messages = []

        try:
            # Reload page to get fresh data
            print("Refreshing page...")
            self.page.reload(wait_until='domcontentloaded')
            self.page.wait_for_timeout(8000)

            # Take screenshot for debugging
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = SCREENSHOT_DIR / f'debug_{timestamp}.png'
            self.page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved: {screenshot_path}")

            # Wait for chat list - try multiple selectors
            chat_list_found = False
            chat_selectors = [
                'div[role="row"]',
                '[data-testid="chat-list"]',
                '#pane-side',
                'div[data-testid="chat-list"]'
            ]
            
            for selector in chat_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000)
                    print(f"Found chat list with selector: {selector}")
                    chat_list_found = True
                    break
                except:
                    continue
            
            if not chat_list_found:
                print("Chat list not found - page may not be fully loaded")
                self.page.wait_for_timeout(10000)
                if not self.page.query_selector('div[role="row"]'):
                    return []

            self.page.wait_for_timeout(3000)

            # Get all chats
            chats = self.page.query_selector_all('div[role="row"]')
            print(f"Found {len(chats)} total chats")

            if not chats:
                print("No chats found")
                return []

            # Look for unread indicators
            unread_chats = []

            for idx, chat in enumerate(chats[:50]):
                try:
                    # Get chat name
                    chat_name = "Unknown"
                    
                    name_elem = chat.query_selector('[data-testid="chat-item-name"]')
                    if name_elem:
                        chat_name = name_elem.inner_text().strip()
                    
                    if not chat_name or chat_name == "Unknown":
                        span_elem = chat.query_selector('span[dir="auto"]')
                        if span_elem:
                            chat_name = span_elem.inner_text().strip()
                    
                    if not chat_name or len(chat_name) < 2:
                        aria = chat.get_attribute('aria-label')
                        if aria:
                            chat_name = aria.split(',')[0].strip()[:30]
                    
                    if not chat_name or chat_name == "Unknown" or len(chat_name) < 2:
                        continue

                    # Check for unread - multiple methods
                    has_unread = False
                    unread_count = 0

                    # Method 1: Look for any span/em with a number (unread count badge)
                    all_spans = chat.query_selector_all('span, em')
                    for span in all_spans:
                        span_text = span.inner_text().strip()
                        span_class = span.get_attribute('class') or ''
                        
                        # Check if it's a number (unread count)
                        if span_text and span_text.isdigit() and int(span_text) > 0:
                            has_unread = True
                            unread_count = int(span_text)
                            print(f"  ✓ [{idx}] {chat_name}: Unread badge '{span_text}'")
                            break
                        
                        # Check for green badge indicator (has background style)
                        span_style = span.get_attribute('style') or ''
                        if 'badge' in span_class.lower() or ('background' in span_style.lower() and span_text):
                            has_unread = True
                            unread_count = 1
                            print(f"  ✓ [{idx}] {chat_name}: Badge detected")
                            break

                    # Method 2: Check aria-label
                    if not has_unread:
                        aria = chat.get_attribute('aria-label')
                        if aria:
                            aria_lower = aria.lower()
                            if 'unread' in aria_lower or 'new' in aria_lower:
                                has_unread = True
                                unread_count = 1
                                print(f"  ✓ [{idx}] {chat_name}: ARIA indicates unread")

                    # Method 3: Check for specific unread indicators
                    if not has_unread:
                        unread_indicators = [
                            '[data-testid="unread-count"]',
                            '[data-testid="unread"]',
                            '.unread-count',
                            '.unread',
                        ]
                        for indicator in unread_indicators:
                            elem = chat.query_selector(indicator)
                            if elem:
                                has_unread = True
                                unread_count = 1
                                print(f"  ✓ [{idx}] {chat_name}: Indicator found")
                                break

                    if has_unread:
                        unread_chats.append({
                            'chat_name': chat_name,
                            'unread_count': unread_count,
                            'element_idx': idx
                        })

                except Exception as e:
                    logger.debug(f"Error checking chat {idx}: {e}")

            print(f"\nTotal unread chats found: {len(unread_chats)}")

            if not unread_chats:
                print("No unread messages detected")
                return []

            # Click into each unread chat and read the message
            for chat_info in unread_chats:
                chat_name = chat_info['chat_name']

                try:
                    print(f"\nOpening chat: {chat_name}...")
                    chats = self.page.query_selector_all('div[role="row"]')

                    if chat_info['element_idx'] < len(chats):
                        chats[chat_info['element_idx']].click()
                    else:
                        for chat in chats:
                            name_elem = chat.query_selector('[data-testid="chat-item-name"]')
                            if name_elem:
                                elem_name = name_elem.inner_text().strip()
                                if elem_name == chat_name:
                                    chat.click()
                                    break

                    self.page.wait_for_timeout(5000)

                    # Get last message - improved extraction
                    last_message = ""
                    
                    # Method 1: Get all message bubbles and find the last text content
                    msg_bubbles = self.page.query_selector_all('div[data-testid="message-bubble"]')
                    if msg_bubbles:
                        # Get the last message bubble
                        last_bubble = msg_bubbles[-1]
                        # Try to get text from spans inside
                        spans = last_bubble.query_selector_all('span[dir="auto"]')
                        for span in reversed(spans):
                            txt = span.inner_text().strip()
                            # Skip timestamps (short, contains AM/PM or just numbers)
                            if txt and len(txt) > 5 and len(txt) < 500:
                                if not any(x in txt.lower() for x in ['am', 'pm', ':']):
                                    last_message = txt
                                    break
                    
                    # Method 2: Try message-text containers
                    if not last_message:
                        msg_containers = self.page.query_selector_all('div[data-testid="message-text"]')
                        if msg_containers:
                            for container in reversed(msg_containers[-5:]):
                                txt = container.inner_text().strip()
                                if txt and len(txt) > 5 and len(txt) < 500:
                                    last_message = txt
                                    break

                    # Method 3: Fallback - all spans in main area
                    if not last_message:
                        main_area = self.page.query_selector('div[role="main"]')
                        if main_area:
                            spans = main_area.query_selector_all('span[dir="auto"]')
                            for span in reversed(spans[-15:]):
                                txt = span.inner_text().strip()
                                # Skip timestamps and dates
                                if txt and len(txt) > 5 and len(txt) < 500:
                                    if not any(x in txt.lower() for x in ['am', 'pm']):
                                        if not txt.replace('.', '').replace(',', '').isdigit():
                                            last_message = txt
                                            break

                    print(f"  Message: {last_message[:80] if last_message else 'EMPTY'}...")

                    # Go back to chat list
                    back = self.page.query_selector('[data-testid="back"]')
                    if back:
                        back.click()
                        self.page.wait_for_timeout(2000)
                    else:
                        self.page.reload(wait_until='domcontentloaded')
                        self.page.wait_for_timeout(3000)

                    # Check for urgent keywords
                    has_keyword = any(kw in last_message.lower() for kw in URGENT_KEYWORDS)

                    msg_id = f"{chat_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    if msg_id not in self.processed_messages:
                        messages.append({
                            'id': msg_id,
                            'chat_name': chat_name,
                            'last_message': last_message,
                            'unread_count': chat_info['unread_count'],
                            'has_urgent_keyword': has_keyword,
                            'timestamp': datetime.now().isoformat()
                        })

                        if has_keyword:
                            print(f"  🔥 KEYWORD MATCH!")
                        else:
                            print(f"  (no keyword match)")

                except Exception as e:
                    logger.error(f"Error reading chat {chat_name}: {e}")
                    print(f"  Error: {e}")
                    try:
                        self.page.reload(wait_until='domcontentloaded')
                        self.page.wait_for_timeout(3000)
                    except:
                        pass

            print(f"\nTotal messages to process: {len(messages)}")

        except Exception as e:
            logger.error(f"Error in get_unread: {e}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        return messages

    def check_for_updates(self) -> list:
        for attempt in range(MAX_RETRIES):
            try:
                print("\n" + "=" * 50)
                print("POLLING WHATSAPP...")
                print("=" * 50)
                
                if not self.page:
                    if not self._init_browser():
                        continue
                    if not self._load_session():
                        if not self._wait_for_qr_scan():
                            return []
                
                if not self._is_logged_in():
                    print("Not logged in, reloading...")
                    if not self._load_session():
                        if not self._wait_for_qr_scan():
                            return []
                
                messages = self._get_unread_messages()
                self._save_session()
                return messages
                
            except Exception as e:
                logger.error(f"Poll error {attempt+1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                else:
                    return []
        return []

    def create_action_file(self, message: Dict[str, Any]) -> Path:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chat_name_safe = message['chat_name'].replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')[:30]
            filename = f"WHATSAPP_{chat_name_safe}_{timestamp}.md"
            filepath = self.needs_action / filename

            priority = 'high' if message.get('has_urgent_keyword', False) else 'medium'

            # Format message content - handle empty messages
            message_content = message.get('last_message', '')
            if not message_content or len(message_content) < 2:
                message_content = "_No text content (may be image, voice message, or other media)_"

            content = f"""---
type: whatsapp
from: {message['chat_name']}
received: {message['timestamp']}
priority: {priority}
status: pending
unread_count: {message['unread_count']}
keywords_detected: {message.get('has_urgent_keyword', False)}
---

## WhatsApp Message

**From:** {message['chat_name']}
**Received:** {message['timestamp']}
**Unread Count:** {message['unread_count']}
**Priority:** {priority.upper()}
**Urgent Keywords:** {'Yes' if message.get('has_urgent_keyword', False) else 'No'}

## Message Content

{message_content}

## Suggested Actions

- [ ] Review message content
- [ ] Reply to sender
- [ ] Flag for approval if needed
- [ ] Archive after processing

## Processing Notes

_Add notes about processing here_
"""

            filepath.write_text(content, encoding='utf-8')
            self.processed_messages.add(message['id'])
            self._save_processed_messages()

            keyword_flag = " 🔥" if message.get('has_urgent_keyword', False) else ""
            print(f"✓ Created: {filename}{keyword_flag}")
            logger.info(f"Created: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating file: {e}")
            raise

    def cleanup(self):
        """Clean up browser and playwright resources."""
        print("\nCleaning up resources...")
        try:
            # Save session before closing
            if self.page and self.context:
                print("Saving session before exit...")
                self._save_session()
            
            if self.browser:
                print("Closing browser...")
                self.browser.close()
                self.browser = None
            if self.playwright:
                print("Stopping Playwright...")
                self.playwright.stop()
                self.playwright = None
            print("Cleanup complete.")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        finally:
            global browser_instance
            browser_instance = None

    def run(self):
        logger.info("Starting WhatsAppWatcher")
        print("")
        print("=" * 60)
        print("=== WhatsApp Watcher STARTED ===")
        print("=" * 60)
        print(f"Monitoring for unread messages...")
        print(f"Urgent keywords: {URGENT_KEYWORDS}")
        print(f"Check interval: {self.check_interval} seconds")
        print("")
        print("📱 Send a test message with 'urgent' or 'payment' to test")
        print("⚡ Press Ctrl+C to stop")
        print("")

        try:
            # Initialize browser
            if not self._init_browser():
                print("Failed to initialize browser")
                return

            # Load session or wait for QR scan
            if not self._load_session():
                print("No valid session found")
                if not self._wait_for_qr_scan():
                    print("QR scan timeout or cancelled")
                    return

            print("\n✓ WhatsApp Web loaded successfully!")
            print("Starting monitoring loop...\n")

            poll_count = 0
            while not shutdown_requested:
                poll_count += 1
                print(f"\n[Poll #{poll_count}] Checking for unread messages...")
                
                try:
                    items = self.check_for_updates()
                    if items:
                        print(f"Found {len(items)} unread message(s) to process")
                        for item in items:
                            self.create_action_file(item)
                        print(f"Processed {len(items)} message(s)")
                    else:
                        print("No new unread messages")
                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    print(f"Error during polling: {e}")

                # Wait between polls
                print(f"Waiting {self.check_interval} seconds before next check...")
                for _ in range(self.check_interval):
                    if shutdown_requested:
                        break
                    time.sleep(1)

        except Exception as e:
            logger.critical(f"Fatal: {e}")
            print(f"\nFatal error: {e}")
        finally:
            self.cleanup()
            print("\n✓ WhatsApp Watcher stopped.")


if __name__ == "__main__":
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent.resolve())
    watcher = WhatsAppWatcher(vault_path=vault_path)
    watcher.run()
