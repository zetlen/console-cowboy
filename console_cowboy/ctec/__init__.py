"""
CTEC - Common Terminal Emulator Configuration

A portable configuration format for terminal emulators that enables
migration of settings between different terminal applications.
"""

from .schema import (
    CTEC,
    ColorScheme,
    Color,
    FontConfig,
    FontWeight,
    FontStyle,
    CursorConfig,
    CursorStyle,
    WindowConfig,
    BehaviorConfig,
    BellMode,
    ScrollConfig,
    KeyBinding,
    Profile,
    TerminalSpecificSetting,
)
from .serializers import CTECSerializer

__all__ = [
    "CTEC",
    "ColorScheme",
    "Color",
    "FontConfig",
    "FontWeight",
    "FontStyle",
    "CursorConfig",
    "CursorStyle",
    "WindowConfig",
    "BehaviorConfig",
    "BellMode",
    "ScrollConfig",
    "KeyBinding",
    "Profile",
    "TerminalSpecificSetting",
    "CTECSerializer",
]
