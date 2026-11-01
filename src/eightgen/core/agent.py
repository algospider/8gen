"""Top-level Agent orchestrator for 8Gen."""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from eightgen.config.settings import Settings
from eightgen.config.loader import get_settings
from eightgen.core.generator import GameGenerator
from eightgen.core.refiner import GameRefiner
from eightgen.llm.factory import create_llm_provider
from eightgen.llm.prompt_builder import PromptBuilder
from eightgen.storage.database import Database
from eightgen.storage.models import Game, GameVersion
from eightgen.storage.repository import GameRepository
from eightgen.utils.browser import open_in_browser
from eightgen.utils.html_utils import extract_game_title
from eightgen.utils.logger import get_logger
from eightgen.utils.slugify import slugify

logger = get_logger("eightgen.agent")


class Agent:
    """Autonomous AI Agent that coordinates generation, refinement, storage, and previewing."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.db = Database(self.settings.db_path)
        self.repo = GameRepository(self.db, self.settings.output_dir)

        # Initialize LLM & Prompts
        self.provider = create_llm_provider(self.settings)
        self.prompt_builder = PromptBuilder()

        # Core Pipelines
        self.generator = GameGenerator(self.provider, self.prompt_builder, self.settings)
        self.refiner = GameRefiner(self.provider, self.prompt_builder, self.settings)

    def set_provider(self, provider: Any) -> None:
        """Update provider across agent pipelines."""
        self.provider = provider
        self.generator.provider = provider
        self.refiner.provider = provider


    async def check_health(self) -> Dict[str, Any]:
        """Check LLM provider connectivity and available models."""
        is_up = await self.provider.is_healthy()
        models = await self.provider.list_models() if is_up else []
        return {
            "provider": self.settings.provider,
            "connected": is_up,
            "ollama_connected": is_up,
            "configured_model": getattr(self.provider, "model", self.settings.model),
            "available_models": models,
            "storage_path": str(self.settings.output_dir.resolve()),
        }

    async def create_game(
        self,
        prompt: str,
        category: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        auto_open: Optional[bool] = None,
    ) -> Game:
        """Generate a brand new game from user prompt."""
        logger.info(f"Generating game for prompt: '{prompt}'...")

        # Run generation pipeline
        html_content = await self.generator.generate(
            prompt=prompt,
            category=category,
            stream_callback=stream_callback,
        )

        # Infer title and slug
        extracted_title = extract_game_title(html_content, fallback=prompt[:30].strip())
        slug = slugify(extracted_title)
        short_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{slug}.html"
        file_path = self.settings.output_dir / filename

        # Create version & game record
        active_model = getattr(self.provider, "model", self.settings.model)
        version = GameVersion(
            version=1,
            prompt=prompt,
            html_content=html_content,
            model=active_model,
            change_summary="Initial generation",
        )

        game = Game(
            id=short_id,
            title=extracted_title,
            slug=slug,
            description=prompt,
            category=category or "arcade",
            tags=[t.strip() for t in (category or "arcade,instant").split(",") if t.strip()],
            current_version=1,
            file_path=file_path,
            versions=[version],
        )

        saved_game = self.repo.save(game)
        logger.info(f"Game saved successfully: {saved_game.file_path}")

        # Auto-launch browser if requested
        should_open = self.settings.auto_open if auto_open is None else auto_open
        if should_open:
            open_in_browser(saved_game.file_path)

        return saved_game

    async def refine_game(
        self,
        game_id: str,
        instruction: str,
        stream_callback: Optional[Callable[[str], None]] = None,
        auto_open: Optional[bool] = None,
    ) -> Game:
        """Iterate or update an existing game."""
        # Handle 'last' or prefix
        if game_id.lower() == "last":
            game = self.repo.get_latest()
            if not game:
                raise ValueError("No existing games found to refine.")
        else:
            game = self.repo.get_by_id(game_id)
            if not game:
                raise ValueError(f"Game with ID '{game_id}' not found.")

        logger.info(f"Refining game '{game.title}' (v{game.current_version}) with: '{instruction}'...")

        existing_html = game.latest_html
        refined_html = await self.refiner.refine(
            game_id=game.id,
            existing_html=existing_html,
            instruction=instruction,
            stream_callback=stream_callback,
        )

        active_model = getattr(self.provider, "model", self.settings.model)
        new_version = GameVersion(
            version=game.current_version + 1,
            prompt=instruction,
            html_content=refined_html,
            model=active_model,
            change_summary=instruction,
        )

        updated_game = self.repo.add_version(game.id, new_version)
        if not updated_game:
            raise RuntimeError("Failed to persist updated game version.")

        logger.info(f"Game '{updated_game.title}' updated to v{updated_game.current_version}!")

        should_open = self.settings.auto_open if auto_open is None else auto_open
        if should_open:
            open_in_browser(updated_game.file_path)

        return updated_game

    def get_game(self, game_id: str) -> Optional[Game]:
        """Fetch game by ID (supports 'last')."""
        if game_id.lower() == "last":
            return self.repo.get_latest()
        return self.repo.get_by_id(game_id)

    def list_games(self, limit: int = 50, tag: Optional[str] = None) -> List[Game]:
        """List all generated games."""
        return self.repo.list_all(limit=limit, tag=tag)

    def delete_game(self, game_id: str) -> bool:
        """Delete game by ID."""
        return self.repo.delete(game_id)

    def export_game(self, game_id: str, output_path: Path) -> Path:
        """Export game HTML file to a target destination."""
        game = self.get_game(game_id)
        if not game:
            raise ValueError(f"Game '{game_id}' not found.")
        dest = Path(output_path).resolve()
        if dest.is_dir():
            dest = dest / game.file_path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(game.latest_html, encoding="utf-8")
        return dest
