"""Repository pattern for Game persistence in SQLite and filesystem."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from eightgen.storage.database import Database
from eightgen.storage.models import Game, GameVersion
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.storage")


class GameRepository:
    """Handles saving, retrieving, and updating games in SQLite & filesystem."""

    def __init__(self, db: Database, output_dir: Path):
        self.db = db
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, game: Game) -> Game:
        """Insert or update a game and its versions."""
        with self.db.get_connection() as conn:
            tags_json = json.dumps(game.tags)
            conn.execute(
                """
                INSERT INTO games (id, title, slug, description, category, tags, current_version, file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    slug = excluded.slug,
                    description = excluded.description,
                    category = excluded.category,
                    tags = excluded.tags,
                    current_version = excluded.current_version,
                    file_path = excluded.file_path,
                    updated_at = excluded.updated_at
                """,
                (
                    game.id,
                    game.title,
                    game.slug,
                    game.description,
                    game.category,
                    tags_json,
                    game.current_version,
                    str(game.file_path),
                    game.created_at.isoformat(),
                    game.updated_at.isoformat(),
                ),
            )

            # Save versions
            for ver in game.versions:
                conn.execute(
                    """
                    INSERT INTO game_versions (game_id, version, prompt, html_content, model, change_summary, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(game_id, version) DO UPDATE SET
                        prompt = excluded.prompt,
                        html_content = excluded.html_content,
                        model = excluded.model,
                        change_summary = excluded.change_summary
                    """,
                    (
                        game.id,
                        ver.version,
                        ver.prompt,
                        ver.html_content,
                        ver.model,
                        ver.change_summary,
                        ver.created_at.isoformat(),
                    ),
                )
            conn.commit()

        # Write latest HTML to file
        if game.versions:
            game.file_path.parent.mkdir(parents=True, exist_ok=True)
            game.file_path.write_text(game.latest_html, encoding="utf-8")

        return game

    def get_by_id(self, game_id: str) -> Optional[Game]:
        """Fetch game by ID or prefix match."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM games WHERE id = ? OR id LIKE ? ORDER BY updated_at DESC LIMIT 1",
                (game_id, f"{game_id}%")
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_game(conn, row)

    def get_by_slug(self, slug: str) -> Optional[Game]:
        """Fetch game by slug."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM games WHERE slug = ? LIMIT 1", (slug,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_game(conn, row)

    def get_latest(self) -> Optional[Game]:
        """Fetch the most recently updated game."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM games ORDER BY updated_at DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_game(conn, row)

    def list_all(self, limit: int = 50, tag: Optional[str] = None) -> List[Game]:
        """List games ordered by most recent update."""
        games: List[Game] = []
        with self.db.get_connection() as conn:
            if tag:
                cursor = conn.execute(
                    "SELECT * FROM games WHERE tags LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"%{tag}%", limit),
                )
            else:
                cursor = conn.execute("SELECT * FROM games ORDER BY updated_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            for row in rows:
                games.append(self._build_game(conn, row))
        return games

    def delete(self, game_id: str) -> bool:
        """Delete game from database and remove HTML file."""
        game = self.get_by_id(game_id)
        if not game:
            return False
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM games WHERE id = ?", (game.id,))
            conn.commit()
        if game.file_path.exists():
            try:
                game.file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove file {game.file_path}: {e}")
        return True

    def add_version(self, game_id: str, version: GameVersion) -> Optional[Game]:
        """Append a new version to an existing game."""
        game = self.get_by_id(game_id)
        if not game:
            return None
        version.version = game.current_version + 1
        game.current_version = version.version
        game.updated_at = datetime.now(timezone.utc)
        game.versions.append(version)
        return self.save(game)

    def _build_game(self, conn, row) -> Game:
        """Helper to construct Game model with versions."""
        v_cursor = conn.execute(
            "SELECT * FROM game_versions WHERE game_id = ? ORDER BY version ASC",
            (row["id"],),
        )
        version_rows = v_cursor.fetchall()
        versions = [
            GameVersion(
                version=v["version"],
                prompt=v["prompt"],
                html_content=v["html_content"],
                model=v["model"],
                change_summary=v["change_summary"],
                created_at=datetime.fromisoformat(v["created_at"]),
            )
            for v in version_rows
        ]

        tags = []
        if row["tags"]:
            try:
                tags = json.loads(row["tags"])
            except Exception:
                tags = [t.strip() for t in row["tags"].split(",") if t.strip()]

        return Game(
            id=row["id"],
            title=row["title"],
            slug=row["slug"],
            description=row["description"] or "",
            category=row["category"] or "arcade",
            tags=tags,
            current_version=row["current_version"],
            file_path=Path(row["file_path"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            versions=versions,
        )
