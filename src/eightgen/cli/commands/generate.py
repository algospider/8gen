"""CLI generate command."""

import asyncio
from typing import Optional
import click
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from eightgen.cli.display import console, print_banner, print_game_card, print_error, print_status
from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent


@click.command(name="generate")
@click.argument("prompt", type=str)
@click.option("--category", "-c", type=str, default=None, help="Game category (arcade, platformer, puzzle, etc.)")
@click.option("--model", "-m", type=str, default=None, help="Override Ollama model")
@click.option("--no-open", is_flag=True, default=False, help="Do not automatically open game in browser")
@click.option("--temperature", "-t", type=float, default=None, help="Sampling temperature")
def generate_cmd(
    prompt: str,
    category: Optional[str],
    model: Optional[str],
    no_open: bool,
    temperature: Optional[float],
) -> None:
    """Generate a brand new HTML5 game from a prompt."""
    print_banner()

    settings = get_settings(
        model=model,
        auto_open=not no_open,
        temperature=temperature,
    )
    agent = Agent(settings)

    async def _run():
        print_status(f"Requesting game: [bold yellow]\"{prompt}\"[/bold yellow]")
        if category:
            print_status(f"Category: [cyan]{category}[/cyan]")
        print_status(f"Ollama Model: [magenta]{settings.model}[/magenta]")

        # Stream container
        stream_buffer = []

        def on_stream(delta: str):
            stream_buffer.append(delta)

        with console.status("[bold green]Synthesizing game code with local AI engine...", spinner="dots"):
            try:
                game = await agent.create_game(
                    prompt=prompt,
                    category=category,
                    stream_callback=on_stream if settings.stream_output else None,
                    auto_open=not no_open,
                )
            except Exception as e:
                print_error(f"Generation failed: {e}")
                return

        print_game_card(game)
        if not no_open:
            console.print("[bold green]🚀 Game opened in your default browser![/bold green]")
        else:
            console.print(f"[dim]Game saved at: {game.file_path}[/dim]")

    asyncio.run(_run())
