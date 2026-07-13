"""
Configuration for ImpressMem
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Config:
    """Configuration class for ImpressMem
    
    Args:
        bot_name: Name of the bot/assistant (default: "ImpressMem Bot")
        bot_alias: Alias of the bot/assistant (default: "")
        owner_name: Name of the owner (default: "")
        memory_model: LLM model to use for memory processing (default: "gpt-4o")
        redis_config: Redis configuration dictionary (default: {"host": "localhost", "port": 6379, "db": 0})
    """
    bot_name: str = "ImpressMem Bot"
    bot_alias: str = ""
    owner_name: str = ""
    memory_model: str = "gpt-4o"
    redis_config: Dict[str, Any] = field(default_factory=lambda: {"host": "localhost", "port": 6379, "db": 0})