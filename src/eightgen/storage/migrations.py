"""Database migrations runner for future schema upgrades."""

from eightgen.storage.database import Database


def run_migrations(db: Database) -> None:
    """Ensure database schema is up-to-date."""
    db.init_db()
