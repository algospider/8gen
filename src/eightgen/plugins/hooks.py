"""Plugin hook definitions."""

from enum import Enum


class HookName(str, Enum):
    """Available lifecycle hooks in 8Gen."""
    PRE_GENERATE = "pre_generate"
    POST_GENERATE = "post_generate"
    PRE_REFINE = "pre_refine"
    POST_REFINE = "post_refine"
    ON_VALIDATE_ERROR = "on_validate_error"
