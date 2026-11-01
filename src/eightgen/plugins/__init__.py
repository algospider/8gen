"""Plugins framework for 8Gen."""

from eightgen.plugins.base import Plugin
from eightgen.plugins.hooks import HookName
from eightgen.plugins.manager import PluginManager, get_plugin_manager

__all__ = ["Plugin", "HookName", "PluginManager", "get_plugin_manager"]
