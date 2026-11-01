"""Game generation pipeline with self-healing validation loop."""

from typing import Callable, Optional
from eightgen.config.settings import Settings
from eightgen.core.extractor import HTMLExtractor
from eightgen.core.validator import GameValidator, ValidationResult
from eightgen.llm.base import LLMProvider
from eightgen.llm.prompt_builder import PromptBuilder
from eightgen.plugins.manager import get_plugin_manager
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.generator")


class GenerationError(Exception):
    """Raised when game generation fails all retries."""
    pass


class GameGenerator:
    """Manages LLM interaction, extraction, validation, and self-healing."""

    def __init__(
        self,
        provider: LLMProvider,
        prompt_builder: PromptBuilder,
        settings: Settings,
    ):
        self.provider = provider
        self.prompt_builder = prompt_builder
        self.settings = settings
        self.plugins = get_plugin_manager()

    async def generate(
        self,
        prompt: str,
        category: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate a complete, validated HTML5 game from a prompt."""
        await self.plugins.trigger_pre_generate(prompt, category)

        messages = self.prompt_builder.build_generate_messages(prompt, category)
        max_attempts = max(1, self.settings.max_retries)
        last_errors = []
        raw_output = ""

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Generation attempt {attempt}/{max_attempts}...")

            if attempt > 1:
                # Self-healing debug attempt
                messages = self.prompt_builder.build_fix_messages(raw_output, last_errors)

            raw_chunks = []
            if stream_callback:
                async for chunk in self.provider.stream(messages, temperature=self.settings.temperature):
                    raw_chunks.append(chunk)
                    stream_callback(chunk)
                raw_output = "".join(raw_chunks)
            else:
                response = await self.provider.generate(messages, temperature=self.settings.temperature)
                raw_output = response.content

            # Extract clean HTML
            html_code = HTMLExtractor.extract(raw_output)
            if not html_code:
                last_errors = ["Failed to extract valid HTML code block from LLM response."]
                await self.plugins.trigger_on_validate_error(raw_output, last_errors)
                continue

            # Validate HTML structure and requirements
            val_result: ValidationResult = GameValidator.validate(html_code)
            if val_result.is_valid:
                logger.info("Validation passed successfully!")
                await self.plugins.trigger_post_generate(prompt, html_code)
                return html_code

            logger.warning(f"Validation failed (attempt {attempt}): {val_result.errors}")
            last_errors = val_result.errors
            await self.plugins.trigger_on_validate_error(html_code, last_errors)

        # If retries exhausted but we have some extracted HTML, log warning and return best effort
        if html_code and "<html" in html_code.lower():
            logger.warning("Max retries reached; returning best effort HTML.")
            return html_code

        raise GenerationError(f"Failed to generate valid game after {max_attempts} attempts: {last_errors}")
