"""Tests for CTEC serializers (TOML, JSON, YAML)."""

import json
import tempfile
from pathlib import Path

import pytest
import tomli
import yaml

from console_cowboy.ctec.schema import (
    CTEC,
    Color,
    ColorScheme,
    CursorConfig,
    CursorStyle,
    FontConfig,
)
from console_cowboy.ctec.serializers import CTECSerializer, OutputFormat


@pytest.fixture
def sample_ctec():
    """Create a sample CTEC configuration for testing."""
    return CTEC(
        source_terminal="test",
        color_scheme=ColorScheme(
            foreground=Color(255, 255, 255),
            background=Color(0, 0, 0),
        ),
        font=FontConfig(family="JetBrains Mono", size=14.0),
        cursor=CursorConfig(style=CursorStyle.BLOCK, blink=True),
    )


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_format_values(self):
        assert OutputFormat.TOML.value == "toml"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.YAML.value == "yaml"


class TestTOMLSerialization:
    """Tests for TOML serialization."""

    def test_to_toml(self, sample_ctec):
        output = CTECSerializer.to_toml(sample_ctec)
        assert isinstance(output, str)

        # Parse the output and verify
        parsed = tomli.loads(output)
        assert parsed["version"] == "1.0"
        assert parsed["source_terminal"] == "test"
        assert parsed["font"]["family"] == "JetBrains Mono"

    def test_from_toml(self):
        toml_content = """
version = "1.0"
source_terminal = "kitty"

[font]
family = "Fira Code"
size = 12.0

[cursor]
style = "beam"
blink = false
"""
        ctec = CTECSerializer.from_toml(toml_content)
        assert ctec.source_terminal == "kitty"
        assert ctec.font.family == "Fira Code"
        assert ctec.cursor.style == CursorStyle.BEAM

    def test_toml_roundtrip(self, sample_ctec):
        toml_str = CTECSerializer.to_toml(sample_ctec)
        restored = CTECSerializer.from_toml(toml_str)

        assert restored.source_terminal == sample_ctec.source_terminal
        assert restored.font.family == sample_ctec.font.family
        assert restored.cursor.style == sample_ctec.cursor.style


class TestJSONSerialization:
    """Tests for JSON serialization."""

    def test_to_json(self, sample_ctec):
        output = CTECSerializer.to_json(sample_ctec)
        assert isinstance(output, str)

        # Parse the output and verify
        parsed = json.loads(output)
        assert parsed["version"] == "1.0"
        assert parsed["source_terminal"] == "test"
        assert parsed["font"]["family"] == "JetBrains Mono"

    def test_to_json_with_indent(self, sample_ctec):
        output = CTECSerializer.to_json(sample_ctec, indent=4)
        # Check that it's properly indented
        assert "    " in output

    def test_from_json(self):
        json_content = """
{
    "version": "1.0",
    "source_terminal": "alacritty",
    "font": {
        "family": "Monaco",
        "size": 13.0
    }
}
"""
        ctec = CTECSerializer.from_json(json_content)
        assert ctec.source_terminal == "alacritty"
        assert ctec.font.family == "Monaco"
        assert ctec.font.size == 13.0

    def test_json_roundtrip(self, sample_ctec):
        json_str = CTECSerializer.to_json(sample_ctec)
        restored = CTECSerializer.from_json(json_str)

        assert restored.source_terminal == sample_ctec.source_terminal
        assert restored.font.family == sample_ctec.font.family


class TestYAMLSerialization:
    """Tests for YAML serialization."""

    def test_to_yaml(self, sample_ctec):
        output = CTECSerializer.to_yaml(sample_ctec)
        assert isinstance(output, str)

        # Parse the output and verify
        parsed = yaml.safe_load(output)
        assert parsed["version"] == "1.0"
        assert parsed["source_terminal"] == "test"
        assert parsed["font"]["family"] == "JetBrains Mono"

    def test_from_yaml(self):
        yaml_content = """
version: "1.0"
source_terminal: ghostty
font:
  family: Fira Code
  size: 12.0
cursor:
  style: underline
  blink: true
"""
        ctec = CTECSerializer.from_yaml(yaml_content)
        assert ctec.source_terminal == "ghostty"
        assert ctec.font.family == "Fira Code"
        assert ctec.cursor.style == CursorStyle.UNDERLINE

    def test_yaml_roundtrip(self, sample_ctec):
        yaml_str = CTECSerializer.to_yaml(sample_ctec)
        restored = CTECSerializer.from_yaml(yaml_str)

        assert restored.source_terminal == sample_ctec.source_terminal
        assert restored.font.family == sample_ctec.font.family


