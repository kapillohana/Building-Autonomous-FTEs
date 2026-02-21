#!/usr/bin/env python3
"""
File System Watcher
Monitors a designated folder for new files and moves them to /Needs_Action
with auto-generated metadata.

Part of Bronze Tier AI Employee implementation.
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='../logs/filesystem_watcher.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileSystemWatcher')


class DropFolderHandler(FileSystemEventHandler):
    """Handles file drop events and creates metadata."""

    def __init__(self, vault_path: str, watch_folder: str = 'Drop'):
        self.vault_path = Path(vault_path)
        self.watch_folder = Path(watch_folder)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.processed_files = set()
        logger.info(f'Initialized FileSystemWatcher for {watch_folder}')

    def on_created(self, event):
        """Called when a file is created in the monitored folder."""
        if event.is_directory:
            logger.debug(f'Directory created: {event.src_path} (ignored)')
            return

        try:
            source = Path(event.src_path)

            # Skip hidden files and temp files
            if source.name.startswith('.') or source.name.endswith('.tmp'):
                logger.debug(f'Skipping hidden/temp file: {source.name}')
                return

            # Avoid processing same file twice
            file_hash = self._get_file_hash(source)
            if file_hash in self.processed_files:
                logger.debug(f'File already processed: {source.name}')
                return

            self.processed_files.add(file_hash)

            # Wait for file to be fully written
            time.sleep(0.5)

            if not source.exists():
                logger.warning(f'File disappeared: {source.name}')
                return

            # Create action file
            self._create_action_file(source)
            logger.info(f'File processed: {source.name}')

        except Exception as e:
            logger.error(f'Error processing file: {e}')

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate a hash of file to detect duplicates."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return file_path.name

    def _create_action_file(self, source: Path) -> Path:
        """Create metadata markdown file for the dropped file."""

        # Generate unique filename for action file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_stem = source.stem.replace(' ', '_')
        action_filename = f'FILE_{file_stem}_{timestamp}.md'
        action_path = self.needs_action / action_filename

        # Get file info
        file_size = source.stat().st_size
        file_mtime = datetime.fromtimestamp(source.stat().st_mtime).isoformat()

        # Create metadata content
        metadata = f'''---
type: file_drop
original_name: {source.name}
original_path: {source.absolute()}
file_size: {file_size}
file_extension: {source.suffix}
received: {datetime.now().isoformat()}
last_modified: {file_mtime}
status: pending
---

## File Dropped for Processing

**Name:** {source.name}
**Size:** {self._format_size(file_size)}
**Type:** {source.suffix if source.suffix else 'No extension'}
**Location:** {source.parent}

## Suggested Actions

- [ ] Review file contents
- [ ] Move to appropriate processing folder
- [ ] Archive after processing
- [ ] Flag for approval if needed

## Processing Notes

_Add notes about processing here_
'''

        try:
            action_path.write_text(metadata)
            logger.info(f'Created action file: {action_path}')
            return action_path
        except Exception as e:
            logger.error(f'Failed to create action file: {e}')
            raise

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f'{bytes_size:.1f} {unit}'
            bytes_size /= 1024
        return f'{bytes_size:.1f} TB'


def watch_folder(vault_path: str, watch_folder: str = 'Drop', check_interval: int = 10):
    """
    Start watching a folder for file drops.

    Args:
        vault_path: Path to the Obsidian vault
        watch_folder: Folder to monitor (relative to current directory)
        check_interval: Polling interval in seconds
    """
    logger.info(f'Starting File System Watcher')
    logger.info(f'Vault path: {vault_path}')
    logger.info(f'Watch folder: {watch_folder}')

    # Create watch folder if it doesn't exist
    watch_path = Path(watch_folder)
    watch_path.mkdir(parents=True, exist_ok=True)

    # Create event handler and observer
    event_handler = DropFolderHandler(vault_path, watch_folder)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)

    # Start observer
    observer.start()
    logger.info(f'Observer started, monitoring: {watch_path.absolute()}')

    try:
        while True:
            time.sleep(check_interval)
    except KeyboardInterrupt:
        logger.info('Shutting down File System Watcher')
        observer.stop()
    observer.wait_for_completion()


if __name__ == '__main__':
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    watch_folder = sys.argv[2] if len(sys.argv) > 2 else 'Drop'

    watch_folder(vault_path, watch_folder)
