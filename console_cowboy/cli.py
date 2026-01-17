"""
Console Cowboy CLI - Portable Terminal Configuration Manager.

This CLI enables migration of terminal emulator configurations between
different terminal applications using the CTEC (Common Terminal Emulator
Configuration) format as an intermediate representation.

Commands:
    export: Export a terminal's configuration to CTEC format
    import: Import a CTEC configuration into a terminal's native format
    list: List supported terminal emulators
    convert: Convert directly between terminal configuration formats
"""

import sys
from pathlib import Path

import click

# Import to trigger registration
import console_cowboy.terminals  # noqa: F401
from console_cowboy.ctec import CTEC, CTECSerializer
from console_cowboy.ctec.serializers import OutputFormat
from console_cowboy.terminals import TerminalRegistry


def get_terminal_choices() -> list[str]:
    """Get list of available terminal names for CLI choices."""
    return TerminalRegistry.get_names()


def print_warnings(ctec: CTEC) -> None:
    """Print any warnings from the CTEC configuration."""
    if ctec.warnings:
        click.echo(click.style("\nWarnings:", fg="yellow", bold=True), err=True)
        for warning in ctec.warnings:
            click.echo(click.style(f"  - {warning}", fg="yellow"), err=True)


def print_terminal_specific(ctec: CTEC) -> None:
    """Print terminal-specific settings that couldn't be mapped."""
    if ctec.terminal_specific:
        click.echo(
            click.style(
                "\nTerminal-specific settings (not portable):", fg="cyan", bold=True
            ),
            err=True,
        )
        for setting in ctec.terminal_specific:
            click.echo(
                click.style(
                    f"  [{setting.terminal}] {setting.key} = {setting.value}", fg="cyan"
                ),
                err=True,
            )


class SourceResolution:
    """Result of resolving a source argument."""

    def __init__(
        self,
        terminal_type: str,
        path: Path | None = None,
        content: str | None = None,
        from_stdin: bool = False,
    ):
        self.terminal_type = terminal_type
        self.path = path
        self.content = content
        self.from_stdin = from_stdin


class DestinationResolution:
    """Result of resolving a destination argument."""

    def __init__(
        self,
        terminal_type: str | None = None,
        path: Path | None = None,
        to_stdout: bool = False,
    ):
        self.terminal_type = terminal_type
        self.path = path
        self.to_stdout = to_stdout


def resolve_source(
    from_arg: str,
    from_type: str | None = None,
) -> SourceResolution:
    """
    Resolve a --from argument to a terminal type, path, and content.

    Args:
        from_arg: The --from value (terminal name, file path, or "-" for stdin)
        from_type: Explicit terminal type override

    Returns:
        SourceResolution with terminal_type, path, content, and from_stdin

    Raises:
        click.ClickException: If source cannot be resolved
    """
    terminal_names = get_terminal_choices()

    # Check if it's stdin
    if from_arg == "-":
        content = sys.stdin.read()
        if from_type:
            if from_type.lower() not in terminal_names:
                raise click.ClickException(
                    f"Unknown terminal type: {from_type}. "
                    f"Supported: {', '.join(terminal_names)}"
                )
            return SourceResolution(
                terminal_type=from_type.lower(),
                content=content,
                from_stdin=True,
            )
        # Try to detect from content
        detected = TerminalRegistry.detect_terminal_type(content)
        if not detected:
            raise click.ClickException(
                "Cannot detect terminal type from stdin content. "
                "Please specify --from-type."
            )
        return SourceResolution(
            terminal_type=detected,
            content=content,
            from_stdin=True,
        )

    # Check if it's a terminal name
    if from_arg.lower() in terminal_names:
        terminal_type = from_arg.lower()
        path = TerminalRegistry.get_default_config_path_for_terminal(terminal_type)
        if not path or not path.exists():
            raise click.ClickException(
                f"Could not find default config for {terminal_type}. "
                f"Please specify a file path instead."
            )
        return SourceResolution(
            terminal_type=terminal_type,
            path=path,
        )

    # It's a file path
    path = Path(from_arg).expanduser().resolve()
    if not path.exists():
        raise click.ClickException(f"File not found: {path}")

    # Determine terminal type
    if from_type:
        if from_type.lower() not in terminal_names:
            raise click.ClickException(
                f"Unknown terminal type: {from_type}. "
                f"Supported: {', '.join(terminal_names)}"
            )
        return SourceResolution(
            terminal_type=from_type.lower(),
            path=path,
        )

    # Try to detect from file
    try:
        content = path.read_text()
    except UnicodeDecodeError:
        # Binary file - try to read bytes for detection
        content = path.read_bytes().decode("latin-1", errors="replace")

    detected = TerminalRegistry.detect_terminal_type(content, path)
    if not detected:
        raise click.ClickException(
            f"Cannot detect terminal type from {path}. "
            f"Please specify --from-type."
        )
    return SourceResolution(
        terminal_type=detected,
        path=path,
    )


