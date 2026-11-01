"""CLI refine command."""

import asyncio
from typing import Optional
import click

from eightgen.cli.display import console, print_banner, print_game_card, print_error, print_status
from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent


@click.command(name="refine")
@click.argument("game_id", type=str)
@click.argument("instruction", type=str)
@click.option("--model", "-m", type=str, default=None, help="Override Ollama model")
@click.option("--no-open", is_flag=True, default=False, help="Do not automatically open game in browser")
def refine_cmd(
    game_id: str,
    instruction: str,
    model: Optional[str],
    no_open: bool,
) -> None:
    """Iterate or modify an existing game (use 'last' for most recent)."""
    print_banner()

    settings = get_settings(model=model, auto_open=not no_open)
    agent = Agent(settings)

    async def _run():
        print_status(f"Target Game: [bold cyan]{game_id}[/bold cyan]")
        print_status(f"Instruction: [bold yellow]\"{instruction}\"[/bold yellow]")

        with console.status("[bold green]Refining game architecture...", spinner="dots"):
            try:
                game = await agent.refine_game(
                    game_id=game_id,
                    instruction=instruction,
                    auto_open=not no_open,
                )
            except Exception as e:
                print_error(f"Refinement failed: {e}")
                return

        print_game_card(game)
        if not no_open:
            console.print(f"[bold green]🚀 Refined version v{game.current_version} launched in browser![/bold green]")

    asyncio.run(_run())
