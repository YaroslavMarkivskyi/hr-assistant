from __future__ import annotations
import logging
import re

from anyascii import anyascii


logger = logging.getLogger(__name__)


def is_cyrillic(text: str) -> bool:
    """Check if the given text contains any Cyrillic characters."""
    return bool(re.search('[\u0400-\u04FF]', text))


def transliterate_for_azure(text: str) -> str:
    if not text:
        return ""
    
    try:
        
        res = anyascii(text)
        res = re.sub(r'[^A-Za-z0-9]+', '', res)
        return res.lower()
    except Exception as e:
        logger.error(f"Transliteration failed for text '{text}': {e}", exc_info=True)
        return ""
    

__all__ = (
    'is_cyrillic',
    'transliterate_for_azure',
)

