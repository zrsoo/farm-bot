from .win32_window import (
    WindowInfo,
    find_window_by_title_regex,
    get_client_rect_in_screen,
    is_foreground,
)

__all__ = [
    "WindowInfo",
    "find_window_by_title_regex", 
    "get_client_rect_in_screen",
    "is_foreground",
]