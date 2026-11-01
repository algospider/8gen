"""CLI list command."""

from typing import Optional
import click
from eightgen.cli.display import print_banner, print_games_table
from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent


@click.command(name="list")
@click.option("--limit", "-n", type=int, default=50, help="Maximum number of games to display")
@click.option("--tag", "-t", type=str, default=None, help="Filter by tag or category")
def list_cmd(limit: int, tag: Optional[str]) -> None:
    """List all generated games in the local library."""
    print_banner()
    settings = get_settings()
    agent = Agent(settings)
    games = agent.list_games(limit=limit, tag=tag)
    print_games_table(games)