def resolve_destination(
    to_arg: str | None,
    to_type: str | None = None,
    for_ctec_output: bool = False,
) -> DestinationResolution:
    """
    Resolve a --to argument to a terminal type and path.

    Args:
        to_arg: The --to value (terminal name, file path, "-" for stdout, or None)
        to_type: Explicit terminal type override
        for_ctec_output: If True, destination is for CTEC format (export command)

    Returns:
        DestinationResolution with terminal_type, path, and to_stdout

    Raises:
        click.ClickException: If destination cannot be resolved
    """
    terminal_names = get_terminal_choices()

    # No --to means stdout
    if to_arg is None or to_arg == "-":
        if for_ctec_output:
            return DestinationResolution(to_stdout=True)
        if to_type:
            if to_type.lower() not in terminal_names:
                raise click.ClickException(
                    f"Unknown terminal type: {to_type}. "
                    f"Supported: {', '.join(terminal_names)}"
                )
            return DestinationResolution(
                terminal_type=to_type.lower(),
                to_stdout=True,
            )
        if to_arg == "-":
            raise click.ClickException(
                "When writing to stdout with '-', --to-type is required "
                "to specify the output terminal format."
            )
        return DestinationResolution(to_stdout=True)

    # Check if it's a terminal name
    if to_arg.lower() in terminal_names:
        if for_ctec_output:
            raise click.ClickException(
                f"'{to_arg}' is a terminal name, not a file path. "
                f"For export, --to must be a file path or '-' for stdout."
            )
        terminal_type = to_arg.lower()
        path = TerminalRegistry.get_default_config_path_for_terminal(terminal_type)
        if not path:
            raise click.ClickException(
                f"Could not determine default config path for {terminal_type}."
            )
        return DestinationResolution(
            terminal_type=terminal_type,
            path=path,
        )

    # It's a file path
    path = Path(to_arg).expanduser().resolve()

    if for_ctec_output:
        return DestinationResolution(path=path)

    # For native output, we need a terminal type
    if to_type:
        if to_type.lower() not in terminal_names:
            raise click.ClickException(
                f"Unknown terminal type: {to_type}. "
                f"Supported: {', '.join(terminal_names)}"
            )
        return DestinationResolution(
            terminal_type=to_type.lower(),
            path=path,
        )

    # Try to detect from existing file content or path
    if path.exists():
        try:
            content = path.read_text()
            detected = TerminalRegistry.detect_terminal_type(content, path)
            if detected:
                return DestinationResolution(
                    terminal_type=detected,
                    path=path,
                )
        except Exception:
            pass

    # Try to detect from path alone
    detected = TerminalRegistry.detect_terminal_type("", path)
    if detected:
        return DestinationResolution(
            terminal_type=detected,
            path=path,
        )

    raise click.ClickException(
        f"Cannot detect terminal type for destination {path}. "
        f"Please specify --to-type."
    )


def write_output(content: str, path: Path | None, to_stdout: bool, quiet: bool) -> None:
    """Write output to file or stdout."""
    if to_stdout or path is None:
        click.echo(content)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if not quiet:
            click.echo(f"Written to {path}", err=True)


@click.group()
@click.version_option()
def cli():
    """
    Console Cowboy - Hop terminals like you hop Linux distributions.

    A tool for making terminal configurations portable across different
    terminal emulators. Export your settings from one terminal and import
    them into another.

    CTEC uses YAML as its primary format, aligned with the iTerm2-Color-Schemes
    ecosystem for maximum compatibility with existing themes.

    Supported terminals: iTerm2, Ghostty, Alacritty, Kitty, Wezterm, VSCode, Terminal.app

    \b
    Examples:
        # Convert between terminals using their default config locations
        console-cowboy convert --from iterm2 --to ghostty

        # Convert from a specific file, auto-detecting the source type
        console-cowboy convert --from ~/custom/config --to ghostty

        # Export iTerm2 config to CTEC format
        console-cowboy export --from iterm2

        # Import CTEC config into Ghostty format
        console-cowboy import --from config.yaml --to ghostty

        # Read from stdin, write to stdout
        cat config.yaml | console-cowboy import --from - --from-type ctec --to-type alacritty --to -
    """
    pass


