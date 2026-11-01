"""Game refinement and iteration pipeline."""

from typing import Callable, Optional
from eightgen.config.settings import Settings
from eightgen.core.extractor import HTMLExtractor
from eightgen.core.validator import GameValidator, ValidationResult
from eightgen.llm.base import LLMProvider
from eightgen.llm.prompt_builder import PromptBuilder
from eightgen.plugins.manager import get_plugin_manager
from eightgen.utils.logger import get_logger

import inspect

logger = get_logger("eightgen.refiner")


class RefinementError(Exception):
    """Raised when game refinement fails all retries."""
    pass


class GameRefiner:
    """Modifies and iterates on existing games using instructions."""

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

    async def refine(
        self,
        game_id: str,
        existing_html: str,
        instruction: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Apply user modifications to existing game code."""
        await self.plugins.trigger_pre_refine(game_id, instruction)

        messages = self.prompt_builder.build_refine_messages(existing_html, instruction)
        max_attempts = max(1, self.settings.max_retries)
        last_errors = []
        raw_output = ""

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Refinement attempt {attempt}/{max_attempts}...")

            if attempt > 1:
                messages = self.prompt_builder.build_fix_messages(raw_output, last_errors)

            raw_chunks = []
            if stream_callback:
                async for chunk in self.provider.stream(messages, temperature=self.settings.temperature):
                    raw_chunks.append(chunk)
                    if inspect.iscoroutinefunction(stream_callback):
                        await stream_callback(chunk)
                    else:
                        stream_callback(chunk)
                raw_output = "".join(raw_chunks)
            else:
                response = await self.provider.generate(messages, temperature=self.settings.temperature)
                raw_output = response.content

            html_code = HTMLExtractor.extract(raw_output)
            if not html_code:
                last_errors = ["Failed to extract valid HTML code block from LLM response."]
                await self.plugins.trigger_on_validate_error(raw_output, last_errors)
                continue

            val_result: ValidationResult = GameValidator.validate(html_code)
            if val_result.is_valid:
                logger.info("Refinement validation passed successfully!")
                await self.plugins.trigger_post_refine(game_id, html_code)
                return html_code

            logger.warning(f"Refinement validation failed (attempt {attempt}): {val_result.errors}")
            last_errors = val_result.errors
            await self.plugins.trigger_on_validate_error(html_code, last_errors)

        if html_code and "<html" in html_code.lower():
            logger.warning("Max retries reached; returning best effort refined HTML.")
            return html_code

        raise RefinementError(f"Failed to refine game after {max_attempts} attempts: {last_errors}")
