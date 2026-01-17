"""
Base classes for terminal emulator adapters.

Each terminal emulator adapter inherits from TerminalAdapter and implements
methods to parse (import) and export configurations to/from CTEC format.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import re
import sys

from console_cowboy.ctec.schema import CTEC


class TerminalAdapter(ABC):
    """
    Abstract base class for terminal emulator configuration adapters.

    Each terminal emulator implementation should inherit from this class
    and provide methods to:
    - Parse the terminal's native config format into CTEC
    - Export CTEC to the terminal's native config format
    """

    # Terminal identifier (lowercase, e.g., 'iterm2', 'ghostty')
    name: str = ""

    # Human-readable terminal name
    display_name: str = ""

    # Description of the terminal
    description: str = ""

    # File extensions for config files
    config_extensions: list[str] = []

    # Default config file paths (relative to home directory)
    default_config_paths: list[str] = []

    @classmethod
    @abstractmethod
    def parse(
        cls,
        source: str | Path,
        *,
        content: str | None = None,
    ) -> CTEC:
        """
        Parse a terminal configuration file into CTEC format.

        Args:
            source: Path to the configuration file, or identifier for content
            content: Optional string content (if provided, source is used as identifier)

        Returns:
            CTEC configuration

        Raises:
            FileNotFoundError: If the source file doesn't exist
            ValueError: If the configuration cannot be parsed
        """
        pass

    @classmethod
    @abstractmethod
    def export(cls, ctec: CTEC) -> str:
        """
        Export CTEC configuration to the terminal's native format.

        Args:
            ctec: CTEC configuration to export

        Returns:
            String in the terminal's native configuration format
        """
        pass

    @classmethod
    def get_default_config_path(cls) -> Path | None:
        """
        Get the default configuration file path for this terminal.

        Returns:
            Path to the default config file, or None if not found
        """
        home = Path.home()
        for path in cls.default_config_paths:
            full_path = home / path
            if full_path.exists():
                return full_path
        return None

    @classmethod
    def write_config(cls, ctec: CTEC, path: str | Path) -> None:
        """
        Export and write CTEC configuration to a file.

        Args:
            ctec: CTEC configuration to export
            path: Path to write the configuration to
        """
        content = cls.export(ctec)
        Path(path).write_text(content)


class TerminalRegistry:
    """
    Registry of available terminal adapters.
    """

    _adapters: dict[str, type[TerminalAdapter]] = {}

    @classmethod
    def register(cls, adapter: type[TerminalAdapter]) -> None:
        """
        Register a terminal adapter.

        Args:
            adapter: Terminal adapter class to register
        """
        cls._adapters[adapter.name] = adapter

    @classmethod
    def get(cls, name: str) -> type[TerminalAdapter] | None:
        """
        Get a terminal adapter by name.

        Args:
            name: Terminal name (case-insensitive)

        Returns:
            Terminal adapter class, or None if not found
        """
        return cls._adapters.get(name.lower())

    @classmethod
    def list_terminals(cls) -> list[type[TerminalAdapter]]:
        """
        List all registered terminal adapters.

        Returns:
            List of terminal adapter classes
        """
        return list(cls._adapters.values())

    @classmethod
    def get_names(cls) -> list[str]:
        """
        Get names of all registered terminals.

        Returns:
            List of terminal names
        """
        return list(cls._adapters.keys())

    @classmethod
    def detect_terminal_type(cls, content: str, file_path: Path | None = None) -> str | None:
        """
        Detect the terminal type from file content and/or file path.

        Uses heuristics to identify the terminal configuration format:
        - Wezterm: Lua config with 'wezterm' module references
        - Alacritty: YAML/TOML with specific section names
        - Kitty: Key-value with kitty-specific keys
        - Ghostty: Key-value with ghostty-specific keys
        - VSCode: JSON with 'terminal.integrated' keys
        - iTerm2: Binary plist or XML plist with iTerm2 structures
        - Terminal.app: Binary plist with Terminal.app structures

        Args:
            content: The file content to analyze
            file_path: Optional file path for extension-based hints

        Returns:
            Terminal name if detected, None otherwise
        """
        # Check file extension first for strong hints
        if file_path:
            ext = file_path.suffix.lower()
            name = file_path.name.lower()

            # Strong extension matches
            if ext == ".lua" or name.endswith(".lua"):
                return "wezterm"
            if ext == ".itermcolors":
                return "iterm2"
            if name == "com.googlecode.iterm2.plist":
                return "iterm2"
            if name == "com.apple.terminal.plist":
                return "terminal_app"

        # Check for binary plist (starts with 'bplist')
        if content.startswith("bplist"):
            # Binary plist - need to check filename for type
            if file_path:
                name = file_path.name.lower()
                if "iterm2" in name:
                    return "iterm2"
                if "terminal" in name:
                    return "terminal_app"
            # Default to iterm2 for plist on macOS
            if sys.platform == "darwin":
                return "iterm2"
            return None

        # Wezterm detection: Lua with wezterm module
        if re.search(r'local\s+wezterm\s*=\s*require', content) or \
           re.search(r'wezterm\.(font|action|color)', content) or \
           re.search(r'config\.\w+\s*=', content) and 'return config' in content:
            return "wezterm"

        # VSCode detection: JSON with terminal.integrated keys
        if '"terminal.integrated' in content or '"workbench.colorCustomizations"' in content:
            return "vscode"

        # Alacritty detection: YAML/TOML with alacritty sections
        # TOML format
        if re.search(r'^\[colors\.(primary|normal|bright)\]', content, re.MULTILINE) or \
           re.search(r'^\[(font|window|scrolling|cursor)\]', content, re.MULTILINE):
            return "alacritty"
        # YAML format
        if re.search(r'^colors:\s*$', content, re.MULTILINE) and \
           (re.search(r'^\s+primary:', content, re.MULTILINE) or
            re.search(r'^\s+normal:', content, re.MULTILINE)):
            return "alacritty"

        # Ghostty detection: key=value with ghostty-specific keys
        ghostty_keys = [
            r'^palette\s*=',
            r'^quick-terminal-',
            r'^cursor-color\s*=',
            r'^selection-foreground\s*=',
            r'^selection-background\s*=',
            r'^font-family\s*=',
            r'^window-padding-',
        ]
        for pattern in ghostty_keys:
            if re.search(pattern, content, re.MULTILINE):
                return "ghostty"

        # Kitty detection: key-value with kitty-specific keys
        kitty_keys = [
            r'^font_family\s+',
            r'^cursor_shape\s+',
            r'^scrollback_lines\s+',
            r'^enable_audio_bell\s+',
            r'^window_padding_width\s+',
            r'^color\d+\s+',
            r'^cursor_text_color\s+',
            r'^selection_foreground\s+',
            r'^selection_background\s+',
        ]
        for pattern in kitty_keys:
            if re.search(pattern, content, re.MULTILINE):
                return "kitty"

        # Check for common key=value patterns that might be ghostty or kitty
        # Ghostty uses key = value (with spaces around =)
        # Kitty uses key value (space separated)
        if re.search(r'^foreground\s*=\s*#', content, re.MULTILINE):
            return "ghostty"
        if re.search(r'^foreground\s+#', content, re.MULTILINE):
            return "kitty"

        return None

    @classmethod
    def get_default_config_path_for_terminal(cls, terminal_name: str) -> Path | None:
        """
        Get the default configuration file path for a terminal.

        This returns the first existing config path, or the first default
        path if none exist (for write operations).

        Args:
            terminal_name: Name of the terminal

        Returns:
            Path to config file, or None if terminal not found
        """
        adapter = cls.get(terminal_name)
        if not adapter:
            return None

        # First try to find an existing config
        existing = adapter.get_default_config_path()
        if existing:
            return existing

        # Return the first default path (for write operations)
        if adapter.default_config_paths:
            return Path.home() / adapter.default_config_paths[0]

        return None
