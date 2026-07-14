"""
Configuration for ImpressMem
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Config:
    """Configuration class for ImpressMem
    
    Args:
        bot_name: Name of the bot/assistant (default: "Bot")
        redis_config: Redis configuration dictionary (default: {"host": "localhost", "port": 6379, "db": 0})
    """
    bot_name: str = "Bot"
    redis_config: Dict[str, Any] = field(default_factory=lambda: {"host": "localhost", "port": 6379, "db": 0})
