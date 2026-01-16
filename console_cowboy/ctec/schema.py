"""
CTEC Schema - Data model for Common Terminal Emulator Configuration.

This module defines the portable configuration format that serves as an
intermediate representation for terminal emulator settings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CursorStyle(Enum):
    """Cursor appearance styles supported by most terminal emulators."""

    BLOCK = "block"
    BEAM = "beam"
    UNDERLINE = "underline"


class BellMode(Enum):
    """Bell notification modes."""

    NONE = "none"
    AUDIBLE = "audible"
    VISUAL = "visual"


@dataclass
class Color:
    """
    Represents an RGB color.

    Attributes:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
    """

    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        for component, name in [(self.r, "r"), (self.g, "g"), (self.b, "b")]:
            if not 0 <= component <= 255:
                raise ValueError(f"Color component {name} must be 0-255, got {component}")

    def to_hex(self) -> str:
        """Convert to hex color string (e.g., '#ff0000')."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create a Color from a hex string (e.g., '#ff0000' or 'ff0000')."""
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)
        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex color: {hex_str}")
        return cls(
            r=int(hex_str[0:2], 16),
            g=int(hex_str[2:4], 16),
            b=int(hex_str[4:6], 16),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {"r": self.r, "g": self.g, "b": self.b}

    @classmethod
    def from_dict(cls, data: dict) -> "Color":
        """Create a Color from a dictionary."""
        return cls(r=data["r"], g=data["g"], b=data["b"])


@dataclass
class ColorScheme:
    """
    Terminal color scheme with ANSI colors and semantic colors.

    Attributes:
        name: Optional name for the color scheme
        foreground: Default text color
        background: Default background color
        cursor: Cursor color
        cursor_text: Text color when under cursor
        selection: Selection highlight color
        selection_text: Selected text color
        black: ANSI color 0 (normal)
        red: ANSI color 1 (normal)
        green: ANSI color 2 (normal)
        yellow: ANSI color 3 (normal)
        blue: ANSI color 4 (normal)
        magenta: ANSI color 5 (normal)
        cyan: ANSI color 6 (normal)
        white: ANSI color 7 (normal)
        bright_black: ANSI color 8 (bright)
        bright_red: ANSI color 9 (bright)
        bright_green: ANSI color 10 (bright)
        bright_yellow: ANSI color 11 (bright)
        bright_blue: ANSI color 12 (bright)
        bright_magenta: ANSI color 13 (bright)
        bright_cyan: ANSI color 14 (bright)
        bright_white: ANSI color 15 (bright)
    """

    name: Optional[str] = None
    foreground: Optional[Color] = None
    background: Optional[Color] = None
    cursor: Optional[Color] = None
    cursor_text: Optional[Color] = None
    selection: Optional[Color] = None
    selection_text: Optional[Color] = None
    # Normal colors (0-7)
    black: Optional[Color] = None
    red: Optional[Color] = None
    green: Optional[Color] = None
    yellow: Optional[Color] = None
    blue: Optional[Color] = None
    magenta: Optional[Color] = None
    cyan: Optional[Color] = None
    white: Optional[Color] = None
    # Bright colors (8-15)
    bright_black: Optional[Color] = None
    bright_red: Optional[Color] = None
    bright_green: Optional[Color] = None
    bright_yellow: Optional[Color] = None
    bright_blue: Optional[Color] = None
    bright_magenta: Optional[Color] = None
    bright_cyan: Optional[Color] = None
    bright_white: Optional[Color] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        if self.name is not None:
            result["name"] = self.name
        color_fields = [
            "foreground",
            "background",
            "cursor",
            "cursor_text",
            "selection",
            "selection_text",
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_black",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
        ]
        for field_name in color_fields:
            color = getattr(self, field_name)
            if color is not None:
                result[field_name] = color.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ColorScheme":
        """Create a ColorScheme from a dictionary."""
        kwargs = {}
        if "name" in data:
            kwargs["name"] = data["name"]
        color_fields = [
            "foreground",
            "background",
            "cursor",
            "cursor_text",
            "selection",
            "selection_text",
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_black",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
        ]
        for field_name in color_fields:
            if field_name in data:
                kwargs[field_name] = Color.from_dict(data[field_name])
        return cls(**kwargs)


@dataclass
class FontConfig:
    """
    Font configuration for the terminal.

    Attributes:
        family: Font family name (e.g., 'JetBrains Mono', 'Fira Code')
        size: Font size in points
        line_height: Line height multiplier (1.0 = normal)
        bold_font: Optional separate font family for bold text
        italic_font: Optional separate font family for italic text
        ligatures: Whether to enable font ligatures
    """

    family: Optional[str] = None
    size: Optional[float] = None
    line_height: Optional[float] = None
    bold_font: Optional[str] = None
    italic_font: Optional[str] = None
    ligatures: Optional[bool] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        for field_name in [
            "family",
            "size",
            "line_height",
            "bold_font",
            "italic_font",
            "ligatures",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "FontConfig":
        """Create a FontConfig from a dictionary."""
        return cls(
            family=data.get("family"),
            size=data.get("size"),
            line_height=data.get("line_height"),
            bold_font=data.get("bold_font"),
            italic_font=data.get("italic_font"),
            ligatures=data.get("ligatures"),
        )


@dataclass
class CursorConfig:
    """
    Cursor appearance and behavior configuration.

    Attributes:
        style: Cursor shape (block, beam, or underline)
        blink: Whether the cursor should blink
        blink_interval: Blink interval in milliseconds
    """

    style: Optional[CursorStyle] = None
    blink: Optional[bool] = None
    blink_interval: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        if self.style is not None:
            result["style"] = self.style.value
        if self.blink is not None:
            result["blink"] = self.blink
        if self.blink_interval is not None:
            result["blink_interval"] = self.blink_interval
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "CursorConfig":
        """Create a CursorConfig from a dictionary."""
        return cls(
            style=CursorStyle(data["style"]) if "style" in data else None,
            blink=data.get("blink"),
            blink_interval=data.get("blink_interval"),
        )


@dataclass
class WindowConfig:
    """
    Window appearance and behavior configuration.

    Attributes:
        columns: Initial number of columns
        rows: Initial number of rows
        opacity: Window opacity (0.0 = transparent, 1.0 = opaque)
        blur: Background blur radius (0 = no blur)
        padding_horizontal: Horizontal padding in pixels
        padding_vertical: Vertical padding in pixels
        decorations: Whether to show window decorations (title bar, etc.)
        startup_mode: Initial window mode ('windowed', 'maximized', 'fullscreen')
        dynamic_title: Whether to update window title from shell
    """

    columns: Optional[int] = None
    rows: Optional[int] = None
    opacity: Optional[float] = None
    blur: Optional[int] = None
    padding_horizontal: Optional[int] = None
    padding_vertical: Optional[int] = None
    decorations: Optional[bool] = None
    startup_mode: Optional[str] = None
    dynamic_title: Optional[bool] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        for field_name in [
            "columns",
            "rows",
            "opacity",
            "blur",
            "padding_horizontal",
            "padding_vertical",
            "decorations",
            "startup_mode",
            "dynamic_title",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "WindowConfig":
        """Create a WindowConfig from a dictionary."""
        return cls(
            columns=data.get("columns"),
            rows=data.get("rows"),
            opacity=data.get("opacity"),
            blur=data.get("blur"),
            padding_horizontal=data.get("padding_horizontal"),
            padding_vertical=data.get("padding_vertical"),
            decorations=data.get("decorations"),
            startup_mode=data.get("startup_mode"),
            dynamic_title=data.get("dynamic_title"),
        )


@dataclass
class BehaviorConfig:
    """
    Terminal behavior configuration.

    Attributes:
        shell: Shell command or path to execute
        working_directory: Initial working directory
        scrollback_lines: Number of lines to keep in scrollback buffer
        mouse_enabled: Whether to enable mouse support
        bell_mode: Bell notification mode
        copy_on_select: Whether to copy text to clipboard on selection
        confirm_close: Whether to confirm before closing with running processes
        close_on_exit: Action when shell exits ('close', 'hold', 'restart')
    """

    shell: Optional[str] = None
    working_directory: Optional[str] = None
    scrollback_lines: Optional[int] = None
    mouse_enabled: Optional[bool] = None
    bell_mode: Optional[BellMode] = None
    copy_on_select: Optional[bool] = None
    confirm_close: Optional[bool] = None
    close_on_exit: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        for field_name in [
            "shell",
            "working_directory",
            "scrollback_lines",
            "mouse_enabled",
            "copy_on_select",
            "confirm_close",
            "close_on_exit",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        if self.bell_mode is not None:
            result["bell_mode"] = self.bell_mode.value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "BehaviorConfig":
        """Create a BehaviorConfig from a dictionary."""
        return cls(
            shell=data.get("shell"),
            working_directory=data.get("working_directory"),
            scrollback_lines=data.get("scrollback_lines"),
            mouse_enabled=data.get("mouse_enabled"),
            bell_mode=BellMode(data["bell_mode"]) if "bell_mode" in data else None,
            copy_on_select=data.get("copy_on_select"),
            confirm_close=data.get("confirm_close"),
            close_on_exit=data.get("close_on_exit"),
        )


@dataclass
class KeyBinding:
    """
    A keyboard shortcut binding.

    Attributes:
        action: The action to perform (e.g., 'copy', 'paste', 'new_tab')
        key: The key (e.g., 'c', 'v', 'Return')
        mods: Modifier keys (e.g., ['ctrl'], ['ctrl', 'shift'])
    """

    action: str
    key: str
    mods: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {"action": self.action, "key": self.key}
        if self.mods:
            result["mods"] = self.mods
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "KeyBinding":
        """Create a KeyBinding from a dictionary."""
        return cls(
            action=data["action"],
            key=data["key"],
            mods=data.get("mods", []),
        )


@dataclass
class TerminalSpecificSetting:
    """
    A setting specific to a particular terminal emulator that cannot
    be mapped to a common CTEC setting.

    Attributes:
        terminal: Terminal emulator name (e.g., 'iterm2', 'ghostty')
        key: Configuration key path (e.g., 'Unlimited Scrollback')
        value: Configuration value (any serializable type)
    """

    terminal: str
    key: str
    value: object

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {"terminal": self.terminal, "key": self.key, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "TerminalSpecificSetting":
        """Create a TerminalSpecificSetting from a dictionary."""
        return cls(terminal=data["terminal"], key=data["key"], value=data["value"])


@dataclass
class Profile:
    """
    A terminal profile with its own set of configurations.

    Attributes:
        name: Profile name
        color_scheme: Color scheme for this profile
        font: Font configuration for this profile
        cursor: Cursor configuration for this profile
        behavior: Behavior configuration for this profile
        is_default: Whether this is the default profile
    """

    name: str
    color_scheme: Optional[ColorScheme] = None
    font: Optional[FontConfig] = None
    cursor: Optional[CursorConfig] = None
    behavior: Optional[BehaviorConfig] = None
    is_default: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {"name": self.name, "is_default": self.is_default}
        if self.color_scheme is not None:
            result["color_scheme"] = self.color_scheme.to_dict()
        if self.font is not None:
            result["font"] = self.font.to_dict()
        if self.cursor is not None:
            result["cursor"] = self.cursor.to_dict()
        if self.behavior is not None:
            result["behavior"] = self.behavior.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        """Create a Profile from a dictionary."""
        return cls(
            name=data["name"],
            color_scheme=ColorScheme.from_dict(data["color_scheme"])
            if "color_scheme" in data
            else None,
            font=FontConfig.from_dict(data["font"]) if "font" in data else None,
            cursor=CursorConfig.from_dict(data["cursor"]) if "cursor" in data else None,
            behavior=BehaviorConfig.from_dict(data["behavior"])
            if "behavior" in data
            else None,
            is_default=data.get("is_default", False),
        )


@dataclass
class CTEC:
    """
    Common Terminal Emulator Configuration.

    The main container for all portable terminal configuration settings.
    This serves as the intermediate format for converting between different
    terminal emulator configurations.

    Attributes:
        version: CTEC format version
        source_terminal: Original terminal emulator this config was exported from
        color_scheme: Global color scheme (used if no profile specified)
        font: Global font configuration
        cursor: Global cursor configuration
        window: Window configuration
        behavior: Terminal behavior configuration
        key_bindings: List of keyboard shortcuts
        profiles: List of terminal profiles
        terminal_specific: Settings that cannot be mapped to common CTEC fields
        warnings: Compatibility warnings generated during import/export
    """

    version: str = "1.0"
    source_terminal: Optional[str] = None
    color_scheme: Optional[ColorScheme] = None
    font: Optional[FontConfig] = None
    cursor: Optional[CursorConfig] = None
    window: Optional[WindowConfig] = None
    behavior: Optional[BehaviorConfig] = None
    key_bindings: list[KeyBinding] = field(default_factory=list)
    profiles: list[Profile] = field(default_factory=list)
    terminal_specific: list[TerminalSpecificSetting] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation suitable for serialization."""
        result = {"version": self.version}
        if self.source_terminal is not None:
            result["source_terminal"] = self.source_terminal
        if self.color_scheme is not None:
            result["color_scheme"] = self.color_scheme.to_dict()
        if self.font is not None:
            result["font"] = self.font.to_dict()
        if self.cursor is not None:
            result["cursor"] = self.cursor.to_dict()
        if self.window is not None:
            result["window"] = self.window.to_dict()
        if self.behavior is not None:
            result["behavior"] = self.behavior.to_dict()
        if self.key_bindings:
            result["key_bindings"] = [kb.to_dict() for kb in self.key_bindings]
        if self.profiles:
            result["profiles"] = [p.to_dict() for p in self.profiles]
        if self.terminal_specific:
            result["terminal_specific"] = [ts.to_dict() for ts in self.terminal_specific]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "CTEC":
        """Create a CTEC from a dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            source_terminal=data.get("source_terminal"),
            color_scheme=ColorScheme.from_dict(data["color_scheme"])
            if "color_scheme" in data
            else None,
            font=FontConfig.from_dict(data["font"]) if "font" in data else None,
            cursor=CursorConfig.from_dict(data["cursor"]) if "cursor" in data else None,
            window=WindowConfig.from_dict(data["window"]) if "window" in data else None,
            behavior=BehaviorConfig.from_dict(data["behavior"])
            if "behavior" in data
            else None,
            key_bindings=[KeyBinding.from_dict(kb) for kb in data.get("key_bindings", [])],
            profiles=[Profile.from_dict(p) for p in data.get("profiles", [])],
            terminal_specific=[
                TerminalSpecificSetting.from_dict(ts)
                for ts in data.get("terminal_specific", [])
            ],
            warnings=data.get("warnings", []),
        )

    def add_warning(self, warning: str) -> None:
        """Add a compatibility warning."""
        self.warnings.append(warning)

    def add_terminal_specific(
        self, terminal: str, key: str, value: object
    ) -> None:
        """Add a terminal-specific setting."""
        self.terminal_specific.append(
            TerminalSpecificSetting(terminal=terminal, key=key, value=value)
        )

    def get_terminal_specific(self, terminal: str) -> list[TerminalSpecificSetting]:
        """Get all terminal-specific settings for a given terminal."""
        return [ts for ts in self.terminal_specific if ts.terminal == terminal]
