"""Extracts clean HTML code from LLM responses."""

import re
from eightgen.utils.html_utils import clean_html


class HTMLExtractor:
    """Extracts executable HTML documents from raw LLM output."""

    @staticmethod
    def extract(raw_text: str) -> str:
        """Parse raw text, extracting html block or finding html document."""
        if not raw_text or not raw_text.strip():
            return ""

        # Pattern 1: Look for ```html ... ``` or ```xml ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:html|xml)?\s*\n(.*?)```", raw_text, re.DOTALL | re.IGNORECASE)
        if fence_match:
            candidate = fence_match.group(1).strip()
            if "<html" in candidate.lower() or "<!doctype" in candidate.lower() or "<canvas" in candidate.lower() or "<script" in candidate.lower():
                return clean_html(candidate)

        # Pattern 2: Look for <!DOCTYPE html> ... </html>
        doc_match = re.search(r"(<!DOCTYPE\s+html.*?>.*?</html>)", raw_text, re.DOTALL | re.IGNORECASE)
        if doc_match:
            return clean_html(doc_match.group(1).strip())

        # Pattern 3: Look for <html ... </html>
        html_match = re.search(r"(<html.*?>.*?</html>)", raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return clean_html(html_match.group(1).strip())

        # Pattern 4: Code block opened with ```html but not properly closed
        open_fence_match = re.search(r"```(?:html|xml)?\s*\n(.*)", raw_text, re.DOTALL | re.IGNORECASE)
        if open_fence_match:
            candidate = open_fence_match.group(1).strip()
            if "<html" in candidate.lower() or "<!doctype" in candidate.lower():
                if not candidate.rstrip().endswith("</html>"):
                    candidate += "\n</html>"
                return clean_html(candidate)

        # Fallback: if raw text contains html tags, return clean raw text
        if "<script" in raw_text.lower() and ("<canvas" in raw_text.lower() or "<div" in raw_text.lower()):
            return clean_html(raw_text.strip())

        return ""
