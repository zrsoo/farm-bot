from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from .templates import LoadedTemplate


@dataclass(frozen=True)
class MatchResult:
    template_name: str
    score: float
    top_left: tuple[int, int]      # in frame coords
    size: tuple[int, int]          # (w, h) in frame coords
    center: tuple[int, int]        # in frame coords

def _method_from_name(name: str) -> int:
    if not hasattr(cv2, name):
        raise ValueError(f"Unknown OpenCV matchTemplate method: {name}")
    return getattr(cv2, name)

def _score_from_minmax(method: int, min_val: float, max_val: float) -> float:
    # For SQDIFF, lower is better. Convert to "higher is better" in [~0..1] if possible.
    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        return 1.0 - float(min_val)
    return float(max_val)

def _loc_from_minmax(method: int, min_loc, max_loc):
    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        return min_loc
    return max_loc

class TemplateMatcher:
    def __init__(self, templates: list[LoadedTemplate], method_name: str, scales: list[float]):
        self.templates = templates
        self.method_name = method_name
        self.method = _method_from_name(method_name)
        self.scales = scales[:] if scales else [1.0]

        # OpenCV sometimes spawns threads and causes jitter. Optional but often good.
        try:
            cv2.setNumThreads(0)
        except Exception:
            pass

    def match_best(self, frame_gray: np.ndarray, frame_edges: np.ndarray, mode: str) -> Optional[MatchResult]:
        best: Optional[MatchResult] = None

        for t in self.templates:
            base = t.edges if mode == "edges" else t.gray

            for s in self.scales:
                if s <= 0:
                    continue

                templ = base
                if abs(s - 1.0) > 1e-6:
                    w = max(8, int(base.shape[1] * s))
                    h = max(8, int(base.shape[0] * s))
                    templ = cv2.resize(base, (w, h), interpolation=cv2.INTER_AREA)

                src = frame_edges if mode == "edges" else frame_gray
                th, tw = templ.shape[:2]
                sh, sw = src.shape[:2]
                if th >= sh or tw >= sw:
                    continue

                res = cv2.matchTemplate(src, templ, self.method)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                score = _score_from_minmax(self.method, min_val, max_val)
                loc = _loc_from_minmax(self.method, min_loc, max_loc)

                x, y = int(loc[0]), int(loc[1])
                cx = x + tw // 2
                cy = y + th // 2

                mr = MatchResult(
                    template_name=t.name,
                    score=score,
                    top_left=(x, y),
                    size=(tw, th),
                    center=(cx, cy),
                )

                if best is None or mr.score > best.score:
                    best = mr

        return best
