"""Main CLI entry point for 8Gen."""

import click
from eightgen import __version__
from eightgen.cli.commands.generate import generate_cmd
from eightgen.cli.commands.refine import refine_cmd
from eightgen.cli.commands.list import list_cmd
from eightgen.cli.commands.serve import serve_cmd
from eightgen.cli.commands.export import export_cmd
from eightgen.cli.commands.config import config_cmd
from eightgen.cli.commands.wizard import wizard_cmd, run_interactive_wizard
from eightgen.cli.commands.image import image_cmd


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, "-v", "--version", message="8Gen version %(version)s")
def cli(ctx: click.Context) -> None:
    """8Gen - Autonomous AI Agent that crafts instant HTML5 games locally."""
    if ctx.invoked_subcommand is None:
        run_interactive_wizard()


cli.add_command(wizard_cmd)
cli.add_command(image_cmd)
cli.add_command(generate_cmd)
cli.add_command(refine_cmd)
cli.add_command(list_cmd)
cli.add_command(serve_cmd)
cli.add_command(export_cmd)
cli.add_command(config_cmd)

if __name__ == "__main__":
    cli()