@cli.command(name="list")
def list_terminals():
    """
    List all supported terminal emulators.

    Shows terminal names that can be used with the export, import, and
    convert commands.
    """
    click.echo(click.style("Supported terminal emulators:", bold=True))
    click.echo()
    for adapter in TerminalRegistry.list_terminals():
        click.echo(click.style(f"  {adapter.name}", fg="green", bold=True))
        click.echo(f"    {adapter.display_name}: {adapter.description}")
        if adapter.default_config_paths:
            paths = ", ".join(f"~/{p}" for p in adapter.default_config_paths)
            click.echo(click.style(f"    Config: {paths}", dim=True))
        click.echo()


@cli.command(name="export")
@click.option(
    "--from",
    "from_arg",
    required=True,
    help="Source: terminal name (e.g., 'iterm2'), file path, or '-' for stdin.",
)
@click.option(
    "--from-type",
    "from_type",
    type=click.Choice(get_terminal_choices(), case_sensitive=False),
    help="Explicit source terminal type (required if auto-detection fails).",
)
@click.option(
    "--to",
    "to_arg",
    help="Output file path or '-' for stdout. Defaults to stdout if not specified.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Output format (default: yaml).",
)
@click.option(
    "--profile",
    "profile_name",
    type=str,
    default=None,
    help="Profile name to export (iTerm2/Terminal.app only).",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress warnings and informational output.",
)
def export_config(
    from_arg: str,
    from_type: str | None,
    to_arg: str | None,
    output_format: str,
    profile_name: str | None,
    quiet: bool,
):
    """
    Export a terminal's configuration to CTEC format.

    The --from argument can be:
      - A terminal name (e.g., 'iterm2'): Uses the default config location
      - A file path: Detects terminal type from contents (or use --from-type)
      - '-': Read from stdin (requires --from-type)

    \b
    Examples:
        # Export from iTerm2's default location
        console-cowboy export --from iterm2

        # Export to a specific file
        console-cowboy export --from ghostty --to config.yaml

        # Export from a specific file
        console-cowboy export --from ~/custom/config --from-type kitty

        # Export a specific iTerm2 profile
        console-cowboy export --from iterm2 --profile "Development"

        # Export as JSON
        console-cowboy export --from alacritty --format json
    """
    # Resolve source
    source = resolve_source(from_arg, from_type)

    # Resolve destination (for CTEC output)
    dest = resolve_destination(to_arg, for_ctec_output=True)

    adapter = TerminalRegistry.get(source.terminal_type)
    if not adapter:
        raise click.ClickException(f"Unknown terminal: {source.terminal_type}")

    # Check if profile option is valid for this terminal
    if profile_name and source.terminal_type not in ("iterm2", "terminal_app"):
        raise click.ClickException(
            f"The --profile option is only supported for iTerm2 and Terminal.app. "
            f"{adapter.display_name} does not have multiple profiles."
        )

    if not quiet and source.path:
        click.echo(f"Reading from: {source.path}", err=True)

    # Parse configuration
    try:
        if source.terminal_type in ("iterm2", "terminal_app"):
            if source.from_stdin:
                ctec = adapter.parse("stdin", content=source.content, profile_name=profile_name)
            else:
                ctec = adapter.parse(source.path, profile_name=profile_name)
        else:
            if source.from_stdin:
                ctec = adapter.parse("stdin", content=source.content)
            else:
                ctec = adapter.parse(source.path)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except ValueError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Failed to parse {source.terminal_type} config: {e}")

    # Serialize to output format
    fmt = OutputFormat(output_format.lower())
    output = CTECSerializer.serialize(ctec, fmt)

    # Write output
    write_output(output, dest.path, dest.to_stdout, quiet)

    # Print warnings and terminal-specific settings
    if not quiet:
        print_warnings(ctec)
        print_terminal_specific(ctec)


