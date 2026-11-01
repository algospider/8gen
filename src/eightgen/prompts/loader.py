"""Jinja2 prompt template loader and renderer."""

from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

PROMPTS_DIR = Path(__file__).parent


class PromptTemplateLoader:
    """Manages loading and rendering Jinja2 prompt templates."""

    def __init__(self, templates_dir: Path = PROMPTS_DIR):
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(default=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with provided context dictionary."""
        template = self.env.get_template(template_name)
        return template.render(**context)


_loader: PromptTemplateLoader | None = None


def get_prompt_loader() -> PromptTemplateLoader:
    """Get or create singleton prompt loader."""
    global _loader
    if _loader is None:
        _loader = PromptTemplateLoader()
    return _loader
