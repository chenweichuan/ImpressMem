"""
Configuration for ImpressMem
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ImpressMemConfig:
    """Configuration class for ImpressMem
    
    Args:
        bot_name: Name of the bot/assistant (default: "Bot")
        redis_config: Redis configuration dictionary (default: {"host": "localhost", "port": 6379, "db": 0})
        categories_per_set: Maximum number of categories to keep (default: 500)
        labels_per_set: Maximum number of labels to keep (default: 1500)
        clues_per_set: Maximum number of clues to keep (default: 500)
        impression_text_units_per_set: Maximum text units for impressions (default: 15000)
        unpinned_emoji: Emoji for unpinned impressions (default: "⚪")
        pinned_emoji: Emoji for pinned impressions (default: "📌")
    """
    bot_name: str = "Bot"
    redis_config: Dict[str, Any] = field(default_factory=lambda: {"host": "localhost", "port": 6379, "db": 0})
    categories_per_set: int = 500
    labels_per_set: int = 1500
    clues_per_set: int = 500
    impression_text_units_per_set: int = 15000
    unpinned_emoji: str = "⚪"
    pinned_emoji: str = "📌"