@cli.command(name="import")
@click.option(
    "--from",
    "from_arg",
    required=True,
    help="Source CTEC file path or '-' for stdin.",
)
@click.option(
    "--to",
    "to_arg",
    help="Destination: terminal name, file path, or '-' for stdout.",
)
@click.option(
    "--to-type",
    "to_type",
    type=click.Choice(get_terminal_choices(), case_sensitive=False),
    help="Explicit destination terminal type (required if auto-detection fails).",
)
@click.option(
    "--format",
    "input_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    help="Input CTEC format. If not specified, detected from file extension.",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress warnings and informational output.",
)
def import_config(
    from_arg: str,
    to_arg: str | None,
    to_type: str | None,
    input_format: str | None,
    quiet: bool,
):
    """
    Import a CTEC configuration into a terminal's native format.

    The --from argument is a CTEC file path or '-' for stdin.

    The --to argument can be:
      - A terminal name (e.g., 'ghostty'): Writes to default config location
      - A file path: Detects terminal type from path/contents (or use --to-type)
      - '-': Write to stdout (requires --to-type)
      - Omitted: Write to stdout

    \b
    Examples:
        # Import to Ghostty's default config location
        console-cowboy import --from config.yaml --to ghostty

        # Import to a specific file
        console-cowboy import --from config.yaml --to ~/.config/alacritty/alacritty.toml --to-type alacritty

        # Import from stdin, output to stdout
        cat config.yaml | console-cowboy import --from - --to-type kitty --to -
    """
    # Read CTEC source
    if from_arg == "-":
        content = sys.stdin.read()
        # Determine format
        if input_format:
            fmt = OutputFormat(input_format.lower())
        else:
            # Default to YAML for stdin
            fmt = OutputFormat.YAML
    else:
        path = Path(from_arg).expanduser().resolve()
        if not path.exists():
            raise click.ClickException(f"File not found: {path}")

        # Determine format
        if input_format:
            fmt = OutputFormat(input_format.lower())
        else:
            try:
                fmt = CTECSerializer.detect_format(path)
            except ValueError:
                raise click.ClickException(
                    "Cannot detect CTEC format from extension. Please specify --format."
                )
        content = path.read_text()

    # Parse CTEC configuration
    try:
        ctec = CTECSerializer.deserialize(content, fmt)
    except Exception as e:
        raise click.ClickException(f"Failed to read CTEC config: {e}")

    # Resolve destination
    if to_arg is None and to_type is None:
        raise click.ClickException(
            "Either --to or --to-type is required to specify the output format."
        )

    dest = resolve_destination(to_arg, to_type, for_ctec_output=False)

    adapter = TerminalRegistry.get(dest.terminal_type)
    if not adapter:
        raise click.ClickException(f"Unknown terminal: {dest.terminal_type}")

    if not quiet and dest.path and not dest.to_stdout:
        click.echo(f"Writing to: {dest.path}", err=True)

    # Export to target format
    try:
        output = adapter.export(ctec)
    except Exception as e:
        raise click.ClickException(f"Failed to export to {dest.terminal_type} format: {e}")

    # Write output
    write_output(output, dest.path, dest.to_stdout, quiet)

    # Print warnings
    if not quiet:
        print_warnings(ctec)

        # Check for incompatibilities
        if ctec.source_terminal and ctec.source_terminal != dest.terminal_type:
            source_specific = ctec.get_terminal_specific(ctec.source_terminal)
            if source_specific:
                click.echo(
                    click.style(
                        f"\nNote: {len(source_specific)} setting(s) from "
                        f"{ctec.source_terminal} could not be converted to {dest.terminal_type}.",
                        fg="yellow",
                    ),
                    err=True,
                )


