"""Configuration settings for 8Gen."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment, config files, or defaults."""

    model_config = SettingsConfigDict(
        env_prefix="EIGHTGEN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # LLM Settings
    provider: str = Field(default="ollama", description="LLM provider: ollama")
    ollama_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    model: str = Field(
        default="huihui_ai/qwen2.5-coder-abliterate:7b",
        description="Ollama model name. If not set or not found, 8Gen will auto-detect available model"
    )
    temperature: float = Field(default=0.7, description="Generation temperature (0.0 to 1.0)")
    timeout: float = Field(default=180.0, description="LLM HTTP timeout in seconds")
    max_retries: int = Field(default=3, description="Self-healing validation retry limit")

    # Storage Settings
    output_dir: Path = Field(default=Path("./games"), description="Directory to save generated games")
    db_path: Path = Field(default=Path("./games/8gen.db"), description="Path to SQLite metadata database")

    # Server Settings
    server_host: str = Field(default="127.0.0.1", description="Web dashboard host")
    server_port: int = Field(default=8000, description="Web dashboard port")
    auto_open: bool = Field(default=True, description="Automatically open generated games in browser")

    # CLI & UI
    stream_output: bool = Field(default=True, description="Stream LLM generation directly to terminal")
    theme: str = Field(default="dark", description="Dashboard UI theme")

    def ensure_directories(self) -> None:
        """Ensure necessary storage directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
