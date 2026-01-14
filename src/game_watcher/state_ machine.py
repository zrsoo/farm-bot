from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern

import win32gui


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    client_left: int
    client_top: int
    client_width: int
    client_height: int

    @property
    def client_right(self) -> int:
        return self.client_left + self.client_width

    @property
    def client_bottom(self) -> int:
        return self.client_top + self.client_height


def _is_good_window(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False
    if win32gui.IsIconic(hwnd):  # minimized
        return False
    # Exclude tool windows / weird chrome if needed later.
    return True


def find_window_by_title_regex(title_regex: str) -> list[int]:
    pattern: Pattern[str] = re.compile(title_regex)

    matches: list[int] = []

    def enum_cb(hwnd: int, _):
        if not _is_good_window(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if title and pattern.search(title):
            matches.append(hwnd)

    win32gui.EnumWindows(enum_cb, None)
    return matches


def get_client_rect_in_screen(hwnd: int) -> WindowInfo:
    title = win32gui.GetWindowText(hwnd) or ""

    # Client rect is relative to client origin (0,0)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    # Convert client (0,0) to screen coords
    client_origin_screen = win32gui.ClientToScreen(hwnd, (0, 0))
    client_left, client_top = client_origin_screen

    return WindowInfo(
        hwnd=hwnd,
        title=title,
        client_left=client_left,
        client_top=client_top,
        client_width=width,
        client_height=height,
    )


def is_foreground(hwnd: int) -> bool:
    return win32gui.GetForegroundWindow() == hwnd
