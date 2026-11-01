"""Utility modules for 8Gen."""

from eightgen.utils.logger import get_logger
from eightgen.utils.slugify import slugify
from eightgen.utils.browser import open_in_browser
from eightgen.utils.html_utils import clean_html, estimate_loc

__all__ = ["get_logger", "slugify", "open_in_browser", "clean_html", "estimate_loc"]
