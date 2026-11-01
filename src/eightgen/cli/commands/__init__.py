"""CLI commands."""

from eightgen.cli.commands.generate import generate_cmd
from eightgen.cli.commands.refine import refine_cmd
from eightgen.cli.commands.list import list_cmd
from eightgen.cli.commands.serve import serve_cmd
from eightgen.cli.commands.export import export_cmd
from eightgen.cli.commands.config import config_cmd
from eightgen.cli.commands.wizard import wizard_cmd, run_interactive_wizard
from eightgen.cli.commands.image import image_cmd

__all__ = [
    "generate_cmd",
    "refine_cmd",
    "list_cmd",
    "serve_cmd",
    "export_cmd",
    "config_cmd",
    "wizard_cmd",
    "image_cmd",
    "run_interactive_wizard",
]
