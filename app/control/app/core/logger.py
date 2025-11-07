"""Minimal logging helpers for the control service."""
from __future__ import annotations

import logging
from typing import Optional

_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str) -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        _LOGGER = logging.getLogger("aionos")
    return _LOGGER.getChild(name)
