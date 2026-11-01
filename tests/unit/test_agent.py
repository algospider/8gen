"""Unit tests for top-level Agent."""

import pytest
from pathlib import Path
from eightgen.config.settings import Settings
from eightgen.core.agent import Agent
from tests.conftest import MockLLMProvider


@pytest.mark.asyncio
async def test_agent_create_game(tmp_settings: Settings):
    agent = Agent(tmp_settings)
    agent.set_provider(MockLLMProvider())

    game = await agent.create_game(
        prompt="Pixel Snake",
        category="arcade",
        auto_open=False,
    )

    assert game is not None
    assert game.title == "Asteroid Blast"
    assert game.current_version == 1
    assert game.file_path.exists()
    assert len(game.versions) == 1


@pytest.mark.asyncio
async def test_agent_refine_game(tmp_settings: Settings):
    agent = Agent(tmp_settings)
    agent.set_provider(MockLLMProvider())

    game = await agent.create_game("Base Game", auto_open=False)
    updated = await agent.refine_game(
        game_id=game.id,
        instruction="add powerups",
        auto_open=False,
    )

    assert updated.current_version == 2
    assert len(updated.versions) == 2
    assert updated.versions[1].change_summary == "add powerups"


@pytest.mark.asyncio
async def test_agent_export_game(tmp_settings: Settings, tmp_path: Path):
    agent = Agent(tmp_settings)
    agent.set_provider(MockLLMProvider())

    game = await agent.create_game("Export test", auto_open=False)

    export_dest = tmp_path / "exported.html"
    exported_path = agent.export_game(game.id, export_dest)
    assert exported_path.exists()
    assert exported_path.read_text() == game.latest_html
