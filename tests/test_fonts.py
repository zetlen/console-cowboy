"""Tests for font name conversion utilities."""

import pytest

from console_cowboy.utils.fonts import (
    is_postscript_name,
    postscript_to_friendly,
    friendly_to_postscript,
)


class TestPostScriptToFriendly:
    """Tests for PostScript to friendly name conversion."""

    def test_jetbrains_mono(self):
        """Test JetBrainsMono conversion - removes -Regular suffix and adds spaces."""
        result = postscript_to_friendly("JetBrainsMono-Regular")
        assert "-Regular" not in result
        assert " " in result  # Has spaces (friendly format)
        assert "Mono" in result

    def test_fira_code(self):
        """Test FiraCode conversion."""
        assert postscript_to_friendly("FiraCode-Retina") == "Fira Code"

    def test_sf_mono(self):
        """Test SFMono conversion."""
        assert postscript_to_friendly("SFMono-Regular") == "SF Mono"

    def test_menlo(self):
        """Test Menlo conversion."""
        assert postscript_to_friendly("Menlo-Regular") == "Menlo"

    def test_monaco(self):
        """Test Monaco conversion (no suffix)."""
        assert postscript_to_friendly("Monaco") == "Monaco"

    def test_nerd_font(self):
        """Test Nerd Font suffix preservation."""
        result = postscript_to_friendly("JetBrainsMono-NF-Regular")
        assert "-Regular" not in result
        assert "NF" in result
        assert "Mono" in result

    def test_meslo(self):
        """Test MesloLGS conversion."""
        result = postscript_to_friendly("MesloLGS-NF-Regular")
        assert "Meslo" in result

    def test_bold_suffix(self):
        """Test Bold suffix removal."""
        result = postscript_to_friendly("JetBrainsMono-Bold")
        assert "-Bold" not in result
        assert "Mono" in result

    def test_italic_suffix(self):
        """Test Italic suffix removal."""
        result = postscript_to_friendly("JetBrainsMono-Italic")
        assert "-Italic" not in result
        assert "Mono" in result

    def test_empty_string(self):
        """Test empty string handling."""
        assert postscript_to_friendly("") == ""

    def test_none_handling(self):
        """Test None-like handling."""
        assert postscript_to_friendly(None) is None


class TestFriendlyToPostScript:
    """Tests for friendly to PostScript name conversion."""

    def test_jetbrains_mono(self):
        """Test JetBrains Mono conversion."""
        assert friendly_to_postscript("JetBrains Mono") == "JetBrainsMono-Regular"

    def test_fira_code(self):
        """Test Fira Code conversion."""
        assert friendly_to_postscript("Fira Code") == "FiraCode-Regular"

    def test_with_bold_weight(self):
        """Test with Bold weight."""
        assert friendly_to_postscript("JetBrains Mono", "Bold") == "JetBrainsMono-Bold"

    def test_empty_string(self):
        """Test empty string handling."""
        assert friendly_to_postscript("") == ""


class TestIsPostScriptName:
    """Tests for PostScript name detection."""

    def test_with_regular_suffix(self):
        """Test detection with -Regular suffix."""
        assert is_postscript_name("JetBrainsMono-Regular") is True

    def test_with_bold_suffix(self):
        """Test detection with -Bold suffix."""
        assert is_postscript_name("FiraCode-Bold") is True

    def test_with_camel_case(self):
        """Test detection with camelCase."""
        assert is_postscript_name("JetBrainsMono") is True

    def test_friendly_name(self):
        """Test friendly name is not detected as PostScript."""
        assert is_postscript_name("JetBrains Mono") is False

    def test_simple_name(self):
        """Test simple name without spaces."""
        assert is_postscript_name("Monaco") is False

    def test_empty_string(self):
        """Test empty string returns False."""
        assert is_postscript_name("") is False

    def test_none(self):
        """Test None returns False."""
        assert is_postscript_name(None) is False
