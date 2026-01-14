from .windowing import (
    WindowInfo,
    find_window_by_title_regex,
    get_client_rect_in_screen,
    is_foreground,
)

__all__ = [
    "__version__",
    "WindowInfo",
    "find_window_by_title_regex",
    "get_client_rect_in_screen", 
    "is_foreground",
]

__version__ = "0.1.0"