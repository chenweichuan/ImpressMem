"""
Utility functions for ImpressMem
"""
import logging
from typing import Any, Dict, List

# Setup logger
logger = logging.getLogger("impressmem")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def count_text_units(text: str) -> int:
    """Count text units (tokens approximation)"""
    # Simple implementation: count characters, ~1 token per 4 chars
    return len(text) // 4

def slice_new_turn_messages(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Slice the new turn-of-conversation messages from the history

    Args:
        history: Conversation history

    Returns:
        List of new turn-of-conversation messages
    """
    # Extract last bot message with previous bot message as context (include user messages in between if any)
    last_bot_idx = len(history) - 1 - next((i for i, msg in enumerate(reversed(history)) if msg["role"] == "assistant"), 0)
    prev_bot_idx = len(history[:last_bot_idx]) - 1 - next((i for i, msg in enumerate(reversed(history[:last_bot_idx])) if msg["role"] == "assistant"), 0)
    return history[prev_bot_idx:]
