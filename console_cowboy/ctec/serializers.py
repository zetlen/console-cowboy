"""
CTEC Serializers - JSON, YAML, and TOML serialization for CTEC configurations.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Union

import tomli
import tomli_w
import yaml

from .schema import CTEC


class OutputFormat(Enum):
    """Supported output formats for CTEC serialization."""

    TOML = "toml"
    JSON = "json"
    YAML = "yaml"


class CTECSerializer:
    """
    Serializer for CTEC configurations.

    Supports reading and writing CTEC configs in TOML, JSON, and YAML formats.
    """

    @staticmethod
    def to_toml(ctec: CTEC) -> str:
        """
        Serialize CTEC to TOML string.

        Args:
            ctec: The CTEC configuration to serialize

        Returns:
            TOML string representation
        """
        return tomli_w.dumps(ctec.to_dict())

    @staticmethod
    def to_json(ctec: CTEC, indent: int = 2) -> str:
        """
        Serialize CTEC to JSON string.

        Args:
            ctec: The CTEC configuration to serialize
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(ctec.to_dict(), indent=indent)

    @staticmethod
    def to_yaml(ctec: CTEC) -> str:
        """
        Serialize CTEC to YAML string.

        Args:
            ctec: The CTEC configuration to serialize

        Returns:
            YAML string representation
        """
        return yaml.dump(ctec.to_dict(), default_flow_style=False, sort_keys=False)

    @staticmethod
    def serialize(ctec: CTEC, format: OutputFormat) -> str:
        """
        Serialize CTEC to the specified format.

        Args:
            ctec: The CTEC configuration to serialize
            format: Output format (TOML, JSON, or YAML)

        Returns:
            String representation in the specified format
        """
        if format == OutputFormat.TOML:
            return CTECSerializer.to_toml(ctec)
        elif format == OutputFormat.JSON:
            return CTECSerializer.to_json(ctec)
        elif format == OutputFormat.YAML:
            return CTECSerializer.to_yaml(ctec)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def from_toml(content: str) -> CTEC:
        """
        Deserialize CTEC from TOML string.

        Args:
            content: TOML string

        Returns:
            CTEC configuration
        """
        data = tomli.loads(content)
        return CTEC.from_dict(data)

    @staticmethod
    def from_json(content: str) -> CTEC:
        """
        Deserialize CTEC from JSON string.

        Args:
            content: JSON string

        Returns:
            CTEC configuration
        """
        data = json.loads(content)
        return CTEC.from_dict(data)

    @staticmethod
    def from_yaml(content: str) -> CTEC:
        """
        Deserialize CTEC from YAML string.

        Args:
            content: YAML string

        Returns:
            CTEC configuration
        """
        data = yaml.safe_load(content)
        return CTEC.from_dict(data)

    @staticmethod
    def deserialize(content: str, format: OutputFormat) -> CTEC:
        """
        Deserialize CTEC from the specified format.

        Args:
            content: String content to deserialize
            format: Input format (TOML, JSON, or YAML)

        Returns:
            CTEC configuration
        """
        if format == OutputFormat.TOML:
            return CTECSerializer.from_toml(content)
        elif format == OutputFormat.JSON:
            return CTECSerializer.from_json(content)
        elif format == OutputFormat.YAML:
            return CTECSerializer.from_yaml(content)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def detect_format(path: Union[str, Path]) -> OutputFormat:
        """
        Detect the format based on file extension.

        Args:
            path: Path to the file

        Returns:
            Detected output format

        Raises:
            ValueError: If the format cannot be determined
        """
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".toml":
            return OutputFormat.TOML
        elif suffix == ".json":
            return OutputFormat.JSON
        elif suffix in (".yaml", ".yml"):
            return OutputFormat.YAML
        else:
            raise ValueError(
                f"Cannot determine format from extension: {suffix}. "
                "Use --format to specify explicitly."
            )

    @staticmethod
    def read_file(path: Union[str, Path], format: OutputFormat = None) -> CTEC:
        """
        Read CTEC from a file.

        Args:
            path: Path to the file
            format: Optional format override (auto-detected from extension if not provided)

        Returns:
            CTEC configuration
        """
        path = Path(path)
        if format is None:
            format = CTECSerializer.detect_format(path)
        content = path.read_text()
        return CTECSerializer.deserialize(content, format)

    @staticmethod
    def write_file(
        ctec: CTEC, path: Union[str, Path], format: OutputFormat = None
    ) -> None:
        """
        Write CTEC to a file.

        Args:
            ctec: The CTEC configuration to write
            path: Path to the output file
            format: Optional format override (auto-detected from extension if not provided)
        """
        path = Path(path)
        if format is None:
            format = CTECSerializer.detect_format(path)
        content = CTECSerializer.serialize(ctec, format)
        path.write_text(content)
