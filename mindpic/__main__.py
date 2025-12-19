# File: mindpic/__main__.py
# -*- coding: utf-8 -*-


from __future__ import annotations

import logging
import tkinter as tk

from .app import MindPicApp
from . import settings
from .paths import get_log_path


def setup_logging() -> None:
    """Configure logging based on settings."""
    log_path = get_log_path()

    # Get log level from settings
    level_name = settings.LOG_LEVEL.upper()
    level = getattr(logging, level_name, logging.INFO)

    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"MindPic starting (log level: {level_name})")
    logger.debug(f"Log file: {log_path}")


def main() -> None:
    # Setup logging first
    try:
        setup_logging()
    except Exception as e:
        # Fallback: basic config if log setup fails
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"Could not setup logging: {e}")

    # Start app
    root = tk.Tk()
    _app = MindPicApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
