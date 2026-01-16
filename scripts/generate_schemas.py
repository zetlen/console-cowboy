#!/usr/bin/env python3
"""
Generate JSON schemas for CTEC and iTerm2-Color-Schemes formats.

This is a developer script for generating schemas to be committed to the repository.
The schemas are generated to the project root for easy discovery.

Usage:
    python scripts/generate_schemas.py

Output files:
    - ctec.schema.json: Full CTEC schema (bundled, single file)
    - iterm2-color-scheme.schema.json: Standalone color scheme schema
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import console_cowboy
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from console_cowboy.ctec.serializers import (
    CTECSerializer,
    CTEC_JSON_SCHEMA_BUNDLED,
    ITERM2_COLOR_SCHEME_SCHEMA,
)


def main():
    """Generate JSON schemas for CTEC and color schemes."""
    # Output to project root
    output_dir = project_root

    # Generate bundled CTEC schema (single file, ready for users)
    ctec_schema_path = output_dir / "ctec.schema.json"
    print(f"Writing CTEC schema to {ctec_schema_path}")
    ctec_schema_path.write_text(json.dumps(CTEC_JSON_SCHEMA_BUNDLED, indent=2))

    # Generate standalone color scheme schema (can be PR'd to iTerm2-Color-Schemes)
    color_scheme_path = output_dir / "iterm2-color-scheme.schema.json"
    print(f"Writing color scheme schema to {color_scheme_path}")
    color_scheme_path.write_text(json.dumps(ITERM2_COLOR_SCHEME_SCHEMA, indent=2))

    print("\nSchemas generated successfully!")
    print("\nFor YAML editor validation, add this comment to your CTEC files:")
    print("    # yaml-language-server: $schema=./ctec.schema.json")


if __name__ == "__main__":
    main()
