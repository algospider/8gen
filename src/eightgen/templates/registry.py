"""Template registry for starter skeletons."""

from pathlib import Path
from typing import Dict, List, Optional

TEMPLATES_DIR = Path(__file__).parent


class TemplateRegistry:
    """Manages built-in game skeletons."""

    def __init__(self, directory: Path = TEMPLATES_DIR):
        self.directory = directory
        self._templates: Dict[str, str] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        for f in self.directory.glob("*.html"):
            name = f.stem
            self._templates[name] = f.read_text(encoding="utf-8")

    def get(self, name: str) -> Optional[str]:
        """Fetch template content by name."""
        return self._templates.get(name)

    def list_templates(self) -> List[str]:
        """List available template names."""
        return list(self._templates.keys())


_registry: TemplateRegistry | None = None


def get_template_registry() -> TemplateRegistry:
    """Get singleton template registry."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry
