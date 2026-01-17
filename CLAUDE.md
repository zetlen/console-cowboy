# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install dependencies (uses uv for dependency management)
uv sync

# Run all tests
uv run python -m pytest

# Run tests with coverage
uv run python -m pytest --cov=console_cowboy

# Run a single test file
uv run python -m pytest tests/test_terminals.py

# Run a specific test
uv run python -m pytest tests/test_terminals.py::test_ghostty_parse

# Run CLI directly
uv run console-cowboy export ghostty -o config.toml
uv run console-cowboy import config.toml -t alacritty

# Or use mise tasks
mise run test
mise run sync
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

## CTEC Schema Design: The Commutativity Principle

**CRITICAL**: The CTEC schema follows a strict commutativity principle for deciding what becomes a first-class schema citizen:

> **If a configuration concept is supported by 2 or more terminal emulators, it MUST be represented in the CTEC schema as a common field.**

This ensures:
1. Settings that are genuinely portable get proper schema representation
2. Terminal-specific settings stay in `terminal_specific` without polluting the common schema
3. Users can convert between terminals and retain meaningful configuration

### When Adding New Configuration Support

1. **Research all terminals**: Check documentation for Ghostty, Kitty, WezTerm, iTerm2, and Alacritty
2. **Identify commutative concepts**: Settings supported by 2+ terminals become schema fields
3. **Store terminal-specific settings**: Settings unique to one terminal go in `terminal_specific`
4. **Document mappings**: Create mapping tables showing how each terminal's setting maps to CTEC
5. **Handle edge cases**: Add validation (e.g., Ghostty's 0.15 minimum for unfocused-split-opacity)

### Example: Tab Bar Visibility

- Ghostty: `window-show-tab-bar` (always/auto/never)
- Kitty: `tab_bar_min_tabs` (1=always, 2=auto) + `tab_bar_style=hidden`
- WezTerm: `enable_tab_bar` + `hide_tab_bar_if_only_one_tab`

All three support the concept → Create `TabBarVisibility` enum in CTEC schema.

## Terminal Documentation & Knowledge Base

This project maintains a knowledge base of terminal documentation in `docs/knowledge_base/`.

### Using the Knowledge Base

**ALWAYS check the knowledge base before making changes to terminal adapters:**

```bash
# Fetch/update documentation for a terminal
uv run python scripts/build_knowledge_base.py ghostty kitty wezterm iterm2

# Or use the /docs skill in Claude Code
/docs ghostty
```

The knowledge base files (`docs/knowledge_base/*.md`) contain:
- Official configuration references
- Accurate setting names and values
- Default values and valid ranges
- Platform-specific notes

### Priority for Terminal Research

1. **First**: Check `docs/knowledge_base/<terminal>.md` for cached documentation
2. **Second**: Use `/docs <terminal>` skill to fetch fresh documentation
3. **Third**: Web search or Context7 for additional context

This ensures consistent, accurate terminal configuration mappings.

## Adding New Terminal Support

1. Create adapter directory: `console_cowboy/terminals/your_terminal/`
2. Create `__init__.py` with docstring and adapter import:
   ```python
   """Your Terminal adapter."""
   from .adapter import YourTerminalAdapter
   __all__ = ["YourTerminalAdapter"]
   ```
3. Create `adapter.py` with your `TerminalAdapter` subclass implementing `parse()` and `export()`
4. Register in `console_cowboy/terminals/__init__.py`
5. Add test fixtures in `tests/fixtures/` and tests in `tests/test_terminals.py`

**Note:** For complex adapters (like WezTerm with Lua parsing), you can add additional modules alongside `adapter.py` in the subdirectory.
