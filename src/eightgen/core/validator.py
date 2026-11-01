"""Validates generated HTML5 games for required structures and playability."""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    """Outcome of HTML5 game validation check."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class GameValidator:
    """Validates game HTML structure and interactivity essentials."""

    @staticmethod
    def validate(html_code: str) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not html_code or not html_code.strip():
            return ValidationResult(is_valid=False, errors=["Empty or missing HTML code."])

        code_lower = html_code.lower()

        # Check HTML basic structure
        if "<html" not in code_lower and "<!doctype html" not in code_lower:
            errors.append("Missing <!DOCTYPE html> or <html> tag.")

        if "</html>" not in code_lower:
            errors.append("Unclosed <html> tag or truncated document.")

        # Check script tags
        script_matches = re.findall(r"<script[^>]*>(.*?)</script>", html_code, re.DOTALL | re.IGNORECASE)
        if not script_matches:
            errors.append("Missing <script> tag with game logic.")
        else:
            total_script_len = sum(len(s.strip()) for s in script_matches)
            if total_script_len < 50:
                errors.append("Script tag appears empty or too short to contain game logic.")

        # Check visual container (Canvas or DOM container)
        has_canvas = "<canvas" in code_lower
        has_container = "id=" in code_lower or "class=" in code_lower
        if not has_canvas and not has_container:
            errors.append("Missing visual container (no <canvas> or interactive DOM element found).")

        # Check interactivity (loop or event listeners)
        has_raf = "requestanimationframe" in code_lower
        has_interval = "setinterval" in code_lower
        has_events = (
            "addeventlistener" in code_lower
            or "onkeydown" in code_lower
            or "onclick" in code_lower
            or "onkeyup" in code_lower
            or "ontouchstart" in code_lower
        )

        if not (has_raf or has_interval or has_events):
            errors.append("Game does not appear to have an update loop or user input event listeners.")

        # Warning checks
        if "audio" not in code_lower and "audiocontext" not in code_lower:
            warnings.append("No Web Audio API detected for sound effects.")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
