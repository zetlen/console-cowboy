"""
CTEC - Common Terminal Emulator Configuration

A portable configuration format for terminal emulators that enables
migration of settings between different terminal applications.
"""

from .schema import (
    CTEC,
    ColorScheme,
    ColorVariant,
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
    TerminalSpecificSetting,
)
from .serializers import CTECSerializer, OutputFormat, CTEC_JSON_SCHEMA

__all__ = [
    "CTEC",
    "ColorScheme",
    "ColorVariant",
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
    "TerminalSpecificSetting",
    "CTECSerializer",
    "OutputFormat",
    "CTEC_JSON_SCHEMA",
]