class TestSerializeMethod:
    """Tests for the generic serialize method."""

    def test_serialize_toml(self, sample_ctec):
        output = CTECSerializer.serialize(sample_ctec, OutputFormat.TOML)
        parsed = tomli.loads(output)
        assert parsed["version"] == "1.0"

    def test_serialize_json(self, sample_ctec):
        output = CTECSerializer.serialize(sample_ctec, OutputFormat.JSON)
        parsed = json.loads(output)
        assert parsed["version"] == "1.0"

    def test_serialize_yaml(self, sample_ctec):
        output = CTECSerializer.serialize(sample_ctec, OutputFormat.YAML)
        parsed = yaml.safe_load(output)
        assert parsed["version"] == "1.0"


class TestDeserializeMethod:
    """Tests for the generic deserialize method."""

    def test_deserialize_toml(self):
        content = 'version = "1.0"\n[font]\nfamily = "Test"'
        ctec = CTECSerializer.deserialize(content, OutputFormat.TOML)
        assert ctec.font.family == "Test"

    def test_deserialize_json(self):
        content = '{"version": "1.0", "font": {"family": "Test"}}'
        ctec = CTECSerializer.deserialize(content, OutputFormat.JSON)
        assert ctec.font.family == "Test"

    def test_deserialize_yaml(self):
        content = "version: '1.0'\nfont:\n  family: Test"
        ctec = CTECSerializer.deserialize(content, OutputFormat.YAML)
        assert ctec.font.family == "Test"


class TestFormatDetection:
    """Tests for format detection from file extension."""

    def test_detect_toml(self):
        assert CTECSerializer.detect_format("config.toml") == OutputFormat.TOML

    def test_detect_json(self):
        assert CTECSerializer.detect_format("config.json") == OutputFormat.JSON

    def test_detect_yaml(self):
        assert CTECSerializer.detect_format("config.yaml") == OutputFormat.YAML
        assert CTECSerializer.detect_format("config.yml") == OutputFormat.YAML

    def test_detect_unknown_raises(self):
        with pytest.raises(ValueError):
            CTECSerializer.detect_format("config.txt")

    def test_detect_with_path_object(self):
        assert CTECSerializer.detect_format(Path("config.toml")) == OutputFormat.TOML


class TestFileOperations:
    """Tests for file read/write operations."""

    def test_write_and_read_toml(self, sample_ctec):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            CTECSerializer.write_file(sample_ctec, path)

            restored = CTECSerializer.read_file(path)
            assert restored.font.family == sample_ctec.font.family

    def test_write_and_read_json(self, sample_ctec):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            CTECSerializer.write_file(sample_ctec, path)

            restored = CTECSerializer.read_file(path)
            assert restored.font.family == sample_ctec.font.family

    def test_write_and_read_yaml(self, sample_ctec):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            CTECSerializer.write_file(sample_ctec, path)

            restored = CTECSerializer.read_file(path)
            assert restored.font.family == sample_ctec.font.family

    def test_read_with_explicit_format(self, sample_ctec):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write as TOML but with .txt extension
            path = Path(tmpdir) / "config.txt"
            path.write_text(CTECSerializer.to_toml(sample_ctec))

            # Read with explicit format
            restored = CTECSerializer.read_file(path, OutputFormat.TOML)
            assert restored.font.family == sample_ctec.font.family

    def test_write_with_explicit_format(self, sample_ctec):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write as JSON but with .txt extension
            path = Path(tmpdir) / "config.txt"
            CTECSerializer.write_file(sample_ctec, path, OutputFormat.JSON)

            # Verify it's valid JSON
            content = path.read_text()
            parsed = json.loads(content)
            assert parsed["font"]["family"] == sample_ctec.font.family
