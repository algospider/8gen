"""Cross-platform browser launcher."""

import webbrowser
from pathlib import Path
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.browser")


def open_in_browser(file_or_url: str | Path) -> bool:
    """Open a file or URL in the system's default browser."""
    try:
        if isinstance(file_or_url, Path) or (isinstance(file_or_url, str) and not file_or_url.startswith(("http://", "https://"))):
            path = Path(file_or_url).resolve()
            url = path.as_uri()
        else:
            url = str(file_or_url)
        return webbrowser.open(url)
    except Exception as e:
        logger.warning(f"Could not open browser automatically: {e}")
        return False
