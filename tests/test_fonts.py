"""Tests for font name conversion utilities."""

import sys
from unittest.mock import patch

from console_cowboy.utils.fonts import (
    _get_system_font_names,
    _postscript_to_friendly_heuristic,
    extract_weight_from_name,
    friendly_to_postscript,
    is_postscript_name,
    normalize_font_family,
    postscript_to_friendly,
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

    def test_abbreviated_reg_suffix(self):
        """Test -Reg abbreviated suffix removal."""
        result = postscript_to_friendly("FiraCode-Reg")
        assert "-Reg" not in result
        assert "Fira Code" == result

    def test_nfp_suffix(self):
        """Test NFP (Nerd Font Patched) suffix handling."""
        result = postscript_to_friendly("JetBrainsMonoNFP")
        assert "NFP" in result
        assert " NFP" in result  # Should have space before NFP

    def test_m_plus_code_font(self):
        """Test M+Code font with + character preserved."""
        result = postscript_to_friendly("M+CodeLat60NFP-Reg")
        assert "M+Code" in result  # + should be preserved
        assert "-Reg" not in result  # Weight suffix removed
        # NFP suffix may be expanded to "Nerd Font Propo" by system lookup
        assert "NFP" in result or "Nerd Font" in result

    def test_m_plus_code_simple(self):
        """Test simple M+Code font."""
        result = postscript_to_friendly("M+Code-Regular")
        assert "M+Code" in result
        assert "-Regular" not in result

    def test_font_with_numbers(self):
        """Test font name with version numbers like Lat60."""
        result = postscript_to_friendly("M+CodeLat60-Regular")
        assert "Lat60" in result  # Numbers should be preserved
        assert "-Regular" not in result


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

    def test_abbreviated_reg_suffix(self):
        """Test detection with -Reg abbreviated suffix."""
        assert is_postscript_name("FiraCode-Reg") is True

    def test_m_plus_code_font(self):
        """Test M+Code font detection."""
        assert is_postscript_name("M+CodeLat60NFP-Reg") is True


class TestExtractWeightFromName:
    """Tests for weight extraction from font names."""

    def test_postscript_bold(self):
        """Test PostScript format with Bold."""
        base, weight = extract_weight_from_name("JetBrainsMono-Bold")
        assert base == "JetBrainsMono"
        assert weight == "Bold"

    def test_postscript_regular(self):
        """Test PostScript format with Regular."""
        base, weight = extract_weight_from_name("FiraCode-Regular")
        assert base == "FiraCode"
        assert weight == "Regular"

    def test_friendly_bold(self):
        """Test friendly format with Bold."""
        base, weight = extract_weight_from_name("JetBrains Mono Bold")
        assert base == "JetBrains Mono"
        assert weight == "Bold"

    def test_no_weight(self):
        """Test font name without weight suffix."""
        base, weight = extract_weight_from_name("Fira Code")
        assert base == "Fira Code"
        assert weight is None

    def test_no_weight_postscript(self):
        """Test PostScript name without weight suffix."""
        base, weight = extract_weight_from_name("Monaco")
        assert base == "Monaco"
        assert weight is None

    def test_semibold(self):
        """Test SemiBold weight."""
        base, weight = extract_weight_from_name("JetBrainsMono-SemiBold")
        assert base == "JetBrainsMono"
        assert weight == "SemiBold"

    def test_empty_string(self):
        """Test empty string."""
        base, weight = extract_weight_from_name("")
        assert base == ""
        assert weight is None

    def test_abbreviated_reg_suffix(self):
        """Test abbreviated -Reg suffix extraction."""
        base, weight = extract_weight_from_name("M+CodeLat60NFP-Reg")
        assert base == "M+CodeLat60NFP"
        assert weight == "Reg"


class TestNormalizeFontFamily:
    """Tests for font family normalization."""

    def test_postscript_with_weight(self):
        """Test normalizing PostScript name with weight."""
        result = normalize_font_family("JetBrainsMono-Bold")
        # Should remove weight and convert to friendly
        assert "-Bold" not in result
        assert " " in result or result == "JetBrainsMono"

    def test_friendly_name(self):
        """Test friendly name passes through."""
        result = normalize_font_family("JetBrains Mono")
        assert result == "JetBrains Mono"

    def test_friendly_with_weight(self):
        """Test friendly name with weight gets weight removed."""
        result = normalize_font_family("JetBrains Mono Bold")
        assert result == "JetBrains Mono"

    def test_empty_string(self):
        """Test empty string handling."""
        assert normalize_font_family("") == ""

    def test_none_handling(self):
        """Test None handling."""
        assert normalize_font_family(None) is None


class TestSystemFontLookup:
    """Tests for system font database lookups."""

    def test_heuristic_fallback_when_system_returns_none(self):
        """Test that heuristics are used when system lookup fails."""
        with patch(
            "console_cowboy.utils.fonts._get_system_font_names", return_value=None
        ):
            # Should fall back to heuristics
            result = postscript_to_friendly("JetBrainsMono-Regular")
            assert "Mono" in result
            assert "-Regular" not in result

    def test_system_lookup_used_when_available(self):
        """Test that system lookup is preferred when available."""
        with patch(
            "console_cowboy.utils.fonts._get_system_font_names",
            return_value=("System Font Name", "SystemFontName-Regular"),
        ):
            result = postscript_to_friendly("AnyFont")
            assert result == "System Font Name"

    def test_friendly_to_postscript_uses_system_lookup(self):
        """Test that friendly_to_postscript uses system lookup."""
        with patch(
            "console_cowboy.utils.fonts._get_system_font_names",
            return_value=("System Font", "SystemFont-Regular"),
        ):
            result = friendly_to_postscript("System Font")
            assert result == "SystemFont-Regular"

    def test_friendly_to_postscript_respects_weight_override(self):
        """Test that weight override works with system lookup."""
        with patch(
            "console_cowboy.utils.fonts._get_system_font_names",
            return_value=("System Font", "SystemFont-Regular"),
        ):
            result = friendly_to_postscript("System Font", "Bold")
            assert "Bold" in result
            assert "SystemFont" in result

    def test_heuristic_preserves_special_characters(self):
        """Test that heuristic handles fonts with + character."""
        # Direct test of heuristic function
        result = _postscript_to_friendly_heuristic("M+Code-Regular")
        assert "M+Code" in result
        assert "-Regular" not in result

    def test_get_system_font_names_unsupported_platform(self):
        """Test that unsupported platforms return None."""
        with patch.object(sys, "platform", "win32"):
            result = _get_system_font_names("AnyFont")
            assert result is None
