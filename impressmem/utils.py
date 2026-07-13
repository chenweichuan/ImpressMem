"""
Utility functions for ImpressMem
"""
import logging

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


def stringify_message_content(content: str | list) -> str:
    """Stringify message content"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if part.get("type") == "text":
                    parts.append(part.get("text", ""))
                # For other types (image, video), we'll just note they exist
                elif part.get("type") in ["image", "video"]:
                    parts.append(f"[{part.get('type', 'media')}]")
        return "\n".join(parts)
    return ""


def stringify_message(message: dict) -> str:
    """Stringify a single message"""
    role = message.get("role", "")
    content = stringify_message_content(message.get("content", ""))
    return f"{role}: {content}"


def count_messages_text_units(messages: list[dict]) -> int:
    """Count text units for a list of messages"""
    total = 0
    for msg in messages:
        total += count_text_units(stringify_message(msg))
    return total