@cli.command(name="convert")
@click.option(
    "--from",
    "from_arg",
    required=True,
    help="Source: terminal name (e.g., 'iterm2'), file path, or '-' for stdin.",
)
@click.option(
    "--from-type",
    "from_type",
    type=click.Choice(get_terminal_choices(), case_sensitive=False),
    help="Explicit source terminal type (required if auto-detection fails).",
)
@click.option(
    "--to",
    "to_arg",
    help="Destination: terminal name, file path, or '-' for stdout.",
)
@click.option(
    "--to-type",
    "to_type",
    type=click.Choice(get_terminal_choices(), case_sensitive=False),
    help="Explicit destination terminal type (required if auto-detection fails).",
)
@click.option(
    "--profile",
    "profile_name",
    type=str,
    default=None,
    help="Profile name to convert (iTerm2/Terminal.app source only).",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress warnings and informational output.",
)
def convert_config(
    from_arg: str,
    from_type: str | None,
    to_arg: str | None,
    to_type: str | None,
    profile_name: str | None,
    quiet: bool,
):
    """
    Convert directly between terminal configuration formats.

    The --from argument can be:
      - A terminal name (e.g., 'iterm2'): Uses the default config location
      - A file path: Detects terminal type from contents (or use --from-type)
      - '-': Read from stdin (requires --from-type)

    The --to argument can be:
      - A terminal name (e.g., 'ghostty'): Writes to default config location
      - A file path: Detects terminal type from path/contents (or use --to-type)
      - '-': Write to stdout (requires --to-type)
      - Omitted: Write to stdout (requires --to-type)

    \b
    Examples:
        # Convert using default config locations
        console-cowboy convert --from iterm2 --to ghostty

        # Convert from a specific file, auto-detecting source type
        console-cowboy convert --from ~/custom/config --to ghostty

        # Convert with explicit types
        console-cowboy convert --from myconfig --from-type kitty --to-type alacritty --to -

        # Convert a specific iTerm2 profile
        console-cowboy convert --from iterm2 --to ghostty --profile "Development"
    """
    # Resolve source
    source = resolve_source(from_arg, from_type)

    # Resolve destination
    if to_arg is None and to_type is None:
        raise click.ClickException(
            "Either --to or --to-type is required to specify the output format."
        )

    dest = resolve_destination(to_arg, to_type, for_ctec_output=False)

    from_adapter = TerminalRegistry.get(source.terminal_type)
    to_adapter = TerminalRegistry.get(dest.terminal_type)

    if not from_adapter:
        raise click.ClickException(f"Unknown source terminal: {source.terminal_type}")
    if not to_adapter:
        raise click.ClickException(f"Unknown target terminal: {dest.terminal_type}")

    # Check if profile option is valid for this terminal
    if profile_name and source.terminal_type not in ("iterm2", "terminal_app"):
        raise click.ClickException(
            f"The --profile option is only supported when converting from iTerm2 or Terminal.app. "
            f"{from_adapter.display_name} does not have multiple profiles."
        )

    if not quiet:
        if source.path:
            click.echo(f"Reading from: {source.path}", err=True)
        if dest.path and not dest.to_stdout:
            click.echo(f"Writing to: {dest.path}", err=True)

    # Parse source configuration
    try:
        if source.terminal_type in ("iterm2", "terminal_app"):
            if source.from_stdin:
                ctec = from_adapter.parse("stdin", content=source.content, profile_name=profile_name)
            else:
                ctec = from_adapter.parse(source.path, profile_name=profile_name)
        else:
            if source.from_stdin:
                ctec = from_adapter.parse("stdin", content=source.content)
            else:
                ctec = from_adapter.parse(source.path)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except ValueError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Failed to parse {source.terminal_type} config: {e}")

    # Export to target format
    try:
        output = to_adapter.export(ctec)
    except Exception as e:
        raise click.ClickException(f"Failed to export to {dest.terminal_type} format: {e}")

    # Write output
    write_output(output, dest.path, dest.to_stdout, quiet)

    # Print warnings and incompatibilities
    if not quiet:
        print_warnings(ctec)

        source_specific = ctec.get_terminal_specific(source.terminal_type)
        if source_specific:
            click.echo(
                click.style(
                    f"\nNote: {len(source_specific)} {source.terminal_type}-specific setting(s) "
                    f"could not be converted:",
                    fg="yellow",
                ),
                err=True,
            )
            for setting in source_specific:
                click.echo(
                    click.style(f"  - {setting.key}", fg="yellow"),
                    err=True,
                )


