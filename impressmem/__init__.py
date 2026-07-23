"""
ImpressMem - Impression-based Memory Management Library
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("impressmem")
except PackageNotFoundError:
    __version__ = "0.0.0"

from impressmem.config import ImpressMemConfig
from impressmem.manager import ImpressMemManager
from impressmem.tools import (
    SaveImpressionTool,
    OrganizeImpressionsTool,
    RecallImpressionsTool,
)
from impressmem.utils import slice_new_turn_messages

__all__ = [
    "ImpressMemConfig",
    "ImpressMemManager",
    "SaveImpressionTool",
    "OrganizeImpressionsTool",
    "RecallImpressionsTool",
    "slice_new_turn_messages",
]
