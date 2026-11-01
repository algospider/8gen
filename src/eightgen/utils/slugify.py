"""Slug generation for game names and file paths."""

import re
import unicodedata


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text into a URL- and filesystem-friendly slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-_")
    if not text:
        return "game"
    return text[:max_length].rstrip("-")
