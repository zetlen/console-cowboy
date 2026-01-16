"""Tests for terminal emulator adapters."""

from pathlib import Path

import pytest

from console_cowboy.ctec.schema import (
    CTEC,
    BellMode,
    Color,
    ColorScheme,
    CursorConfig,
    CursorStyle,
    FontConfig,
    WindowConfig,
)
from console_cowboy.terminals import (
    AlacrittyAdapter,
    GhosttyAdapter,
    ITerm2Adapter,
    KittyAdapter,
    TerminalRegistry,
    WeztermAdapter,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestTerminalRegistry:
    """Tests for the terminal registry."""

    def test_get_all_terminals(self):
        names = TerminalRegistry.get_names()
        assert "iterm2" in names
        assert "ghostty" in names
        assert "alacritty" in names
        assert "kitty" in names
        assert "wezterm" in names

    def test_get_terminal_by_name(self):
        adapter = TerminalRegistry.get("ghostty")
        assert adapter == GhosttyAdapter

    def test_get_terminal_case_insensitive(self):
        adapter = TerminalRegistry.get("GHOSTTY")
        assert adapter == GhosttyAdapter

    def test_get_unknown_terminal(self):
        adapter = TerminalRegistry.get("unknown")
        assert adapter is None

    def test_list_terminals(self):
        terminals = TerminalRegistry.list_terminals()
        assert len(terminals) == 5
        assert ITerm2Adapter in terminals


class TestGhosttyAdapter:
    """Tests for the Ghostty adapter."""

    def test_adapter_metadata(self):
        assert GhosttyAdapter.name == "ghostty"
        assert GhosttyAdapter.display_name == "Ghostty"
        assert ".config/ghostty/config" in GhosttyAdapter.default_config_paths

    def test_parse_fixture(self):
        config_path = FIXTURES_DIR / "ghostty" / "config"
        ctec = GhosttyAdapter.parse(config_path)

        assert ctec.source_terminal == "ghostty"
        assert ctec.font.family == "JetBrains Mono"
        assert ctec.font.size == 14.0
        assert ctec.cursor.style == CursorStyle.BLOCK
        assert ctec.cursor.blink is True
        assert ctec.window.columns == 120
        assert ctec.window.rows == 40
        assert ctec.window.opacity == 0.95

    def test_parse_colors(self):
        config_path = FIXTURES_DIR / "ghostty" / "config"
        ctec = GhosttyAdapter.parse(config_path)

        assert ctec.color_scheme is not None
        # Check foreground (#c5c8c6)
        assert ctec.color_scheme.foreground.r == 197
        assert ctec.color_scheme.foreground.g == 200
        assert ctec.color_scheme.foreground.b == 198
        # Check background (#1d1f21)
        assert ctec.color_scheme.background.r == 29

    def test_parse_from_content(self):
        content = """
font-family = Test Font
font-size = 16
cursor-style = bar
"""
        ctec = GhosttyAdapter.parse("test", content=content)
        assert ctec.font.family == "Test Font"
        assert ctec.font.size == 16.0
        assert ctec.cursor.style == CursorStyle.BEAM

    def test_export(self):
        ctec = CTEC(
            font=FontConfig(family="Fira Code", size=12.0),
            cursor=CursorConfig(style=CursorStyle.UNDERLINE, blink=False),
        )
        output = GhosttyAdapter.export(ctec)

        assert "font-family = Fira Code" in output
        assert "font-size = 12.0" in output
        assert "cursor-style = underline" in output
        assert "cursor-style-blink = false" in output

    def test_export_colors(self):
        ctec = CTEC(
            color_scheme=ColorScheme(
                foreground=Color(255, 255, 255),
                background=Color(0, 0, 0),
                red=Color(204, 0, 0),
            )
        )
        output = GhosttyAdapter.export(ctec)

        assert "foreground = #ffffff" in output
        assert "background = #000000" in output
        assert "palette = 1=#cc0000" in output

    def test_roundtrip(self):
        config_path = FIXTURES_DIR / "ghostty" / "config"
        original = GhosttyAdapter.parse(config_path)

        # Export and re-parse
        exported = GhosttyAdapter.export(original)
        restored = GhosttyAdapter.parse("test", content=exported)

        assert restored.font.family == original.font.family
        assert restored.font.size == original.font.size
        assert restored.cursor.style == original.cursor.style


class TestAlacrittyAdapter:
    """Tests for the Alacritty adapter."""

    def test_adapter_metadata(self):
        assert AlacrittyAdapter.name == "alacritty"
        assert ".toml" in AlacrittyAdapter.config_extensions

    def test_parse_toml_fixture(self):
        config_path = FIXTURES_DIR / "alacritty" / "alacritty.toml"
        ctec = AlacrittyAdapter.parse(config_path)

        assert ctec.source_terminal == "alacritty"
        assert ctec.font.family == "JetBrains Mono"
        assert ctec.font.size == 14.0
        assert ctec.cursor.style == CursorStyle.BLOCK
        assert ctec.window.columns == 120
        assert ctec.window.rows == 40

    def test_parse_yaml_fixture(self):
        config_path = FIXTURES_DIR / "alacritty" / "alacritty.yml"
        ctec = AlacrittyAdapter.parse(config_path)

        assert ctec.source_terminal == "alacritty"
        assert ctec.font.family == "JetBrains Mono"

    def test_parse_colors(self):
        config_path = FIXTURES_DIR / "alacritty" / "alacritty.toml"
        ctec = AlacrittyAdapter.parse(config_path)

        assert ctec.color_scheme is not None
        assert ctec.color_scheme.foreground is not None
        assert ctec.color_scheme.background is not None

    def test_export_toml(self):
        ctec = CTEC(
            font=FontConfig(family="Monaco", size=13.0),
            window=WindowConfig(columns=100, rows=30),
        )
        output = AlacrittyAdapter.export(ctec, use_toml=True)

        assert "Monaco" in output
        assert "columns = 100" in output

    def test_export_yaml(self):
        ctec = CTEC(
            font=FontConfig(family="Monaco", size=13.0),
        )
        output = AlacrittyAdapter.export(ctec, use_toml=False)

        assert "Monaco" in output
        assert ":" in output  # YAML uses colons

    def test_key_bindings(self):
        config_path = FIXTURES_DIR / "alacritty" / "alacritty.toml"
        ctec = AlacrittyAdapter.parse(config_path)

        assert len(ctec.key_bindings) > 0
        # Check for Copy binding
        copy_binding = next(
            (kb for kb in ctec.key_bindings if kb.action == "Copy"), None
        )
        assert copy_binding is not None


class TestKittyAdapter:
    """Tests for the Kitty adapter."""

    def test_adapter_metadata(self):
        assert KittyAdapter.name == "kitty"
        assert ".conf" in KittyAdapter.config_extensions

    def test_parse_fixture(self):
        config_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(config_path)

        assert ctec.source_terminal == "kitty"
        assert ctec.font.family == "JetBrains Mono"
        assert ctec.font.size == 14.0
        assert ctec.cursor.style == CursorStyle.BLOCK
        assert ctec.window.columns == 120
        assert ctec.window.rows == 40

    def test_parse_colors(self):
        config_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(config_path)

        assert ctec.color_scheme is not None
        # Check foreground (#c5c8c6)
        assert ctec.color_scheme.foreground.r == 197

    def test_parse_behavior(self):
        config_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(config_path)

        assert ctec.behavior is not None
        assert ctec.behavior.shell == "/bin/zsh"
        assert ctec.behavior.bell_mode == BellMode.VISUAL
        # Scrollback is now in ctec.scroll, not behavior
        assert ctec.scroll is not None
        assert ctec.scroll.lines == 10000

    def test_export(self):
        ctec = CTEC(
            font=FontConfig(family="Fira Code", size=12.0),
            cursor=CursorConfig(style=CursorStyle.BEAM, blink=True),
        )
        output = KittyAdapter.export(ctec)

        assert "font_family Fira Code" in output
        assert "font_size 12.0" in output
        assert "cursor_shape beam" in output

    def test_key_bindings(self):
        config_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(config_path)

        assert len(ctec.key_bindings) > 0

    def test_terminal_specific_settings(self):
        config_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(config_path)

        kitty_specific = ctec.get_terminal_specific("kitty")
        assert len(kitty_specific) > 0


class TestWeztermAdapter:
    """Tests for the Wezterm adapter."""

    def test_adapter_metadata(self):
        assert WeztermAdapter.name == "wezterm"
        assert ".lua" in WeztermAdapter.config_extensions

    def test_parse_fixture(self):
        config_path = FIXTURES_DIR / "wezterm" / "wezterm.lua"
        ctec = WeztermAdapter.parse(config_path)

        assert ctec.source_terminal == "wezterm"
        assert ctec.font.family == "JetBrains Mono"
        assert ctec.font.size == 14.0
        assert ctec.window.columns == 120
        assert ctec.window.rows == 40

    def test_parse_colors(self):
        config_path = FIXTURES_DIR / "wezterm" / "wezterm.lua"
        ctec = WeztermAdapter.parse(config_path)

        assert ctec.color_scheme is not None
        # Wezterm parsing may have warnings about Lua complexity
        assert len(ctec.warnings) > 0  # Expected warning about Lua

    def test_parse_cursor(self):
        config_path = FIXTURES_DIR / "wezterm" / "wezterm.lua"
        ctec = WeztermAdapter.parse(config_path)

        assert ctec.cursor is not None
        assert ctec.cursor.style == CursorStyle.BLOCK
        assert ctec.cursor.blink is True

    def test_export(self):
        ctec = CTEC(
            font=FontConfig(family="Fira Code", size=12.0),
            cursor=CursorConfig(style=CursorStyle.BEAM, blink=False),
        )
        output = WeztermAdapter.export(ctec)

        assert 'wezterm.font("Fira Code")' in output
        assert "font_size = 12.0" in output
        assert "SteadyBar" in output

    def test_export_colors(self):
        ctec = CTEC(
            color_scheme=ColorScheme(
                foreground=Color(255, 255, 255),
                background=Color(0, 0, 0),
            )
        )
        output = WeztermAdapter.export(ctec)

        assert 'foreground = "#ffffff"' in output
        assert 'background = "#000000"' in output

    def test_export_valid_lua(self):
        """Verify the exported Lua is syntactically valid."""
        ctec = CTEC(
            font=FontConfig(family="Test", size=12.0),
            window=WindowConfig(columns=80, rows=24),
        )
        output = WeztermAdapter.export(ctec)

        # Should have required Lua structure
        assert "local wezterm = require 'wezterm'" in output
        assert "local config = wezterm.config_builder()" in output
        assert "return config" in output


class TestITerm2Adapter:
    """Tests for the iTerm2 adapter."""

    def test_adapter_metadata(self):
        assert ITerm2Adapter.name == "iterm2"
        assert ".plist" in ITerm2Adapter.config_extensions

    def test_parse_fixture(self):
        config_path = FIXTURES_DIR / "iterm2" / "com.googlecode.iterm2.plist"
        ctec = ITerm2Adapter.parse(config_path)

        assert ctec.source_terminal == "iterm2"
        assert ctec.window.columns == 120
        assert ctec.window.rows == 40

    def test_parse_default_profile(self):
        """Test that the default profile settings are imported correctly."""
        config_path = FIXTURES_DIR / "iterm2" / "com.googlecode.iterm2.plist"
        ctec = ITerm2Adapter.parse(config_path)

        # Settings from the default profile should be at the CTEC level
        assert ctec.color_scheme is not None
        assert ctec.font is not None or ctec.cursor is not None

    def test_parse_colors(self):
        config_path = FIXTURES_DIR / "iterm2" / "com.googlecode.iterm2.plist"
        ctec = ITerm2Adapter.parse(config_path)

        assert ctec.color_scheme is not None
        assert ctec.color_scheme.foreground is not None

    def test_export(self):
        ctec = CTEC(
            font=FontConfig(family="Monaco", size=12.0),
            cursor=CursorConfig(style=CursorStyle.BLOCK, blink=True),
            color_scheme=ColorScheme(
                foreground=Color(255, 255, 255),
                background=Color(0, 0, 0),
            ),
        )
        output = ITerm2Adapter.export(ctec)

        # Should be valid plist XML
        assert '<?xml version="1.0"' in output
        assert "<plist" in output
        assert "Monaco" in output

    def test_terminal_specific_settings(self):
        config_path = FIXTURES_DIR / "iterm2" / "com.googlecode.iterm2.plist"
        ctec = ITerm2Adapter.parse(config_path)

        iterm_specific = ctec.get_terminal_specific("iterm2")
        assert len(iterm_specific) > 0


class TestCrossTerminalConversion:
    """Tests for converting between different terminals."""

    def test_ghostty_to_alacritty(self):
        # Parse Ghostty config
        ghostty_path = FIXTURES_DIR / "ghostty" / "config"
        ctec = GhosttyAdapter.parse(ghostty_path)

        # Export to Alacritty
        alacritty_output = AlacrittyAdapter.export(ctec)

        # Re-parse as Alacritty
        alacritty_ctec = AlacrittyAdapter.parse("test.toml", content=alacritty_output)

        # Core settings should be preserved
        assert alacritty_ctec.font.family == ctec.font.family
        assert alacritty_ctec.font.size == ctec.font.size

    def test_kitty_to_ghostty(self):
        # Parse Kitty config
        kitty_path = FIXTURES_DIR / "kitty" / "kitty.conf"
        ctec = KittyAdapter.parse(kitty_path)

        # Export to Ghostty
        ghostty_output = GhosttyAdapter.export(ctec)

        # Re-parse as Ghostty
        ghostty_ctec = GhosttyAdapter.parse("test", content=ghostty_output)

        # Core settings should be preserved
        assert ghostty_ctec.font.family == ctec.font.family
        assert ghostty_ctec.font.size == ctec.font.size

    def test_alacritty_to_kitty(self):
        # Parse Alacritty config
        alacritty_path = FIXTURES_DIR / "alacritty" / "alacritty.toml"
        ctec = AlacrittyAdapter.parse(alacritty_path)

        # Export to Kitty
        kitty_output = KittyAdapter.export(ctec)

        # Re-parse as Kitty
        kitty_ctec = KittyAdapter.parse("test.conf", content=kitty_output)

        # Core settings should be preserved
        assert kitty_ctec.font.family == ctec.font.family

    def test_color_preservation_across_terminals(self):
        """Test that colors are preserved when converting between terminals."""
        # Start with a known color scheme
        original = CTEC(
            color_scheme=ColorScheme(
                foreground=Color(197, 200, 198),
                background=Color(29, 31, 33),
                red=Color(204, 102, 102),
            )
        )

        # Convert through all terminals
        ghostty_output = GhosttyAdapter.export(original)
        ghostty_ctec = GhosttyAdapter.parse("test", content=ghostty_output)

        # Colors should be preserved
        assert ghostty_ctec.color_scheme.foreground.r == 197
        assert ghostty_ctec.color_scheme.foreground.g == 200
        assert ghostty_ctec.color_scheme.foreground.b == 198
