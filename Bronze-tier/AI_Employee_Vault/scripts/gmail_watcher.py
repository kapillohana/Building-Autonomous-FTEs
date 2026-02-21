from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import json
import os
from pathlib import Path
from base_watcher import BaseWatcher
import logging
import sys

# ────────────────────────────────────────────────────────────────
# Debug / Visibility (temporary - remove or comment later)
print("=== GmailWatcher STARTED ===")
print(f"Logging to: {os.path.abspath('../logs/watcher.log')}")
print("Press Ctrl+C to stop")
print(f"Python version: {sys.version}")
print(f"Current dir: {os.getcwd()}")
# ────────────────────────────────────────────────────────────────

# Logging setup - console + file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/watcher.log', mode='a'),
        logging.StreamHandler(sys.stdout)  # show in terminal too
    ]
)
logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = '../scripts/credentials.json', check_interval: int = 120):
        super().__init__(vault_path, check_interval)

        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Needs_Action: {self.needs_action}")

        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']  # read + modify (or use gmail.readonly)

        try:
            creds = None
            token_path = Path('../scripts/token.json').resolve()

            # Load existing token if available
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                logger.info("Loaded existing token")

            # If no valid creds → run full OAuth flow (opens browser)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                else:
                    logger.info("No valid token - starting OAuth flow (browser will open)")
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)  # opens browser automatically

                # Save the token for next time
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                logger.info("Token saved to token.json")

            self.creds = creds
            self.service = build('gmail', 'v1', credentials=self.creds)

            self.processed_ids_file = Path('../logs/processed_gmail_ids.json').resolve()
            if self.processed_ids_file.exists():
                with open(self.processed_ids_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_ids)} processed IDs")
            else:
                self.processed_ids = set()
                logger.info("Starting with empty processed IDs")

            logger.info("GmailWatcher initialized successfully")
            print("Initialization complete - Gmail API ready")

        except FileNotFoundError as e:
            logger.error(f"Credentials file missing: {credentials_path}")
            print(f"ERROR: {credentials_path} not found. Download from https://console.cloud.google.com/apis/credentials")
            raise
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            print(f"Initialization failed: {str(e)}")
            raise

    def check_for_updates(self) -> list:
        try:
            print("Polling Gmail now...")
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important'
            ).execute()
            messages = results.get('messages', [])
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            logger.info(f"Found {len(new_messages)} new unread important messages")
            print(f"Found {len(new_messages)} new messages")

            return new_messages
        except Exception as e:
            logger.error(f"Polling error: {str(e)}")
            print(f"Polling error: {str(e)}")
            return []

    def create_action_file(self, message) -> Path:
        try:
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{msg.get('snippet', '')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
"""

            filepath = self.needs_action / f"EMAIL_{message['id']}.md"
            filepath.write_text(content, encoding='utf-8')

            self.processed_ids.add(message['id'])
            with open(self.processed_ids_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_ids), f)

            logger.info(f"Created action file: {filepath}")
            print(f"-> Created: {filepath.name}")

            return filepath
        except Exception as e:
            logger.error(f"Error creating file for {message['id']}: {str(e)}")
            print(f"Create file error: {str(e)}")
            raise


if __name__ == "__main__":
    try:
        vault_path = str(Path(__file__).parent.parent.resolve())  # AI_Employee_Vault
        watcher = GmailWatcher(vault_path=vault_path)
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user (Ctrl+C)")
        print("\nWatcher stopped gracefully.")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        print(f"Fatal: {str(e)}")
        sys.exit(1)