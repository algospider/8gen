"""CLI config and diagnostic command."""

import asyncio
import click
from rich.panel import Panel
from rich.table import Table
from eightgen.cli.display import console, print_banner, print_status, print_error, print_success
from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent


@click.group(name="config")
def config_cmd() -> None:
    """View and verify 8Gen configuration and Ollama connectivity."""
    pass


@config_cmd.command(name="show")
def show_config() -> None:
    """Display current active configuration."""
    print_banner()
    settings = get_settings()

    table = Table(title="🔧 Active Settings", border_style="cyan")
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Provider", settings.provider)
    table.add_row("Ollama URL", settings.ollama_url)
    table.add_row("Configured Model", settings.model)
    table.add_row("Temperature", str(settings.temperature))
    table.add_row("Max Retries", str(settings.max_retries))
    table.add_row("Output Directory", str(settings.output_dir.resolve()))
    table.add_row("Database Path", str(settings.db_path.resolve()))
    table.add_row("Web Server", f"http://{settings.server_host}:{settings.server_port}")
    table.add_row("Auto Open", str(settings.auto_open))

    console.print(table)


@config_cmd.command(name="check")
def check_config() -> None:
    """Diagnose local Ollama connection and installed models."""
    print_banner()
    settings = get_settings()
    agent = Agent(settings)

    async def _check():
        print_status("Checking Ollama health...")
        health = await agent.check_health()
        if health["ollama_connected"]:
            print_success(f"Ollama server is active at {health['ollama_url']}")
            models = health.get("available_models", [])
            if models:
                console.print(f"[bold green]✔ Models found ({len(models)}):[/bold green]")
                for m in models:
                    marker = "★ (active)" if m == health["configured_model"] or health["configured_model"] in m else "•"
                    console.print(f"  {marker} [cyan]{m}[/cyan]")
            else:
                console.print("[dim yellow]No models downloaded in Ollama yet. Run: ollama pull llama3.1[/dim yellow]")
        else:
            print_error(f"Cannot reach Ollama at {health['ollama_url']}")
            console.print("[dim]Make sure Ollama is installed and running (`ollama serve` or open the Ollama app).[/dim]")

    asyncio.run(_check())
