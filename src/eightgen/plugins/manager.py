"""Plugin Manager orchestrating hook execution."""

from typing import List, Optional
from eightgen.plugins.base import Plugin
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.plugins")


class PluginManager:
    """Manages active plugins and triggers hook dispatches."""

    def __init__(self):
        self._plugins: List[Plugin] = []

    def register(self, plugin: Plugin) -> None:
        """Register a new plugin instance."""
        self._plugins.append(plugin)
        logger.debug(f"Registered plugin: {plugin.name} v{plugin.version}")

    def unregister(self, name: str) -> None:
        """Remove a plugin by name."""
        self._plugins = [p for p in self._plugins if p.name != name]

    async def trigger_pre_generate(self, prompt: str, category: Optional[str]) -> None:
        for p in self._plugins:
            try:
                await p.pre_generate(prompt, category)
            except Exception as e:
                logger.warning(f"Plugin {p.name} failed on pre_generate: {e}")

    async def trigger_post_generate(self, prompt: str, html: str) -> None:
        for p in self._plugins:
            try:
                await p.post_generate(prompt, html)
            except Exception as e:
                logger.warning(f"Plugin {p.name} failed on post_generate: {e}")

    async def trigger_pre_refine(self, game_id: str, instruction: str) -> None:
        for p in self._plugins:
            try:
                await p.pre_refine(game_id, instruction)
            except Exception as e:
                logger.warning(f"Plugin {p.name} failed on pre_refine: {e}")

    async def trigger_post_refine(self, game_id: str, html: str) -> None:
        for p in self._plugins:
            try:
                await p.post_refine(game_id, html)
            except Exception as e:
                logger.warning(f"Plugin {p.name} failed on post_refine: {e}")

    async def trigger_on_validate_error(self, html: str, errors: List[str]) -> None:
        for p in self._plugins:
            try:
                await p.on_validate_error(html, errors)
            except Exception as e:
                logger.warning(f"Plugin {p.name} failed on on_validate_error: {e}")


_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Get singleton plugin manager."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
