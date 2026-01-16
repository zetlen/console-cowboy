# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install with test dependencies
pip install -e '.[test]'

# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=console_cowboy

# Run a single test file
python -m pytest tests/test_terminals.py

# Run a specific test
python -m pytest tests/test_terminals.py::test_ghostty_parse

# Run CLI directly
console-cowboy export ghostty -o config.toml
console-cowboy import config.toml -t alacritty
python -m console_cowboy [command]
```

## Architecture

Console Cowboy uses a **plugin-based adapter pattern** with CTEC (Common Terminal Emulator Configuration) as an intermediate representation.

### Core Components

1. **CTEC Schema** (`ctec/schema.py`): Dataclass-based data model with `ColorScheme`, `FontConfig`, `CursorConfig`, `WindowConfig`, `BehaviorConfig`, `KeyBinding`, `Profile`, and `TerminalSpecificSetting`. All classes implement `.to_dict()` / `.from_dict()` for serialization.

2. **TerminalAdapter** (`terminals/base.py`): Abstract base class with:
   - `parse(source) -> CTECConfig`: Convert native config to CTEC
   - `export(ctec) -> str`: Convert CTEC to native format
   - `TerminalRegistry`: Manages adapter registration and lookup

3. **Terminal Adapters** (`terminals/`): Five implementations (iterm2, ghostty, alacritty, kitty, wezterm), each handling their native config format.

4. **Serializers** (`ctec/serializers.py`): TOML (default), JSON, YAML output with auto-format detection.

5. **CLI** (`cli.py`): Click-based commands: `export`, `import`, `convert`, `list`, `info`.

### Data Flow

```
Native Config → TerminalAdapter.parse() → CTEC → TerminalAdapter.export() → Native Config
```

## Key Patterns

- **Color handling**: All colors normalized to RGB (0-255) via `utils/colors.py`. Use `normalize_color()` for any color input.
- **Unmappable settings**: Stored in `terminal_specific` list to allow round-trip conversion for the same terminal.
- **Warnings**: Use `ctec.add_warning()` for conversion issues instead of failing.
- **CLI output**: stderr for progress/warnings, stdout for output. Use `click.style()` for formatting.

## Adding New Terminal Support

1. Create adapter in `console_cowboy/terminals/your_terminal.py`
2. Inherit from `TerminalAdapter`, implement `parse()` and `export()`
3. Register in `console_cowboy/terminals/__init__.py`
4. Add test fixtures in `tests/fixtures/` and tests in `tests/test_terminals.py`
