---
allowed-tools: Bash(uv run:*)
argument-hint: <terminal_name>
description: Fetch terminal emulator documentation for the knowledge base
---

# Fetch Terminal Documentation

Fetch the latest documentation for a terminal emulator to use as context.

## Available Terminals

- `ghostty` - Ghostty configuration reference
- `kitty` - Kitty configuration reference
- `alacritty` - Alacritty man page (scdoc)
- `wezterm` - WezTerm configuration (multiple pages)
- `iterm2` - iTerm2 preferences documentation
- `windows_terminal` - Windows Terminal JSON Schema
- `macos_terminal` - macOS Terminal.app preferences (macOS only)

## Usage

`/docs ghostty` - Fetch Ghostty documentation
`/docs --list` - List available terminals

## Instructions

Run the knowledge base builder script to fetch documentation for terminal: **$ARGUMENTS**

```bash
uv run python scripts/build_knowledge_base.py $ARGUMENTS
```

After fetching, read the generated documentation file from `docs/knowledge_base/` and use it as context for answering questions about that terminal's configuration.
