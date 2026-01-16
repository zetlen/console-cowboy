"""
iTerm2 configuration adapter.

iTerm2 uses a macOS plist format for its configuration, stored in
~/Library/Preferences/com.googlecode.iterm2.plist

Color schemes can also be stored as separate .itermcolors files.
"""

import plistlib
from pathlib import Path
from typing import Optional, Union

from console_cowboy.ctec.schema import (
    CTEC,
    BehaviorConfig,
    BellMode,
    Color,
    ColorScheme,
    CursorConfig,
    CursorStyle,
    FontConfig,
    KeyBinding,
    Profile,
    WindowConfig,
)
from console_cowboy.utils.colors import color_to_float_tuple, float_tuple_to_color

from .base import TerminalAdapter


class ITerm2Adapter(TerminalAdapter):
    """
    Adapter for iTerm2 terminal emulator.

    Supports parsing:
    - Full iTerm2 plist configuration
    - .itermcolors color scheme files

    Note: iTerm2 uses plist format with colors stored as floating point
    RGB values (0.0-1.0).
    """

    name = "iterm2"
    display_name = "iTerm2"
    description = "macOS terminal emulator with extensive customization options"
    config_extensions = [".plist", ".itermcolors"]
    default_config_paths = [
        "Library/Preferences/com.googlecode.iterm2.plist",
    ]

    # Mapping of iTerm2 cursor styles to CTEC
    CURSOR_STYLE_MAP = {
        0: CursorStyle.UNDERLINE,
        1: CursorStyle.BLOCK,
        2: CursorStyle.BEAM,
    }

    CURSOR_STYLE_REVERSE_MAP = {v: k for k, v in CURSOR_STYLE_MAP.items()}

    # Color key mappings from iTerm2 to CTEC
    COLOR_KEY_MAP = {
        "Foreground Color": "foreground",
        "Background Color": "background",
        "Cursor Color": "cursor",
        "Cursor Text Color": "cursor_text",
        "Selection Color": "selection",
        "Selected Text Color": "selection_text",
        "Ansi 0 Color": "black",
        "Ansi 1 Color": "red",
        "Ansi 2 Color": "green",
        "Ansi 3 Color": "yellow",
        "Ansi 4 Color": "blue",
        "Ansi 5 Color": "magenta",
        "Ansi 6 Color": "cyan",
        "Ansi 7 Color": "white",
        "Ansi 8 Color": "bright_black",
        "Ansi 9 Color": "bright_red",
        "Ansi 10 Color": "bright_green",
        "Ansi 11 Color": "bright_yellow",
        "Ansi 12 Color": "bright_blue",
        "Ansi 13 Color": "bright_magenta",
        "Ansi 14 Color": "bright_cyan",
        "Ansi 15 Color": "bright_white",
    }

    COLOR_KEY_REVERSE_MAP = {v: k for k, v in COLOR_KEY_MAP.items()}

    @classmethod
    def _parse_iterm_color(cls, color_dict: dict) -> Color:
        """Parse an iTerm2 color dictionary to a Color object."""
        # iTerm2 uses "Color Space" and RGB component keys
        r = color_dict.get("Red Component", 0.0)
        g = color_dict.get("Green Component", 0.0)
        b = color_dict.get("Blue Component", 0.0)
        return float_tuple_to_color((r, g, b))

    @classmethod
    def _export_color(cls, color: Color) -> dict:
        """Export a Color to iTerm2 color dictionary format."""
        r, g, b = color_to_float_tuple(color)
        return {
            "Color Space": "sRGB",
            "Red Component": r,
            "Green Component": g,
            "Blue Component": b,
        }

    @classmethod
    def _parse_color_scheme(cls, profile: dict) -> ColorScheme:
        """Parse color settings from an iTerm2 profile."""
        scheme = ColorScheme()
        for iterm_key, ctec_key in cls.COLOR_KEY_MAP.items():
            if iterm_key in profile:
                color = cls._parse_iterm_color(profile[iterm_key])
                setattr(scheme, ctec_key, color)
        return scheme

    @classmethod
    def _parse_profile(cls, profile_data: dict, ctec: CTEC) -> Profile:
        """Parse an iTerm2 profile into a CTEC Profile."""
        name = profile_data.get("Name", "Default")
        profile = Profile(name=name)

        # Parse color scheme
        profile.color_scheme = cls._parse_color_scheme(profile_data)

        # Parse font configuration
        if "Normal Font" in profile_data:
            font_str = profile_data["Normal Font"]
            # iTerm2 font format: "FontName Size"
            parts = font_str.rsplit(" ", 1)
            if len(parts) == 2:
                profile.font = FontConfig(
                    family=parts[0],
                    size=float(parts[1]) if parts[1].replace(".", "").isdigit() else None,
                )
            else:
                profile.font = FontConfig(family=font_str)

        # Parse cursor configuration
        cursor_config = CursorConfig()
        if "Cursor Type" in profile_data:
            cursor_type = profile_data["Cursor Type"]
            cursor_config.style = cls.CURSOR_STYLE_MAP.get(cursor_type, CursorStyle.BLOCK)
        if "Blinking Cursor" in profile_data:
            cursor_config.blink = profile_data["Blinking Cursor"]
        profile.cursor = cursor_config

        # Parse behavior configuration
        behavior = BehaviorConfig()
        if "Command" in profile_data:
            behavior.shell = profile_data["Command"]
        if "Working Directory" in profile_data:
            behavior.working_directory = profile_data["Working Directory"]
        if "Scrollback Lines" in profile_data:
            behavior.scrollback_lines = profile_data["Scrollback Lines"]
        if "Silence Bell" in profile_data:
            if profile_data["Silence Bell"]:
                behavior.bell_mode = BellMode.NONE
            elif profile_data.get("Visual Bell", False):
                behavior.bell_mode = BellMode.VISUAL
            else:
                behavior.bell_mode = BellMode.AUDIBLE
        profile.behavior = behavior

        # Store iTerm2-specific settings
        specific_keys = [
            "Unlimited Scrollback",
            "Use Bold Font",
            "Use Italic Font",
            "ASCII Anti Aliased",
            "Non-ASCII Anti Aliased",
            "Ambiguous Double Width",
            "Horizontal Spacing",
            "Vertical Spacing",
            "Use Non-ASCII Font",
            "Minimum Contrast",
            "Draw Powerline Glyphs",
        ]
        for key in specific_keys:
            if key in profile_data:
                ctec.add_terminal_specific("iterm2", f"profile.{name}.{key}", profile_data[key])

        return profile

    @classmethod
    def parse(
        cls,
        source: Union[str, Path],
        *,
        content: Optional[str] = None,
    ) -> CTEC:
        """
        Parse an iTerm2 configuration file.

        Supports both full plist configs and .itermcolors files.
        """
        ctec = CTEC(source_terminal="iterm2")

        if content is not None:
            data = plistlib.loads(content.encode())
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")
            with open(path, "rb") as f:
                data = plistlib.load(f)

        # Check if this is a color scheme file (.itermcolors)
        if "Ansi 0 Color" in data or "Foreground Color" in data:
            # This is a color scheme file
            ctec.color_scheme = cls._parse_color_scheme(data)
            return ctec

        # Full iTerm2 config
        if "New Bookmarks" in data:
            # Parse profiles
            for i, profile_data in enumerate(data["New Bookmarks"]):
                profile = cls._parse_profile(profile_data, ctec)
                if i == 0 or profile_data.get("Default Bookmark", "No") == "Yes":
                    profile.is_default = True
                ctec.profiles.append(profile)

            # Set global settings from default profile if available
            if ctec.profiles:
                default_profile = next(
                    (p for p in ctec.profiles if p.is_default), ctec.profiles[0]
                )
                ctec.color_scheme = default_profile.color_scheme
                ctec.font = default_profile.font
                ctec.cursor = default_profile.cursor
                ctec.behavior = default_profile.behavior

        # Parse window configuration
        window = WindowConfig()
        if "Default Bookmark Window Width" in data:
            window.columns = data["Default Bookmark Window Width"]
        if "Default Bookmark Window Height" in data:
            window.rows = data["Default Bookmark Window Height"]
        if window.columns or window.rows:
            ctec.window = window

        # Parse global settings
        global_specific_keys = [
            "TabStyleWithAutomaticOption",
            "HideTab",
            "HideMenuBarInFullscreen",
            "SplitPaneDimmingAmount",
            "UseBorder",
            "HideScrollbar",
            "PromptOnQuit",
            "OnlyWhenMoreTabs",
        ]
        for key in global_specific_keys:
            if key in data:
                ctec.add_terminal_specific("iterm2", key, data[key])

        return ctec

    @classmethod
    def _export_profile(cls, profile: Profile, ctec: CTEC) -> dict:
        """Export a CTEC Profile to iTerm2 profile format."""
        result = {"Name": profile.name, "Guid": profile.name.lower().replace(" ", "-")}

        # Export colors
        color_scheme = profile.color_scheme or ctec.color_scheme
        if color_scheme:
            for ctec_key, iterm_key in cls.COLOR_KEY_REVERSE_MAP.items():
                color = getattr(color_scheme, ctec_key, None)
                if color:
                    result[iterm_key] = cls._export_color(color)

        # Export font
        font = profile.font or ctec.font
        if font and font.family:
            size = font.size or 12
            result["Normal Font"] = f"{font.family} {size}"

        # Export cursor
        cursor = profile.cursor or ctec.cursor
        if cursor:
            if cursor.style:
                result["Cursor Type"] = cls.CURSOR_STYLE_REVERSE_MAP.get(cursor.style, 1)
            if cursor.blink is not None:
                result["Blinking Cursor"] = cursor.blink

        # Export behavior
        behavior = profile.behavior or ctec.behavior
        if behavior:
            if behavior.shell:
                result["Command"] = behavior.shell
                result["Custom Command"] = "Yes"
            if behavior.working_directory:
                result["Working Directory"] = behavior.working_directory
                result["Custom Directory"] = "Yes"
            if behavior.scrollback_lines is not None:
                result["Scrollback Lines"] = behavior.scrollback_lines
            if behavior.bell_mode is not None:
                result["Silence Bell"] = behavior.bell_mode == BellMode.NONE
                result["Visual Bell"] = behavior.bell_mode == BellMode.VISUAL

        # Restore terminal-specific settings
        for setting in ctec.get_terminal_specific("iterm2"):
            if setting.key.startswith(f"profile.{profile.name}."):
                actual_key = setting.key.split(".", 2)[2]
                result[actual_key] = setting.value

        return result

    @classmethod
    def export(cls, ctec: CTEC) -> str:
        """
        Export CTEC to iTerm2 plist format.

        Returns a plist XML string that can be saved to a file.
        """
        result = {}

        # Export profiles
        profiles = []
        if ctec.profiles:
            for profile in ctec.profiles:
                profiles.append(cls._export_profile(profile, ctec))
        else:
            # Create a default profile from global settings
            default_profile = Profile(
                name="Default",
                color_scheme=ctec.color_scheme,
                font=ctec.font,
                cursor=ctec.cursor,
                behavior=ctec.behavior,
                is_default=True,
            )
            profiles.append(cls._export_profile(default_profile, ctec))

        result["New Bookmarks"] = profiles

        # Export window configuration
        if ctec.window:
            if ctec.window.columns:
                result["Default Bookmark Window Width"] = ctec.window.columns
            if ctec.window.rows:
                result["Default Bookmark Window Height"] = ctec.window.rows

        # Restore terminal-specific global settings
        for setting in ctec.get_terminal_specific("iterm2"):
            if not setting.key.startswith("profile."):
                result[setting.key] = setting.value

        return plistlib.dumps(result).decode()

    @classmethod
    def export_color_scheme(cls, color_scheme: ColorScheme) -> str:
        """
        Export a ColorScheme to .itermcolors format.

        Args:
            color_scheme: Color scheme to export

        Returns:
            Plist XML string for .itermcolors file
        """
        result = {}
        for ctec_key, iterm_key in cls.COLOR_KEY_REVERSE_MAP.items():
            color = getattr(color_scheme, ctec_key, None)
            if color:
                result[iterm_key] = cls._export_color(color)
        return plistlib.dumps(result).decode()