@cli.command(name="info")
@click.option(
    "--from",
    "from_arg",
    required=True,
    help="Source: terminal name, file path, or CTEC file.",
)
@click.option(
    "--from-type",
    "from_type",
    type=click.Choice(get_terminal_choices(), case_sensitive=False),
    help="Terminal type (if parsing native config). If not specified, assumes CTEC format.",
)
def show_info(from_arg: str, from_type: str | None):
    """
    Display information about a configuration file.

    Shows what settings are present and what can/cannot be ported
    to other terminals.

    \b
    Examples:
        # Show info about a CTEC file
        console-cowboy info --from my-config.yaml

        # Show info about a native terminal config
        console-cowboy info --from ~/.config/kitty/kitty.conf --from-type kitty

        # Show info about a terminal's default config
        console-cowboy info --from iterm2 --from-type iterm2
    """
    terminal_names = get_terminal_choices()

    # Check if it's a terminal name with explicit type
    if from_arg.lower() in terminal_names and from_type:
        # Use default config path
        path = TerminalRegistry.get_default_config_path_for_terminal(from_arg.lower())
        if not path or not path.exists():
            raise click.ClickException(
                f"Could not find default config for {from_arg}."
            )
        adapter = TerminalRegistry.get(from_type.lower())
        if not adapter:
            raise click.ClickException(f"Unknown terminal: {from_type}")
        try:
            ctec = adapter.parse(path)
        except Exception as e:
            raise click.ClickException(f"Failed to parse config: {e}")
    elif from_type:
        # Parse as native config
        path = Path(from_arg).expanduser().resolve()
        if not path.exists():
            raise click.ClickException(f"File not found: {path}")

        adapter = TerminalRegistry.get(from_type.lower())
        if not adapter:
            raise click.ClickException(f"Unknown terminal: {from_type}")
        try:
            ctec = adapter.parse(path)
        except Exception as e:
            raise click.ClickException(f"Failed to parse config: {e}")
    else:
        # Try to parse as CTEC file
        path = Path(from_arg).expanduser().resolve()
        if not path.exists():
            raise click.ClickException(f"File not found: {path}")

        try:
            fmt = CTECSerializer.detect_format(path)
            ctec = CTECSerializer.read_file(path, fmt)
        except ValueError:
            # Try to detect and parse as native config
            try:
                content = path.read_text()
                detected = TerminalRegistry.detect_terminal_type(content, path)
                if detected:
                    adapter = TerminalRegistry.get(detected)
                    ctec = adapter.parse(path)
                else:
                    raise click.ClickException(
                        "Cannot detect format. Use --from-type to specify terminal type."
                    )
            except click.ClickException:
                raise
            except Exception as e:
                raise click.ClickException(f"Failed to parse config: {e}")
        except Exception as e:
            raise click.ClickException(f"Failed to parse CTEC config: {e}")

    # Display information
    click.echo(click.style("Configuration Summary", bold=True, underline=True))
    click.echo()

    if ctec.source_terminal:
        click.echo(f"Source terminal: {click.style(ctec.source_terminal, fg='green')}")

    click.echo(f"CTEC version: {ctec.version}")
    click.echo()

    # Colors
    if ctec.color_scheme:
        click.echo(click.style("Color Scheme:", bold=True))
        scheme = ctec.color_scheme
        color_count = sum(
            1
            for attr in [
                "foreground",
                "background",
                "cursor",
                "black",
                "red",
                "green",
            ]
            if getattr(scheme, attr, None)
        )
        click.echo(f"  Defined colors: {color_count}+")
        if scheme.name:
            click.echo(f"  Name: {scheme.name}")
        click.echo()

    # Font
    if ctec.font:
        click.echo(click.style("Font:", bold=True))
        if ctec.font.family:
            click.echo(f"  Family: {ctec.font.family}")
        if ctec.font.size:
            click.echo(f"  Size: {ctec.font.size}")
        click.echo()

    # Cursor
    if ctec.cursor:
        click.echo(click.style("Cursor:", bold=True))
        if ctec.cursor.style:
            click.echo(f"  Style: {ctec.cursor.style.value}")
        if ctec.cursor.blink is not None:
            click.echo(f"  Blink: {ctec.cursor.blink}")
        click.echo()

    # Window
    if ctec.window:
        click.echo(click.style("Window:", bold=True))
        if ctec.window.columns:
            click.echo(f"  Columns: {ctec.window.columns}")
        if ctec.window.rows:
            click.echo(f"  Rows: {ctec.window.rows}")
        if ctec.window.opacity is not None:
            click.echo(f"  Opacity: {ctec.window.opacity}")
        click.echo()

    # Behavior
    if ctec.behavior:
        click.echo(click.style("Behavior:", bold=True))
        if ctec.behavior.shell:
            click.echo(f"  Shell: {ctec.behavior.shell}")
        if ctec.behavior.scrollback_lines is not None:
            click.echo(f"  Scrollback: {ctec.behavior.scrollback_lines} lines")
        click.echo()

    # Key bindings
    if ctec.key_bindings:
        click.echo(click.style("Key Bindings:", bold=True))
        click.echo(f"  Defined: {len(ctec.key_bindings)}")
        click.echo()

    # Terminal-specific
    if ctec.terminal_specific:
        click.echo(click.style("Terminal-Specific Settings:", bold=True))
        by_terminal: dict[str, int] = {}
        for setting in ctec.terminal_specific:
            by_terminal[setting.terminal] = by_terminal.get(setting.terminal, 0) + 1
        for term, count in by_terminal.items():
            click.echo(f"  {term}: {count} setting(s)")
        click.echo()

    # Warnings
    print_warnings(ctec)


if __name__ == "__main__":
    cli()
