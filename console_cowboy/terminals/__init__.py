"""
Terminal emulator parsers and exporters.

This module provides classes for reading and writing configuration files
for various terminal emulators.
"""

from .base import TerminalAdapter, TerminalRegistry
from .iterm2 import ITerm2Adapter
from .ghostty import GhosttyAdapter
from .alacritty import AlacrittyAdapter
from .kitty import KittyAdapter
from .wezterm import WeztermAdapter

# Register all adapters
TerminalRegistry.register(ITerm2Adapter)
TerminalRegistry.register(GhosttyAdapter)
TerminalRegistry.register(AlacrittyAdapter)
TerminalRegistry.register(KittyAdapter)
TerminalRegistry.register(WeztermAdapter)

__all__ = [
    "TerminalAdapter",
    "TerminalRegistry",
    "ITerm2Adapter",
    "GhosttyAdapter",
    "AlacrittyAdapter",
    "KittyAdapter",
    "WeztermAdapter",
]
