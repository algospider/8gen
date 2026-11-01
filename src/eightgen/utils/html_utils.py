"""HTML validation and inspection utilities."""

import re


def clean_html(html_code: str) -> str:
    """Strip unnecessary trailing/leading whitespace and clean common LLM artifacts."""
    code = html_code.strip()
    # Ensure DOCTYPE if missing
    if not re.search(r"<!DOCTYPE\s+html>", code, re.IGNORECASE):
        code = "<!DOCTYPE html>\n" + code
    return code


def estimate_loc(code: str) -> int:
    """Return non-empty line count."""
    return len([line for line in code.splitlines() if line.strip()])


def extract_game_title(html_code: str, fallback: str = "Untitled Game") -> str:
    """Extract <title> from HTML or return fallback."""
    match = re.search(r"<title>(.*?)</title>", html_code, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        if title:
            return title
    # Try looking for h1
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_code, re.IGNORECASE | re.DOTALL)
    if h1_match:
        h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
        if h1:
            return h1
    return fallback
