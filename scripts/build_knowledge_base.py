#!/usr/bin/env python3
"""
build_knowledge_base.py

Fetches and cleans documentation for terminal emulators supported by Console Cowboy.

Usage:
    # Fetch all terminals
    uv run python scripts/build_knowledge_base.py

    # Fetch specific terminal(s)
    uv run python scripts/build_knowledge_base.py ghostty kitty
    uv run python scripts/build_knowledge_base.py --terminal=wezterm

    # List available terminals
    uv run python scripts/build_knowledge_base.py --list

The output is stored in `docs/knowledge_base/` to be used as context for LLMs.
"""

import argparse
import json
import platform
import plistlib
import re
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

# Third-party imports
try:
    import html2text
    import requests
    from bs4 import BeautifulSoup, Comment
except ImportError:
    print("Error: This script requires 'requests', 'beautifulsoup4', and 'html2text'.")
    print("Run: uv sync --group scripts")
    sys.exit(1)

OUTPUT_DIR = Path("docs/knowledge_base")


def create_html2text_converter():
    """Create and configure an html2text converter for documentation."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0  # Don't wrap lines
    h.protect_links = True
    h.unicode_snob = True
    h.skip_internal_links = True
    return h


def clean_documentation(content):
    """Apply cleaning to documentation content."""
    # Remove excessive code blocks (keep first example per section, limit length)
    # This is a light touch - we want examples but not redundant ones

    # Remove navigation cruft patterns
    nav_patterns = [
        r"^Table of Contents\n.*?(?=\n#|\n\*\*|\Z)",
        r"^\s*\*\s*\[.*?\]\(</.*?>\)\s*$",
        r"^Introduction\n\n\s*\*.*?(?=\n#|\n---|\Z)",
        r"^User Interface\n\n\s*\*.*?(?=\n#|\n---|\Z)",
        r"^Features\n\n\s*\*.*?(?=\n#|\n---|\Z)",
        r"^Scripting\n\n\s*\*.*?(?=\n#|\n---|\Z)",
        r"^Advanced\n\n\s*\*.*?(?=\n#|\n---|\Z)",
        r"^\* \* \*\s*$",
        r"^\[Showing results with pagination.*?\]$",
    ]

    for pattern in nav_patterns:
        content = re.sub(pattern, "", content, flags=re.MULTILINE | re.DOTALL)

    # Remove boilerplate patterns
    boilerplate_patterns = [
        r"Changing this configuration at runtime will only affect new terminals.*?$",
        r"{{since\('.*?'\)}}",
    ]

    for pattern in boilerplate_patterns:
        content = re.sub(pattern, "", content, flags=re.MULTILINE | re.IGNORECASE)

    # Clean up excessive newlines
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    return content


class TerminalDocFetcher(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def fetch(self):
        """Fetch and return the documentation content."""
        pass

    def save(self, content, extension="md"):
        """Save content to the output directory."""
        filename = OUTPUT_DIR / f"{self.name}.{extension}"
        print(f"  Saving to {filename}...")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)


class SchemaFetcher(TerminalDocFetcher):
    def __init__(self, name, description, url):
        super().__init__(name, description)
        self.url = url

    def fetch(self):
        print(f"  Fetching JSON schema from {self.url}...")
        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data, indent=2)

    def save(self, content):
        super().save(content, extension="json")


class WebDocFetcher(TerminalDocFetcher):
    """Fetches web documentation and converts HTML to markdown."""

    def __init__(self, name, description, url, content_selector="main"):
        super().__init__(name, description)
        self.url = url
        self.content_selector = content_selector

    def fetch(self):
        print(f"  Fetching documentation from {self.url}...")
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Extract main content
        content = (
            soup.select_one(self.content_selector) if self.content_selector else None
        )
        if not content:
            content = soup.body

        # Convert to markdown
        converter = create_html2text_converter()
        markdown = converter.handle(str(content))

        # Apply cleaning
        markdown = clean_documentation(markdown)

        header = f"# {self.name.replace('_', ' ').title()} Configuration Documentation\n\nSource: {self.url}\n\n"
        return header + markdown


class RawFileFetcher(TerminalDocFetcher):
    """Fetches raw files directly."""

    def __init__(self, name, description, url):
        super().__init__(name, description)
        self.url = url

    def fetch(self):
        print(f"  Fetching raw file from {self.url}...")
        response = requests.get(self.url)
        response.raise_for_status()
        return response.text


class CombinedDocFetcher(TerminalDocFetcher):
    """Fetches multiple documentation sources and combines them."""

    def __init__(self, name, description, sources):
        super().__init__(name, description)
        self.sources = sources

    def fetch(self):
        parts = [
            f"# {self.name.replace('_', ' ').title()} Configuration Documentation\n"
        ]
        parts.append("This document combines multiple documentation sources.\n\n")

        for source in self.sources:
            section_title = source[0]
            url = source[1]
            fetcher_type = source[2]
            content_selector = source[3] if len(source) > 3 else "main"

            print(f"  Fetching {section_title}...")

            try:
                response = requests.get(url)
                response.raise_for_status()

                if fetcher_type == "raw":
                    content = response.text
                else:
                    soup = BeautifulSoup(response.content, "html.parser")
                    for element in soup(
                        ["script", "style", "nav", "footer", "header", "aside"]
                    ):
                        element.decompose()
                    for comment in soup.find_all(
                        string=lambda text: isinstance(text, Comment)
                    ):
                        comment.extract()

                    main_content = soup.select_one(content_selector)
                    if not main_content:
                        main_content = soup.body

                    converter = create_html2text_converter()
                    content = converter.handle(str(main_content))

                content = clean_documentation(content)
                parts.append(f"\n---\n\n## {section_title}\n\nSource: {url}\n\n")
                parts.append(content)

            except Exception as e:
                parts.append(f"\n---\n\n## {section_title}\n\n**Error:** {e}\n")

        return "\n".join(parts)


class DefaultsReadFetcher(TerminalDocFetcher):
    """Fetches macOS application preferences using `defaults read`."""

    def __init__(self, name, description, domain):
        super().__init__(name, description)
        self.domain = domain

    def _format_value(self, value, indent=0):
        """Recursively format a plist value."""
        prefix = "  " * indent

        if isinstance(value, dict):
            if not value:
                return "{}"
            lines = ["{"]
            for k, v in sorted(value.items()):
                formatted_v = self._format_value(v, indent + 1)
                lines.append(f"{prefix}  {k} = {formatted_v}")
            lines.append(f"{prefix}}}")
            return "\n".join(lines)
        elif isinstance(value, list):
            if not value:
                return "[]"
            lines = ["["]
            for item in value:
                formatted_item = self._format_value(item, indent + 1)
                lines.append(f"{prefix}  {formatted_item},")
            lines.append(f"{prefix}]")
            return "\n".join(lines)
        elif isinstance(value, bytes):
            hex_preview = value[:32].hex()
            if len(value) > 32:
                hex_preview += "..."
            return f"<data: {len(value)} bytes, preview: {hex_preview}>"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            if len(value) > 500:
                value = value[:500] + "..."
            return json.dumps(value)
        else:
            return str(value)

    def fetch(self):
        if platform.system() != "Darwin":
            raise RuntimeError("DefaultsReadFetcher only works on macOS")

        print(f"  Reading defaults from {self.domain}...")

        result = subprocess.run(
            ["defaults", "export", self.domain, "-"],
            capture_output=True,
            check=True,
        )

        plist_data = plistlib.loads(result.stdout)

        parts = [
            "# macOS Terminal.app Configuration",
            "",
            f"Source: `defaults read {self.domain}`",
            "",
            "This file contains macOS Terminal.app preferences.",
            f"Settings stored in `~/Library/Preferences/{self.domain}.plist`.",
            "",
            "## Window Settings (Profiles)",
            "",
        ]

        window_settings = plist_data.get("Window Settings", {})
        if window_settings:
            for profile_name, profile_data in sorted(window_settings.items()):
                parts.append(f"### Profile: {profile_name}")
                parts.append("")
                parts.append("```")
                parts.append(self._format_value(profile_data))
                parts.append("```")
                parts.append("")

        other_settings = {k: v for k, v in plist_data.items() if k != "Window Settings"}
        if other_settings:
            parts.append("## Other Settings")
            parts.append("")
            parts.append("```")
            parts.append(self._format_value(other_settings))
            parts.append("```")

        return "\n".join(parts)


class GhosttyDocFetcher(TerminalDocFetcher):
    """Fetches Ghostty documentation, preferring local CLI if available."""

    GHOSTTY_WEB_URL = "https://ghostty.org/docs/config/reference"

    def __init__(self):
        super().__init__("ghostty", "Ghostty configuration reference")

    def _find_ghostty(self):
        """Find the ghostty executable, checking PATH and standard locations."""
        # Check PATH first
        ghostty_path = shutil.which("ghostty")
        if ghostty_path:
            return ghostty_path

        # Check standard macOS application bundle location
        macos_app_path = Path("/Applications/Ghostty.app/Contents/MacOS/ghostty")
        if macos_app_path.exists():
            return str(macos_app_path)

        return None

    def fetch(self):
        ghostty_path = self._find_ghostty()

        if ghostty_path:
            return self._fetch_from_cli(ghostty_path)
        else:
            return self._fetch_from_web()

    def _fetch_from_cli(self, ghostty_path):
        """Fetch documentation using ghostty +show-config --default --docs."""
        print(f"  Using local Ghostty installation: {ghostty_path}")
        print("  Running: ghostty +show-config --default --docs")

        result = subprocess.run(
            [ghostty_path, "+show-config", "--default", "--docs"],
            capture_output=True,
            text=True,
            check=True,
        )

        header = (
            "# Ghostty Configuration Reference\n\n"
            f"Generated from local Ghostty installation: `{ghostty_path}`\n\n"
            "This documentation was generated using `ghostty +show-config --default --docs`.\n\n"
            "---\n\n"
        )
        return header + result.stdout

    def _fetch_from_web(self):
        """Fall back to fetching documentation from the web."""
        print(f"  Ghostty not found locally, fetching from {self.GHOSTTY_WEB_URL}...")

        response = requests.get(self.GHOSTTY_WEB_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Extract main content
        content = soup.select_one("main")
        if not content:
            content = soup.body

        # Convert to markdown
        converter = create_html2text_converter()
        markdown = converter.handle(str(content))

        # Apply cleaning
        markdown = clean_documentation(markdown)

        header = f"# Ghostty Configuration Documentation\n\nSource: {self.GHOSTTY_WEB_URL}\n\n"
        return header + markdown


def is_macos():
    return platform.system() == "Darwin"


# Registry of all available terminal fetchers
def get_fetchers():
    fetchers = {
        "windows_terminal": SchemaFetcher(
            "windows_terminal",
            "Windows Terminal JSON Schema",
            "https://raw.githubusercontent.com/microsoft/terminal/main/doc/cascadia/profiles.schema.json",
        ),
        "alacritty": RawFileFetcher(
            "alacritty",
            "Alacritty man page (scdoc)",
            "https://raw.githubusercontent.com/alacritty/alacritty/master/extra/man/alacritty.5.scd",
        ),
        "ghostty": GhosttyDocFetcher(),
        "kitty": WebDocFetcher(
            "kitty",
            "Kitty configuration reference",
            "https://sw.kovidgoyal.net/kitty/conf/",
            content_selector="article",
        ),
        "wezterm": CombinedDocFetcher(
            "wezterm",
            "WezTerm configuration (multiple pages)",
            [
                (
                    "Appearance",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/appearance.md",
                    "raw",
                ),
                (
                    "Fonts",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/fonts.md",
                    "raw",
                ),
                (
                    "Keys",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/default-keys.md",
                    "raw",
                ),
                (
                    "Mouse",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/mouse.md",
                    "raw",
                ),
                (
                    "Colors",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/color_schemes.md",
                    "raw",
                ),
                (
                    "Launch",
                    "https://raw.githubusercontent.com/wezterm/wezterm/main/docs/config/launch.md",
                    "raw",
                ),
            ],
        ),
        "iterm2": CombinedDocFetcher(
            "iterm2",
            "iTerm2 preferences documentation",
            [
                (
                    "Profiles - General",
                    "https://iterm2.com/documentation-preferences-profiles-general.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Colors",
                    "https://iterm2.com/documentation-preferences-profiles-colors.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Text",
                    "https://iterm2.com/documentation-preferences-profiles-text.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Window",
                    "https://iterm2.com/documentation-preferences-profiles-window.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Terminal",
                    "https://iterm2.com/documentation-preferences-profiles-terminal.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Session",
                    "https://iterm2.com/documentation-preferences-profiles-session.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Keys",
                    "https://iterm2.com/documentation-preferences-profiles-keys.html",
                    "web",
                    "body",
                ),
                (
                    "Profiles - Advanced",
                    "https://iterm2.com/documentation-preferences-profiles-advanced.html",
                    "web",
                    "body",
                ),
                (
                    "Dynamic Profiles",
                    "https://iterm2.com/documentation-dynamic-profiles.html",
                    "web",
                    "body",
                ),
                (
                    "Hidden Settings",
                    "https://iterm2.com/documentation-hidden-settings.html",
                    "web",
                    "body",
                ),
            ],
        ),
    }

    # macOS-only fetcher
    if is_macos():
        fetchers["macos_terminal"] = DefaultsReadFetcher(
            "macos_terminal",
            "macOS Terminal.app preferences",
            "com.apple.Terminal",
        )

    return fetchers


def main():
    parser = argparse.ArgumentParser(
        description="Fetch terminal emulator documentation for knowledge base.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # Fetch all terminals
  %(prog)s ghostty kitty        # Fetch specific terminals
  %(prog)s --list               # List available terminals
        """,
    )
    parser.add_argument(
        "terminals",
        nargs="*",
        help="Terminal(s) to fetch. If not specified, fetches all.",
    )
    parser.add_argument(
        "--terminal",
        "-t",
        action="append",
        dest="terminals_opt",
        help="Terminal to fetch (can be repeated).",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available terminals and exit.",
    )

    args = parser.parse_args()

    fetchers = get_fetchers()

    if args.list:
        print("Available terminals:")
        for name, fetcher in sorted(fetchers.items()):
            print(f"  {name:20} - {fetcher.description}")
        return

    # Combine positional and --terminal arguments
    requested = args.terminals or []
    if args.terminals_opt:
        requested.extend(args.terminals_opt)

    # If no terminals specified, fetch all
    if not requested:
        requested = list(fetchers.keys())

    # Validate requested terminals
    invalid = [t for t in requested if t not in fetchers]
    if invalid:
        print(f"Error: Unknown terminal(s): {', '.join(invalid)}")
        print(f"Available: {', '.join(sorted(fetchers.keys()))}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in requested:
        fetcher = fetchers[name]
        print(f"[{name}] {fetcher.description}")
        try:
            content = fetcher.fetch()
            fetcher.save(content)
            print(f"[{name}] Done.")
        except Exception as e:
            print(f"[{name}] Error: {e}")

    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
