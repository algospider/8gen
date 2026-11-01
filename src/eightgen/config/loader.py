"""Configuration loader and manager."""

from pathlib import Path
import tomllib
from typing import Any, Dict
from eightgen.config.settings import Settings

DEFAULT_CONFIG_LOCATIONS = [
    Path("./8gen.toml"),
    Path.home() / ".config" / "eightgen" / "config.toml",
]


def load_toml_config(path: Path) -> Dict[str, Any]:
    """Parse TOML configuration file flattening sections."""
    if not path.is_file():
        return {}
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        flattened: Dict[str, Any] = {}
        for key, val in data.items():
            if isinstance(val, dict):
                for sub_key, sub_val in val.items():
                    if sub_key == "provider":
                        flattened["provider"] = sub_val
                    elif sub_key == "ollama_url":
                        flattened["ollama_url"] = sub_val
                    elif sub_key == "model":
                        flattened["model"] = sub_val
                    elif sub_key == "temperature":
                        flattened["temperature"] = sub_val
                    elif sub_key == "timeout":
                        flattened["timeout"] = sub_val
                    elif sub_key == "max_retries":
                        flattened["max_retries"] = sub_val
                    elif sub_key == "output_dir":
                        flattened["output_dir"] = Path(sub_val)
                    elif sub_key == "db_path":
                        flattened["db_path"] = Path(sub_val)
                    elif sub_key == "host":
                        flattened["server_host"] = sub_val
                    elif sub_key == "port":
                        flattened["server_port"] = sub_val
                    elif sub_key == "auto_open":
                        flattened["auto_open"] = sub_val
                    elif sub_key == "stream_output":
                        flattened["stream_output"] = sub_val
                    elif sub_key == "theme":
                        flattened["theme"] = sub_val
                    else:
                        flattened[sub_key] = sub_val
            else:
                flattened[key] = val
        return flattened
    except Exception:
        return {}


def get_settings(config_path: Path | None = None, **overrides: Any) -> Settings:
    """Load settings with priority: overrides > config file > environment variables > defaults."""
    file_data: Dict[str, Any] = {}
    if config_path and Path(config_path).is_file():
        file_data = load_toml_config(Path(config_path))
    else:
        for loc in DEFAULT_CONFIG_LOCATIONS:
            if loc.is_file():
                file_data = load_toml_config(loc)
                break

    # Strip None overrides
    clean_overrides = {k: v for k, v in overrides.items() if v is not None}
    merged_data = {**file_data, **clean_overrides}

    settings = Settings(**merged_data)
    settings.ensure_directories()
    return settings
