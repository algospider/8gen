"""Storage models for games and version history."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class GameVersion(BaseModel):
    """Represents a single snapshot / iteration of a generated game."""
    version: int = Field(default=1, description="Sequential version number")
    prompt: str = Field(description="Prompt that generated this version")
    html_content: str = Field(description="Complete HTML/JS code of the game")
    model: str = Field(description="LLM model used")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_summary: Optional[str] = Field(default=None, description="Summary of changes in this version")


class Game(BaseModel):
    """Represents a game project with metadata and version history."""
    id: str = Field(description="Unique game identifier (e.g. short uuid or slug)")
    title: str = Field(description="Human readable game title")
    slug: str = Field(description="Filesystem-friendly slug")
    description: str = Field(default="", description="Game overview or description")
    category: str = Field(default="arcade", description="Category: arcade, puzzle, platformer, action, etc.")
    tags: List[str] = Field(default_factory=list, description="Game tags")
    current_version: int = Field(default=1, description="Latest version number")
    file_path: Path = Field(description="Path to current HTML file on disk")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    versions: List[GameVersion] = Field(default_factory=list, description="History of versions")

    @property
    def latest_html(self) -> str:
        """Get the HTML content of the latest version."""
        if self.versions:
            return self.versions[-1].html_content
        return ""
