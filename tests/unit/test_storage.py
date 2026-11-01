"""Unit tests for Storage and Repository."""

from pathlib import Path
from eightgen.storage.models import Game, GameVersion
from eightgen.storage.repository import GameRepository


def test_repository_save_and_get(repo: GameRepository, tmp_path: Path):
    file_path = tmp_path / "test_game.html"
    version = GameVersion(
        version=1,
        prompt="A cute platformer",
        html_content="<!DOCTYPE html><html><body>Test</body></html>",
        model="test-model",
    )
    game = Game(
        id="test1234",
        title="Test Platformer",
        slug="test-platformer",
        description="A cute platformer",
        category="platformer",
        tags=["cute", "platformer"],
        current_version=1,
        file_path=file_path,
        versions=[version],
    )

    saved = repo.save(game)
    assert saved.id == "test1234"
    assert file_path.exists()
    assert file_path.read_text() == version.html_content

    # Retrieve by ID
    retrieved = repo.get_by_id("test1234")
    assert retrieved is not None
    assert retrieved.title == "Test Platformer"
    assert len(retrieved.versions) == 1
    assert retrieved.versions[0].prompt == "A cute platformer"


def test_repository_add_version(repo: GameRepository, tmp_path: Path):
    file_path = tmp_path / "game_v.html"
    v1 = GameVersion(
        version=1,
        prompt="Initial",
        html_content="<html>v1</html>",
        model="m1",
    )
    game = Game(
        id="gver1",
        title="Versioned Game",
        slug="versioned-game",
        file_path=file_path,
        versions=[v1],
    )
    repo.save(game)

    v2 = GameVersion(
        version=2,
        prompt="Add sound",
        html_content="<html>v2 with sound</html>",
        model="m1",
    )
    updated = repo.add_version("gver1", v2)
    assert updated.current_version == 2
    assert len(updated.versions) == 2
    assert file_path.read_text() == "<html>v2 with sound</html>"


def test_repository_delete(repo: GameRepository, tmp_path: Path):
    file_path = tmp_path / "to_delete.html"
    game = Game(
        id="del1",
        title="Delete Me",
        slug="delete-me",
        file_path=file_path,
        versions=[GameVersion(version=1, prompt="p", html_content="<html></html>", model="m")],
    )
    repo.save(game)
    assert repo.get_by_id("del1") is not None

    deleted = repo.delete("del1")
    assert deleted is True
    assert repo.get_by_id("del1") is None
